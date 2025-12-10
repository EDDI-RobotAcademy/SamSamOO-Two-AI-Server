"""
Redis 기반 세션 인증 헬퍼 함수들
"""
import json
from fastapi import HTTPException, Cookie
from typing import Optional
from config.redis_config import get_redis

redis_client = get_redis()


def get_current_user_id(session_id: str | None = Cookie(None)) -> int:
    """
    Redis 세션에서 현재 로그인한 사용자의 ID를 가져옵니다.

    Args:
        session_id: 쿠키에서 자동으로 추출되는 세션 ID

    Returns:
        int: 로그인한 사용자의 account.id

    Raises:
        HTTPException: 로그인하지 않은 경우 401 에러
    """
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="로그인이 필요합니다. (세션 ID 없음)"
        )

    redis_key = f"session:{session_id}"
    session_data = redis_client.get(redis_key)

    if not session_data:
        raise HTTPException(
            status_code=401,
            detail="세션이 만료되었거나 존재하지 않습니다."
        )

    # bytes → str 변환
    if isinstance(session_data, bytes):
        session_data = session_data.decode("utf-8")

    session_dict = json.loads(session_data)
    user_id = session_dict.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="세션 데이터가 올바르지 않습니다."
        )

    return int(user_id)


def get_current_user_info(session_id: str | None = Cookie(None)) -> dict:
    """
    Redis 세션에서 현재 로그인한 사용자의 전체 정보를 가져옵니다.

    Args:
        session_id: 쿠키에서 자동으로 추출되는 세션 ID

    Returns:
        dict: 사용자 정보 (user_id, access_token 등)

    Raises:
        HTTPException: 로그인하지 않은 경우 401 에러
    """
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="로그인이 필요합니다."
        )

    redis_key = f"session:{session_id}"
    session_data = redis_client.get(redis_key)

    if not session_data:
        raise HTTPException(
            status_code=401,
            detail="세션이 만료되었습니다."
        )

    # bytes → str 변환
    if isinstance(session_data, bytes):
        session_data = session_data.decode("utf-8")

    session_dict = json.loads(session_data)

    return session_dict


def get_optional_user_id(session_id: str | None = Cookie(None)) -> Optional[int]:
    """
    Redis 세션에서 사용자 ID를 가져옵니다. (선택적)
    로그인하지 않은 경우 None을 반환합니다.

    Args:
        session_id: 쿠키에서 자동으로 추출되는 세션 ID

    Returns:
        Optional[int]: 로그인한 사용자의 ID 또는 None
    """
    if not session_id:
        return None

    redis_key = f"session:{session_id}"
    session_data = redis_client.get(redis_key)

    if not session_data:
        return None

    try:
        # bytes → str 변환
        if isinstance(session_data, bytes):
            session_data = session_data.decode("utf-8")

        session_dict = json.loads(session_data)
        user_id = session_dict.get("user_id")

        return int(user_id) if user_id else None
    except:
        return None