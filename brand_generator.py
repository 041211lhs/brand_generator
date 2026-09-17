"""
AI 브랜드 아이덴티티 생성기 (메인 실행 파일)

$ python brand_generator.py
"""

from utils import load_brief, ensure_output_dir, save_json
from llm_generator import (
    get_client,
    generate_naming,
    generate_slogans,
    generate_story,
    generate_color_palette,
)
from image_generator import get_image_client, generate_logos
from color_palette import visualize_palette


def main():
    print("\n🎨 AI 브랜드 아이덴티티 생성기\n")

    brief_path = input("브리프 파일 경로를 입력하세요: ").strip()
    output_dir_input = input("출력 폴더 경로를 입력하세요 (엔터 시 ./output): ").strip()
    output_dir_path = output_dir_input if output_dir_input else "./output"

    # 브리프 로드 (필수 입력이므로 실패하면 더 진행할 수 없어 여기서 종료)
    try:
        brief = load_brief(brief_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ 브리프 파일을 불러오는 중 오류가 발생했습니다: {e}")
        return

    output_dir = ensure_output_dir(output_dir_path)

    result = {
        "brief": brief,
        "namings": [],
        "slogans": [],
        "story": "",
        "color_palette": {},
        "logo_files": [],
    }

    # LLM 클라이언트 생성 (API 키가 없으면 utils.get_api_key에서 안내 후 종료됨)
    client = get_client()

    print()

    # [1/5] 브랜드 네이밍 생성
    print("[1/5] 브랜드 네이밍 생성 중...")
    try:
        namings = generate_naming(client, brief)
        result["namings"] = namings
        for item in namings:
            print(f"  - {item.get('name')} : {item.get('meaning')}")
    except Exception as e:
        print(f"  ⚠️ 네이밍 생성 실패: {e}")

    # [2/5] 슬로건 생성
    print("[2/5] 슬로건 생성 중...")
    try:
        slogans = generate_slogans(client, brief)
        result["slogans"] = slogans
        for slogan in slogans:
            print(f'  - "{slogan}"')
    except Exception as e:
        print(f"  ⚠️ 슬로건 생성 실패: {e}")

    # [3/5] 브랜드 스토리 생성
    print("[3/5] 브랜드 스토리 생성 중...")
    try:
        story = generate_story(client, brief)
        result["story"] = story
        print(f"  - 스토리 생성 완료 ({len(story)}자)")
    except Exception as e:
        print(f"  ⚠️ 스토리 생성 실패: {e}")

    # [4/5] 컬러 팔레트 생성 및 시각화
    print("[4/5] 컬러 팔레트 생성 중...")
    color_palette = {}
    try:
        color_palette = generate_color_palette(client, brief)
        result["color_palette"] = color_palette

        main_color = color_palette.get("main_color", {})
        sub_colors = color_palette.get("sub_colors", [])
        print(f"  - 메인: {main_color.get('hex')} ({main_color.get('name')})")
        if sub_colors:
            sub_hex_list = ", ".join(c.get("hex", "") for c in sub_colors)
            print(f"  - 서브: {sub_hex_list}")

        palette_path = visualize_palette(color_palette, output_dir)
        print(f"  - 저장: {palette_path}")
    except Exception as e:
        print(f"  ⚠️ 컬러 팔레트 생성/저장 실패: {e}")

    # [5/5] 로고 시안 생성
    print("[5/5] 로고 시안 생성 중...")
    try:
        brand_name = (
            result["namings"][0]["name"] if result["namings"] else brief["industry"]
        )
        image_client = get_image_client()
        logo_paths = generate_logos(
            image_client, brand_name, brief, color_palette, output_dir, count=2
        )
        result["logo_files"] = [str(p) for p in logo_paths]
        for p in logo_paths:
            print(f"  - 저장: {p}")
    except Exception as e:
        print(f"  ⚠️ 로고 시안 생성 실패: {e}")

    # 결과 저장
    result_path = save_json(result, output_dir)
    print(f"\n✅ 완료! {output_dir}/ 폴더를 확인하세요. (결과 JSON: {result_path.name})")


if __name__ == "__main__":
    main()