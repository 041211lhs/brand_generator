"""
이미지 생성 API(OpenAI DALL-E)를 사용하여 로고 시안을 생성하는 모듈
"""

import base64
from pathlib import Path

from openai import OpenAI

from utils import get_api_key

IMAGE_MODEL_NAME = "dall-e-3"


def get_image_client() -> OpenAI:
    """환경 변수에서 API 키를 읽어 이미지 생성용 클라이언트를 생성한다."""
    api_key = get_api_key("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


def _build_logo_prompt(brand_name: str, brief: dict, color_palette: dict) -> str:
    """로고 이미지 생성을 위한 영어 프롬프트를 만든다."""
    main_color = (color_palette or {}).get("main_color", {}).get("name", "")
    keywords = ", ".join(brief.get("keywords", []))
    return (
        f"A minimalist, professional logo mark for a brand named '{brand_name}'. "
        f"Industry: {brief['industry']}. Target audience: {brief['target']}. "
        f"Brand keywords: {keywords}. "
        f"Primary color theme: {main_color or 'brand-appropriate colors'}. "
        "Clean flat vector style, simple geometric shapes, white background, "
        "no extra text, suitable as a standalone brand logo icon."
    )


def generate_logos(
    client: OpenAI,
    brand_name: str,
    brief: dict,
    color_palette: dict,
    output_dir: Path,
    count: int = 2,
) -> list:
    """
    로고 시안을 count개 생성하여 PNG로 저장한다.
    dall-e-3는 한 번의 호출당 이미지 1장만 지원하므로 count번 반복 호출한다.

    반환값: 저장된 파일 경로(Path) 리스트
    """
    prompt = _build_logo_prompt(brand_name, brief, color_palette)
    saved_paths = []

    for i in range(1, count + 1):
        try:
            response = client.images.generate(
                model=IMAGE_MODEL_NAME,
                prompt=prompt,
                size="1024x1024",
                n=1,
                response_format="b64_json",
            )
        except Exception as e:
            print(f"  ⚠️ 로고 시안 {i} 생성 실패: {e}")
            continue

        image_b64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)

        file_name = f"logo_{i:02d}.png"
        file_path = output_dir / file_name
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        saved_paths.append(file_path)

    return saved_paths