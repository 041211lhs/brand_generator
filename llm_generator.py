"""
LLM API를 사용하여 텍스트 기반 브랜드 요소(네이밍, 슬로건, 스토리, 컬러 팔레트)를 생성하는 모듈
"""

import json

from openai import OpenAI, OpenAIError

from utils import get_api_key

MODEL_NAME = "gpt-5.4"  # 팀 상황에 맞게 다른 모델로 교체 가능


def get_client() -> OpenAI:
    """환경 변수에서 API 키를 읽어 OpenAI 클라이언트를 생성한다."""
    api_key = get_api_key("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


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


def _call_llm_json(client: OpenAI, system_prompt: str, user_prompt: str) -> dict:
    """
    LLM을 호출하고 JSON으로 파싱된 결과를 반환한다.
    호출/파싱 실패 시 예외를 그대로 올려서 호출부(brand_generator.py)의
    try/except에서 '다음 단계 계속 진행'을 처리하도록 한다.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.9,
    )
    content = response.choices[0].message.content
    return json.loads(content)


def generate_naming(client: OpenAI, brief: dict) -> list:
    """브랜드 네이밍 후보 3~5개와 의미를 생성한다."""
    system_prompt = (
        "당신은 전문 브랜드 네이밍 컨설턴트입니다. "
        "결과는 반드시 순수 JSON으로만 응답하세요. 다른 설명은 붙이지 마세요."
    )
    user_prompt = (
        f"{_brief_to_text(brief)}\n\n"
        "위 정보를 바탕으로 브랜드명 후보 3~5개를 제안해줘. "
        "각 후보는 name(브랜드명)과 meaning(의미/유래 설명, 한국어 1~2문장)을 포함해야 해.\n"
        '응답 형식: {"namings": [{"name": "...", "meaning": "..."}, ...]}'
    )
    result = _call_llm_json(client, system_prompt, user_prompt)
    return result.get("namings", [])


def generate_slogans(client: OpenAI, brief: dict) -> list:
    """슬로건/태그라인 3개를 생성한다."""
    system_prompt = (
        "당신은 전문 카피라이터입니다. "
        "결과는 반드시 순수 JSON으로만 응답하세요."
    )
    user_prompt = (
        f"{_brief_to_text(brief)}\n\n"
        "위 브랜드의 톤앤매너에 맞는 슬로건/태그라인 3개를 제안해줘.\n"
        '응답 형식: {"slogans": ["...", "...", "..."]}'
    )
    result = _call_llm_json(client, system_prompt, user_prompt)
    return result.get("slogans", [])


def generate_story(client: OpenAI, brief: dict) -> str:
    """브랜드 스토리(300자 내외)를 생성한다."""
    system_prompt = (
        "당신은 브랜드 스토리텔링 전문가입니다. "
        "결과는 반드시 순수 JSON으로만 응답하세요."
    )
    user_prompt = (
        f"{_brief_to_text(brief)}\n\n"
        "위 브랜드의 탄생 배경, 철학, 비전을 포함한 브랜드 스토리를 "
        "한국어로 300자 내외로 작성해줘.\n"
        '응답 형식: {"story": "..."}'
    )
    result = _call_llm_json(client, system_prompt, user_prompt)
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
        "메인 컬러 1개와 서브 컬러 2~3개를 각각 정확한 HEX 코드(#RRGGBB)로 제시하고, "
        "컬러 이름과 선택 이유도 함께 적어줘.\n"
        '응답 형식: {"main_color": {"hex": "#RRGGBB", "name": "...", "reason": "..."}, '
        '"sub_colors": [{"hex": "#RRGGBB", "name": "...", "reason": "..."}, ...]}'
    )
    result = _call_llm_json(client, system_prompt, user_prompt)
    return result


# --- 참고: OpenAIError를 잡고 싶을 때 brand_generator.py에서 이렇게 사용 가능 ---
# try:
#     namings = generate_naming(client, brief)
# except OpenAIError as e:
#     print(f"API 호출 오류: {e}")