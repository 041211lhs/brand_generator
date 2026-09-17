# brand_generator
# AI 브랜드 아이덴티티 생성기

브랜드 브리프(업종, 타겟, 키워드 등)를 입력하면 LLM API로 네이밍/슬로건/스토리/컬러 팔레트를,
이미지 생성 API(DALL-E)로 로고 시안을 자동 생성하는 CLI 프로그램입니다.

## 1. 설치

```bash
pip install -r requirements.txt
```

## 2. API 키 설정 (중요 — 팀원 모두 각자 설정 필요)

이 프로젝트는 **API 키를 코드에 직접 작성하지 않습니다.** 대신 `.env` 파일에서 읽어옵니다.

1. 프로젝트 루트에 `.env` 파일을 새로 만듭니다.
2. 아래처럼 본인의 OpenAI API 키를 입력합니다.

   ```
   OPENAI_API_KEY=sk-여기에_본인_키_입력
   ```

3. `.gitignore`에 `.env`가 포함되어 있는지 반드시 확인하세요. (이미 포함되어 있다면 그대로 두면 됩니다.)
   → `.env`는 절대 GitHub에 올라가면 안 됩니다. 팀원끼리 키를 공유할 때는 `.env` 파일 자체가 아니라
   메시지 등 별도 채널로 전달하세요.

## 3. 실행

```bash
python brand_generator.py
```

실행 후 프롬프트에 브리프 파일 경로(예: `brief.json`)와 출력 폴더 경로를 입력하면 됩니다.

## 4. 브리프 파일 형식 (`brief.json`)

| 필드 | 필수 여부 | 설명 |
|---|---|---|
| industry | 필수 | 업종 |
| target | 필수 | 타겟 고객 |
| keywords | 필수 | 브랜드 키워드 (배열) |
| tone | 선택 | 톤앤매너 |
| competitors | 선택 | 경쟁사 목록 |
| notes | 선택 | 추가 요청사항 |

## 5. 출력 결과

지정한 출력 폴더(기본값 `./output`)에 아래 파일들이 생성됩니다.

- `brand_result.json` — 네이밍/슬로건/스토리/컬러 팔레트 등 전체 텍스트 결과
- `color_palette.png` — 컬러 팔레트 시각화 이미지
- `logo_01.png`, `logo_02.png` — 로고 시안 이미지

## 6. 파일 구조

```
brand_generator.py   # 메인 CLI (전체 파이프라인 실행)
llm_generator.py      # LLM API 호출 (네이밍/슬로건/스토리/컬러)
image_generator.py    # 이미지 생성 API 호출 (로고 시안)
color_palette.py       # 컬러 팔레트 시각화 (matplotlib)
utils.py                # 공통 유틸 (env 로드, JSON 입출력)
brief.json              # 예시 브리프 입력 파일
requirements.txt        # 필요 패키지 목록
```

## 7. 에러 처리 정책

- 각 생성 단계(네이밍/슬로건/스토리/컬러/로고)는 서로 독립적으로 try/except 처리되어 있어,
  하나가 실패해도 나머지 단계는 계속 진행됩니다.
- API 키가 없거나 잘못된 경우, 어떤 환경 변수를 설정해야 하는지 안내 메시지를 출력합니다.