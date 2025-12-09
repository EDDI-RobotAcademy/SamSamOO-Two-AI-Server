from typing import Dict, Any, List

class AnalysisSummary:
    def __init__(self, job_id: str, summary: str, insights: Dict[str, Any],
                 metadata: Dict[str, Any], evidence_ids: List[str]):
        self.job_id = job_id
        self.summary = summary
        self.insights = insights
        self.metadata = metadata
        self.evidence_ids = evidence_ids

    def to_db_dict(self):
        # DB 저장을 위해 JSON 필드를 매핑
        return {
            "job_id": self.job_id,
            "summary": self.summary,
            "insights_json": self.insights,
            "metadata_json": self.metadata,
            "evidence_ids": self.evidence_ids
        }