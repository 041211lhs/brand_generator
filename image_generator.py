"""
이미지 생성 API를 사용하여 로고 시안을 생성하는 모듈
"""

import base64
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from utils import get_api_key


# .env 파일 불러오기
load_dotenv()


# 환경 변수에서 이미지 모델명 가져오기
IMAGE_MODEL_NAME = os.getenv(
    "IMAGE_MODEL",
    "gpt-image-2"
)


def _build_logo_prompt(
    brand_name: str,
    brief: dict,
    color_palette: dict
) -> str:
    """로고 이미지 생성을 위한 영어 프롬프트를 만든다."""

    main_color = (
        (color_palette or {})
        .get("main_color", {})
        .get("name", "")
    )

    keywords = ", ".join(
        brief.get("keywords", [])
    )

    return (
        f"A minimalist, professional logo mark "
        f"for a brand named '{brand_name}'. "
        f"Industry: {brief['industry']}. "
        f"Target audience: {brief['target']}. "
        f"Brand keywords: {keywords}. "
        f"Primary color theme: "
        f"{main_color or 'brand-appropriate colors'}. "
        "Clean flat vector style, "
        "simple geometric shapes, "
        "white background, "
        "no extra text, "
        "suitable as a standalone brand logo icon."
    )


def generate_logos(
    brand_name: str,
    brief: dict,
    color_palette: dict,
    output_dir: Path,
    count: int = 2,
) -> list:
    """
    로고 시안을 count개 생성하여 PNG로 저장한다.

    반환값:
        저장된 파일 경로(Path) 리스트
    """

    prompt = _build_logo_prompt(
        brand_name,
        brief,
        color_palette
    )

    saved_paths = []

    # API 키
    api_key = get_api_key("OPENAI_API_KEY")

    # Base URL
    base_url = os.getenv("OPENAI_BASE_URL")

    if not base_url:
        raise ValueError(
            "환경 변수 'OPENAI_BASE_URL'이 설정되어 있지 않습니다."
        )

    # OPENAI_BASE_URL = https://copa.codyssey.kr/v1
    # → 이미지 생성 endpoint = /images
    url = "https://copa.codyssey.kr/api/v1/images"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for i in range(1, count + 1):

        try:

            data = {
                "model": IMAGE_MODEL_NAME,
                "prompt": prompt,
                "size": "1024x1024",
                "n": 1,
                "response_format": "b64_json",
            }

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=120,
            )

            response.raise_for_status()

            result = response.json()

            # API 응답 구조 확인
            if "data" in result:
                b64_data = result["data"][0]["b64_json"]

            elif (
                "result" in result
                and "images" in result["result"]
            ):
                b64_data = (
                    result["result"]["images"][0]["b64_json"]
                )

            else:
                raise ValueError(
                    f"예상하지 못한 이미지 API 응답 형식: "
                    f"{result}"
                )

            image_bytes = base64.b64decode(
                b64_data
            )

            file_name = f"logo_{i:02d}.png"
            file_path = output_dir / file_name

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            saved_paths.append(file_path)

            print(
                f"  - 로고 시안 {i} 저장 완료: "
                f"{file_path}"
            )

        except Exception as e:

            print(
                f"  ⚠️ 로고 시안 {i} 생성 실패: {e}"
            )

            continue

    return saved_paths