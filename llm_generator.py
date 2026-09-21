"""
LLM API를 사용하여 텍스트 기반 브랜드 요소
(네이밍, 슬로건, 스토리, 컬러 팔레트)를 생성하는 모듈
"""

import time 
import json
import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from utils import get_api_key


# .env 파일 불러오기
load_dotenv()

# 환경 변수에서 모델명 가져오기
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5.4")


def get_client() -> OpenAI:
    """환경 변수에서 API 키와 Base URL을 읽어 OpenAI 클라이언트를 생성한다."""

    api_key = get_api_key("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not base_url:
        raise ValueError(
            "환경 변수 'OPENAI_BASE_URL'이 설정되어 있지 않습니다."
        )

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def _brief_to_text(brief: dict) -> str:
    """브리프 딕셔너리를 프롬프트에 넣기 좋은 문자열로 변환한다."""

    return (
        f"업종: {brief['industry']}\n"
        f"타겟: {brief['target']}\n"
        f"키워드: {', '.join(brief['keywords'])}\n"
        f"톤앤매너: {brief.get('tone') or '지정 없음'}\n"
        f"경쟁사: {', '.join(brief.get('competitors', [])) or '없음'}\n"
        f"추가 요청사항: {brief.get('notes') or '없음'}"
    )


def _call_llm_json(
    client: OpenAI,
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3 # 최대 3번 재시도
) -> dict:
    """
    LLM을 호출하고 JSON으로 파싱된 결과를 반환한다.
    실패 시 최대 max_retries 만큼 재시도(지수 백오프)한다.
    """
    
    # 💡 여기서 for문이 시작됩니다! (최대 3번 반복)
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    },
                ],
                temperature=0.9,
                #response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("LLM 응답 내용이 비어 있습니다.")

            # 성공하면 결과 반환하고 함수 종료 (for문도 끝남)
            return json.loads(content)

        except Exception as e:
            # 에러가 발생했을 때 실행되는 부분
            print(f"\n    [경고] API 통신 지연/오류 발생 ({attempt + 1}/{max_retries}회): {e}")
            
            if attempt < max_retries - 1:
                print("    ⏳ 2초 후 재시도합니다...")
                time.sleep(2) # 2초 대기 (백오프)
            else:
                # 3번 다 실패하면 최종 에러를 발생시킴 -> 메인 파일(brand_generator.py)로 넘어가서 JSON에 기록됨
                raise e


def generate_naming(client: OpenAI, brief: dict) -> list:
    """브랜드 네이밍 후보 3~5개와 의미를 생성한다."""

    system_prompt = (
        "당신은 전문 브랜드 네이밍 컨설턴트입니다. "
        "결과는 반드시 순수 JSON으로만 응답하세요. "
        "JSON 이외의 설명은 절대 붙이지 마세요."
    )

    user_prompt = (
        f"{_brief_to_text(brief)}\n\n"
        "위 정보를 바탕으로 브랜드명 후보 3~5개를 제안해줘. "
        "각 후보는 name(브랜드명)과 meaning(의미/유래 설명, "
        "한국어 1~2문장)을 포함해야 해.\n"
        '응답 형식: '
        '{"namings": [{"name": "...", "meaning": "..."}, ...]}'
    )

    result = _call_llm_json(
        client,
        system_prompt,
        user_prompt
    )

    return result.get("namings", [])


def generate_slogans(client: OpenAI, brief: dict) -> list:
    """슬로건/태그라인 3개를 생성한다."""

    system_prompt = (
        "당신은 전문 카피라이터입니다. "
        "결과는 반드시 순수 JSON으로만 응답하세요."
    )

    user_prompt = (
        f"{_brief_to_text(brief)}\n\n"
        "위 브랜드의 톤앤매너에 맞는 "
        "슬로건/태그라인 3개를 제안해줘.\n"
        '응답 형식: '
        '{"slogans": ["...", "...", "..."]}'
    )

    result = _call_llm_json(
        client,
        system_prompt,
        user_prompt
    )

    return result.get("slogans", [])


def generate_story(client: OpenAI, brief: dict) -> str:
    """브랜드 스토리(300자 내외)를 생성한다."""

    system_prompt = (
        "당신은 브랜드 스토리텔링 전문가입니다. "
        "결과는 반드시 순수 JSON으로만 응답하세요."
    )

    user_prompt = (
        f"{_brief_to_text(brief)}\n\n"
        "위 브랜드의 탄생 배경, 철학, 비전을 포함한 "
        "브랜드 스토리를 한국어로 300자 내외로 작성해줘.\n"
        '응답 형식: {"story": "..."}'
    )

    result = _call_llm_json(
        client,
        system_prompt,
        user_prompt
    )

    return result.get("story", "")


def generate_color_palette(client: OpenAI, brief: dict) -> dict:
    """메인 컬러 1개, 서브 컬러 2~3개를 HEX 코드로 생성한다."""

    system_prompt = (
        "당신은 브랜드 컬러 전문 디자이너입니다. "
        "결과는 반드시 순수 JSON으로만 응답하세요."
    )

    user_prompt = (
        f"{_brief_to_text(brief)}\n\n"
        "위 브랜드에 어울리는 컬러 팔레트를 추천해줘. "
        "메인 컬러 1개와 서브 컬러 2~3개를 각각 "
        "정확한 HEX 코드(#RRGGBB)로 제시하고, "
        "컬러 이름과 선택 이유도 함께 적어줘.\n"
        '응답 형식: '
        '{"main_color": {"hex": "#RRGGBB", "name": "...", '
        '"reason": "..."}, '
        '"sub_colors": [{"hex": "#RRGGBB", "name": "...", '
        '"reason": "..."}, ...]}'
    )

    result = _call_llm_json(
        client,
        system_prompt,
        user_prompt
    )

    return result