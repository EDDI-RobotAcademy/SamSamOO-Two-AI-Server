import os
from pathlib import Path
from dotenv import load_dotenv


def load_env():
    """
    .env, .env.local, .env.dev, .env.prod 파일을 자동 인식해서 환경 변수 로드
    우선순위:
      1. .env (공통)
      2. APP_ENV or 파일 존재 기준으로 .env.local/.env.dev/.env.prod 덮어쓰기
    """
    project_root = Path(__file__).resolve().parent.parent  # app/config → app
    base_env = project_root / ".env"

    # 1️⃣ 기본 .env 로드
    if base_env.exists():
        load_dotenv(dotenv_path=base_env, override=False)
        print(f"✅ Loaded base .env")

    # 2️⃣ APP_ENV 판단
    app_env = os.getenv("APP_ENV")
    if not app_env and (project_root / ".env.local").exists():
        app_env = "local"

    env_map = {
        "local": ".env.local",
        "dev": ".env.dev",
        "prod": ".env.prod",
    }

    # 3️⃣ 환경별 .env 로드 (override=True 로 덮어쓰기)
    if app_env in env_map:
        env_file = project_root / env_map[app_env]
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=True)
            print(f"✅ Loaded environment file: {env_file.name}")
        else:
            # ⚠️ 환경 파일이 없을 때 대체 안내
            print(f"⚠️ {env_file.name} not found — fallback to base .env values")
        os.environ["APP_ENV"] = app_env
    else:
        os.environ.setdefault("APP_ENV", "local")
        print("⚠️ APP_ENV not specified — defaulting to 'local' (.env only)")

    # ✅ 요약 로그
    print(f"✅ Final APP_ENV: {os.getenv('APP_ENV')}")


# 🔹 단독 실행 테스트
if __name__ == "__main__":
    load_env()
