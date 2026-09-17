"""
이미지 생성 API를 사용하여 로고 시안을 생성하는 모듈
"""

import base64
from pathlib import Path

import requests  # 파이썬의 기본 통신 라이브러리 활용하여 센터 주소 직접 지정

from utils import get_api_key

IMAGE_MODEL_NAME = "gpt-image-2"


#def get_image_client() -> OpenAI:
#    """환경 변수에서 API 키를 읽어 이미지 생성용 클라이언트를 생성한다."""
#    api_key = get_api_key("OPENAI_API_KEY")
#    return OpenAI(api_key=api_key)


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
    #client: OpenAI,
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

    # 💡 추가된 부분: API 키와 URL, 헤더를 반복문 전에 미리 준비합니다.
    api_key = get_api_key("OPENAI_API_KEY")
    url = "https://copa.codyssey.kr/api/v1/images"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for i in range(1, count + 1):
        try:
            # 💡 수정된 부분: OpenAI 라이브러리 대신 requests.post 사용
            data = {
                "model": IMAGE_MODEL_NAME,
                "prompt": prompt,
                "size": "1024x1024",
                "n": 1,
                "response_format": "b64_json"
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            # 👇👇👇 디버깅 코드 👇👇👇
            #print(f"\n🔍 [디버깅 {i}] API 상태 코드:", response.status_code)
            #print(f"🔍 [디버깅 {i}] API 응답 내용:", response.status_code)
            #print("-" * 30)
            # 👆👆👆 여기까지 👆👆👆

            response.raise_for_status()  # 에러가 나면 아래 except 블록으로 보내는 역할
            
            result = response.json() # 응답을 파이썬 딕셔너리로 변환

            # (이 아래에 이미지를 저장하는 코드가 이어질 겁니다)

        except Exception as e:
            print(f"  ⚠️ 로고 시안 {i} 생성 실패: {e}")
            continue

        # 딕셔너리에서 데이터를 꺼내는 방식 ([ ] 사용)
        # 1. 센터 API 구조에 맞게 이미지 경로(URL) 추출
        b64_data = result["result"]["images"][0]["b64_json"]

        image_bytes = base64.b64decode(b64_data)

        file_name = f"logo_{i:02d}.png"
        file_path = output_dir / file_name
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        saved_paths.append(file_path)

    return saved_paths