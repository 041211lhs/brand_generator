"""
공통 유틸리티 함수 모음
- 환경 변수(API 키) 로드
- 브랜드 브리프 JSON 로드
- 결과 저장, 출력 폴더 관리
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일을 읽어 os.environ에 반영한다.
# .env 파일이 없어도 에러 없이 그냥 통과한다.
load_dotenv()


def get_api_key(env_var_name: str) -> str:
    """
    환경 변수에서 API 키를 읽어온다.
    ⚠️ 코드에 API 키를 직접 작성하지 않기 위한 필수 함수.
    """
    api_key = os.environ.get(env_var_name)
    if not api_key:
        print(f"❌ 환경 변수 '{env_var_name}'가 설정되어 있지 않습니다.")
        print(f"   프로젝트 루트에 .env 파일을 만들고 아래처럼 입력해주세요:")
        print(f"   {env_var_name}=sk-xxxxxxxx")
        print("   (※ .env 파일은 절대 GitHub에 올리지 마세요. .gitignore에 포함되어 있어야 합니다.)")
        sys.exit(1)
    return api_key


def load_brief(path: str) -> dict:
    """브랜드 브리프 JSON 파일을 읽고 필수 필드를 검증한다."""
    brief_path = Path(path)
    if not brief_path.exists():
        raise FileNotFoundError(f"브리프 파일을 찾을 수 없습니다: {path}")

    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)

    required_fields = ["industry", "target", "keywords"]
    missing = [field for field in required_fields if field not in brief]
    if missing:
        raise ValueError(f"브리프 파일에 필수 필드가 없습니다: {', '.join(missing)}")

    # 선택 필드는 기본값으로 채워 이후 코드에서 KeyError가 나지 않게 한다.
    brief.setdefault("tone", "")
    brief.setdefault("competitors", [])
    brief.setdefault("notes", "")

    return brief


def ensure_output_dir(path: str) -> Path:
    """출력 폴더가 없으면 생성하고 Path 객체를 반환한다."""
    output_path = Path(path)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def save_json(data: dict, output_dir: Path, filename: str = "brand_result.json") -> Path:
    """결과 데이터를 JSON 파일로 저장한다."""
    file_path = output_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_path