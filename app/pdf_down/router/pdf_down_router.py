# app/pdf_down/router/pdf_down_router.py

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import text
from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright

# 세션 주입
from config.database.session import get_db_session

# 도메인/엔티티
from product.domain.entity.product import Platform
from product.infrastructure.orm.product_orm import ProductORM
# ※ 아래 ORM들은 사용 안 하지만, 프로젝트 구조 유지 차원에서 import 가능
# from product_analysis.infrastructure.orm.analysis_result_orm import AnalysisResultORM
# from product_analysis.infrastructure.orm.insight_result_orm import InsightResultORM

router = APIRouter(prefix="/report", tags=["report"])

# 템플릿 디렉토리 (프로젝트 구조에 맞춰 조정)
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)


# ------------------------- 유틸 -------------------------
def _html_to_pdf_bytes(html_str: str) -> bytes:
    # Playwright (Chromium) 기반 PDF 생성
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_str, wait_until="networkidle")
        pdf = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "16mm", "right": "16mm", "bottom": "16mm", "left": "16mm"},
        )
        browser.close()
        return pdf


def _format_percent(n: int, total: int) -> int:
    if not total or total <= 0:
        return 0
    return round(n * 100 / total)


def _json_or(v, default):
    # 문자열/bytes면 json.loads, 이미 파이썬 객체면 그대로, None이면 default
    if v is None:
        return default
    if isinstance(v, (str, bytes, bytearray)):
        try:
            return json.loads(v)
        except Exception:
            return default
    return v


def _safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default


_filename_forbidden = re.compile(r'[\\/:*?"<>|]+')

def _safe_filename(name: str, fallback: str = "report") -> str:
    if not name:
        return fallback
    name = _filename_forbidden.sub(" ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or fallback


# ------------------------- 데이터 조회 -------------------------
def _get_product(db: Session, source: str, product_id: str) -> dict:
    orm = (
        db.query(ProductORM)
        .filter(
            ProductORM.source == Platform.from_string(source).value,
            ProductORM.source_product_id == product_id,
        )
        .one_or_none()
    )
    if not orm:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    return {
        "title": orm.title,
        "price": orm.price,
        "source": orm.source,
        "source_product_id": orm.source_product_id,
        "source_url": getattr(orm, "url", None),
        "collected_at": orm.collected_at.strftime("%Y-%m-%d") if orm.collected_at else "",
        "category": getattr(orm, "category", None),
    }


def _get_latest_analysis(db: Session, source: str, product_id: str) -> dict:
    stmt = text("""
        SELECT
          ar.job_id,
          ar.total_reviews,
          ar.sentiment_json,   -- 퍼센트(positive/neutral/negative) 그대로
          ar.keywords_json,    -- 주요 키워드 리스트
          ar.issues_json,      -- 주요 이슈 리스트
          ar.aspects_json,     -- (있으면) 속성별 감성
          ar.trend_json,       -- (있으면) 트렌드
          ar.created_at
        FROM analysis_result ar
        JOIN analysis_jobs aj ON aj.id = ar.job_id
        WHERE aj.source = :source
          AND aj.source_product_id = :pid
        ORDER BY ar.created_at DESC
        LIMIT 1
    """)
    row = db.execute(
        stmt, {"source": Platform.from_string(source).value, "pid": product_id}
    ).mappings().first()
    if not row:
        return {}

    return {
        "job_id": row["job_id"],
        "total_reviews": row["total_reviews"] or 0,
        "sentiment_json": _json_or(row["sentiment_json"], {"positive":0,"neutral":0,"negative":0}),
        "keywords_json":  _json_or(row["keywords_json"], []),
        "issues_json":    _json_or(row["issues_json"], []),
        "aspects_json":   _json_or(row["aspects_json"], {}),
        "trend_json":     _json_or(row["trend_json"], {}),
        "created_at": row["created_at"],
    }




def _get_latest_insight(db: Session, source: str, product_id: str, job_id: str | None) -> dict:
    """
    동일 job_id 기준 최신 insight_result 1건 조회.
    job_id가 없을 때는 동일 상품의 최근 job_id를 서브쿼리로 찾아 fallback.
    (MySQL 5.7 호환: CTE 미사용)
    """
    if job_id:
        stmt = text("""
            SELECT summary, insights_json, metadata_json, evidence_ids, created_at
            FROM insight_result
            WHERE job_id = :job_id
            ORDER BY created_at DESC
            LIMIT 1
        """)
        row = db.execute(stmt, {"job_id": job_id}).mappings().first()
    else:
        # Fallback: 동일 상품의 최신 job_id 기준으로 조회
        stmt = text("""
            SELECT ir.summary, ir.insights_json, ir.metadata_json, ir.evidence_ids, ir.created_at
            FROM insight_result ir
            WHERE ir.job_id = (
                SELECT ar.job_id
                FROM analysis_result ar
                JOIN analysis_jobs aj ON aj.id = ar.job_id
                WHERE aj.source = :source AND aj.source_product_id = :pid
                ORDER BY ar.created_at DESC
                LIMIT 1
            )
            ORDER BY ir.created_at DESC
            LIMIT 1
        """)
        row = db.execute(
            stmt, {"source": Platform.from_string(source).value, "pid": product_id}
        ).mappings().first()

    if not row:
        return {
            "summary": "",
            "insights": {},
            "metadata": {},
            "evidence_ids": [],
            "created_at": None,
        }

    return {
        "summary": row["summary"] or "",
        "insights": _json_or(row["insights_json"], {}),
        "metadata": _json_or(row["metadata_json"], {}),
        "evidence_ids": _json_or(row["evidence_ids"], []),
        "created_at": row["created_at"],
    }


# ------------------------- 디버그 -------------------------
@router.get("/debug/db")
def debug_db(db: Session = Depends(get_db_session)):
    try:
        db.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB 연결 실패: {e}")


# ------------------------- PDF 라우트 -------------------------
@router.get("/product/{source}/{product_id}/pdf")
def download_pdf(source: str, product_id: str, db: Session = Depends(get_db_session)):
    product = _get_product(db, source, product_id)

    analysis = _get_latest_analysis(db, source, product_id)
    if not analysis:
        raise HTTPException(status_code=409, detail="분석 결과가 없습니다. 먼저 분석을 완료해 주세요.")

    insight = _get_latest_insight(db, source, product_id, job_id=analysis.get("job_id"))

    html = env.get_template("product_report.html").render(
        product=product,
        analysis=analysis,
        insight=insight,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    pdf_bytes = _html_to_pdf_bytes(html)

    content_disposition = _disposition_filename(product["title"])
    headers = {"Content-Disposition": content_disposition}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


from urllib.parse import quote

def _disposition_filename(title: str) -> str:
    # 표시용 원본(UTF-8) + ASCII fallback 둘 다 준비
    base = _safe_filename(title) or "report"
    utf8_name = f"{base}_분석_보고서.pdf"
    ascii_fallback = (
        base.encode("ascii", "ignore").decode().strip() or "report"
    ) + "_report.pdf"  # pure ASCII

    # RFC 5987 (filename*=UTF-8'') + ASCII fallback 동시 제공
    # 전체 헤더 문자열은 반드시 latin-1로만 구성되어야 하므로 percent-encode 사용
    return (
        f"attachment; "
        f"filename={ascii_fallback}; "
        f"filename*=UTF-8''{quote(utf8_name)}"
    )