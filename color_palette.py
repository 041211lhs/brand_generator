"""
LLM이 생성한 컬러 팔레트(HEX 코드)를 시각화하여 PNG 이미지로 저장하는 모듈
"""

import platform
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 컬러 이름/설명에 한글이 포함될 수 있으므로 OS별 한글 폰트를 지정한다.
# 팀원 PC에 해당 폰트가 없으면 자동으로 기본 폰트로 대체될 수 있다.
_system = platform.system()
if _system == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif _system == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
else:
    plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False


def visualize_palette(
    color_palette: dict, output_dir: Path, filename: str = "color_palette.png"
) -> Path:
    """
    메인 컬러 + 서브 컬러들을 색상 스와치 형태로 그려 PNG로 저장한다.

    color_palette 예시:
    {
        "main_color": {"hex": "#2E7D32", "name": "Forest Green", "reason": "..."},
        "sub_colors": [
            {"hex": "#81C784", "name": "...", "reason": "..."},
            {"hex": "#E8F5E9", "name": "...", "reason": "..."}
        ]
    }
    """
    colors = []
    labels = []

    main_color = color_palette.get("main_color", {})
    if main_color.get("hex"):
        colors.append(main_color["hex"])
        labels.append(f"MAIN\n{main_color.get('name', '')}\n{main_color['hex']}")

    for sub_color in color_palette.get("sub_colors", []):
        if sub_color.get("hex"):
            colors.append(sub_color["hex"])
            labels.append(f"SUB\n{sub_color.get('name', '')}\n{sub_color['hex']}")

    if not colors:
        raise ValueError("시각화할 컬러 정보가 없습니다.")

    fig, ax = plt.subplots(figsize=(2.2 * len(colors), 3))

    for i, (color, label) in enumerate(zip(colors, labels)):
        rect = patches.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor="#DDDDDD")
        ax.add_patch(rect)
        ax.text(i + 0.5, -0.15, label, ha="center", va="top", fontsize=9)

    ax.set_xlim(0, len(colors))
    ax.set_ylim(-0.5, 1)
    ax.axis("off")
    ax.set_title("Brand Color Palette", fontsize=13, fontweight="bold", pad=15)

    output_path = output_dir / filename
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path