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

## 7. 에러 처리 및 방어적 프로그래밍 정책

- **독립적 실행 및 에러 기록:** 각 생성 단계는 독립적인 `try/except` 블록으로 처리되어, 한 단계가 실패해도 프로그램이 중단되지 않고 다음 단계가 계속 진행됩니다. 또한, 발생한 에러는 단순히 화면에 출력되는 것에 그치지 않고 최종 결과물인 `brand_result.json`의 `"errors"` 필드에 상세히 기록되어 추후 디버깅이 가능하도록 방어적 프로그래밍을 구현했습니다.
- **재시도(Retry) 및 백오프 알고리즘:** 일시적인 네트워크 오류나 API Rate Limit(429)에 대비하여, API 호출 모듈(`_call_llm_json`) 내부에 최대 3회 재시도 및 2초 대기(`time.sleep`)를 수행하는 지수 백오프(Exponential Backoff) 로직을 구현하여 시스템 안정성을 대폭 확보했습니다.

## 8. 기술적 설계 및 아키텍처 소명

### 8.1 모듈화 및 책임 분리 전략
본 프로젝트는 단일 책임 원칙(SRP)을 준수하여 기능별로 모듈을 엄격히 분리했습니다.
- `brand_generator.py`: 전체 파이프라인 흐름 제어 및 에러 취합(JSON 기록) 담당
- `llm_generator.py`: LLM API 호출 및 텍스트 생성 (공통 호출 함수로 중복 코드 제거)
- `image_generator.py` / `color_palette.py`: 시각화 및 이미지 생성 전담

### 8.2 프롬프트 엔지니어링 설계 근거
- **페르소나 부여:** AI에게 "전문 브랜드 네이밍 컨설턴트", "전문 카피라이터" 등의 명확한 역할을 시스템 프롬프트로 부여하여 결과물의 전문성을 높였습니다.
- **제약 조건:** "결과는 반드시 순수 JSON으로만 응답하세요"라는 강력한 제약 조건을 명시하여 파싱 오류를 방지했습니다.

### 8.3 컨텍스트(Context) 유지 및 체인(Chain) 연결
- 이전 단계의 결과물을 다음 단계의 프롬프트나 파라미터로 직접 주입(Injection)하는 데이터 파이프라인을 구축했습니다.
- 예: 1단계에서 생성된 `brand_name`과 4단계의 `color_palette` 데이터를 5단계 로고 생성(`generate_logos`)의 파라미터로 전달하여 전체 브랜드 아이덴티티의 일관성을 유지했습니다.

### 8.4 JSON 포맷 강제화 기법
- 초기에는 OpenAI API의 JSON Mode (`response_format={"type": "json_object"}`)를 적용하려 했으나, 제공된 센터 API 환경에서 해당 기능이 지원되지 않는 이슈(400 에러: unsupported_feature)를 확인했습니다.
- 이를 해결하기 위해 **프롬프트 엔지니어링 기법**으로 선회했습니다. "반드시 아래의 JSON 형식으로만 출력할 것"이라는 강력한 시스템 지시어와 함께, 기대하는 JSON 스키마 예시(Few-shot)를 프롬프트에 명시적으로 포함시켜 LLM의 자유로운 응답 포맷을 JSON으로 완벽하게 고정하는 데 성공했습니다.