# MEFO
> **RAG 챗봇을 사용한 맞춤형 건강 비서 서비스 AI Server** 

## 배포 상태
- **현재 배포 상태:** 🛑 리팩토링 진행 중 (추후 배포 예정, 로컬 환경 실행 가능)
- **GitHub Repository (AI):** https://github.com/SSU-Medifood/mefo-chat

## 기술 스택
- **Language:** `Python`
- **Framework & Libraries:** `FastAPI`, `LangChain`, `Pydantic`
- **Database & Cache:** `Chroma DB`, `Redis`, `MySQL`
- **AI Model & API:** `DeepSeek-r1`, `Upstage Document Parse API`
- **Collaboration & Deployment:** `GitHub`, `Docker`, `VSCode`, `AWS EC2`

## 프로젝트 소개
- **기획 배경:** 기존의 많은 건강 관리 서비스는 레시피나 복약 관리 등 특정 기능에만 집중된 단편적인 서비스를 제공하여, 사용자가 자신의 건강 상태를 종합적으로 관리하기 어렵다는 한계가 있었습니다. 이에 MEFO는 사용자의 알레르기·질환 정보를 기반으로 한 맞춤형 식단 추천, 복약 알림, RAG(Retrieval-Augmented Generation) 기반 AI 챗봇 기능을 하나의 서비스로 통합하여 간편하고 신뢰도 높은 건강 관리 환경을 제공하고자 기획되었습니다.- **개발 기간:** 2025. 03. 04 ~ 2025. 06. 20

## 주요 기능
**RAG 기반 AI 건강 상담 챗봇**
- 사용자 건강 정보와 공공 의료 문서를 기반으로 맞춤형 질의응답 제공
- DeepSeek LLM, Chroma DB 활용 및 실시간 스트리밍(SSE)을 통한 즉각적인 답변 출력
- Upstage Document Parse API를 이용한 한국어 특화 문서 임베딩으로 할루시네이션 방지 및 신뢰도 향상

**맞춤형 식단 및 레시피 추천**
- 사용자 신체 정보 기반 권장 영양소 및 하루 식단 자동 계산
- 규칙 기반(질환/알레르기 필터링)과 콘텐츠 기반(TF-IDF, 코사인 유사도) 필터링 결합
- Redis 캐싱을 도입하여 반복 연산 최소화 및 추천 시스템 응답 속도 최적화

**개인화 흑백 음식 추천**
- 건강 상태에 따라 섭취를 권장하는 백색 음식과 피해야 할 흑색 음식을 5가지씩 추천
- LLM 프롬프트에 시드(Seed) 값을 적용하여 추천 결과의 다양성 확보

**복약 관리**
- 복용약 등록(약 종류, 1회 투여량, 복용 시간, 알림 시간 설정) 및 수정·삭제
- 설정한 시간에 맞춘 복약 알림(FCM) 수신, 시간대별 영양제 추천 정보 제공

**사용자 인증 및 관리**
- 이메일 인증 기반 회원가입, 건강 정보(성별/키/몸무게/흡연·음주 여부/알레르기/질환) 입력
- JWT 토큰 기반 로그인/인증, 비밀번호 재설정
- 마이페이지에서 건강 정보 조회·수정, 알림/마케팅 수신 설정

## 프로젝트 구조
```text
프로젝트 루트
├── .github/          # 깃허브 템플릿 (PR, Issue)
├── app/              # 메인 애플리케이션 코드
│   ├── auth/         # 보안 및 인증 관련 로직
│   ├── history/      # 챗봇 대화 기록 관리
│   ├── recipe/       # 추천 알고리즘 (규칙/콘텐츠 기반, 영양소 계산 등)
│   ├── routers/      # API 엔드포인트 라우터 (chat, recipe, recommend)
│   ├── services/     # 비즈니스 로직 (rag, recommend, chat_service 등)
│   ├── utils/        # 공통 유틸리티 (redis, response 등)
│   └── main.py       # FastAPI 애플리케이션 엔트리 포인트
├── scripts/          # DB 연결 테스트 및 임베딩 초기화 스크립트
├── Dockerfile        # 도커 이미지 빌드 설정
├── docker-compose.yml# 멀티 컨테이너 실행 설정
└── requirements.txt  # Python 의존성 패키지 목록
```

## 팀원 및 역할 분담
| 이름 | 포지션 | 담당 업무 |
|:---:|:---:|:---|
| **김소영** | AI (Data) | RAG 기반 챗봇 시스템 및 추천 알고리즘 설계/구현 |
| **임성은** | Frontend | 전체 UI 구현, SSE 기반 챗봇 스트리밍 연동 및 FCM 알림 구축 |
| **박수현** | Backend | Spring Boot 기반 API 개발, DB 설계 및 인증/인가 구현 |

## 트러블슈팅 및 기술적 의사결정
**Nginx 환경에서의 SSE(실시간 스트리밍) 연결 지연 및 버퍼링 해결:**
- **문제:** 배포 환경에서 챗봇의 실시간 스트리밍 응답이 즉각적으로 오지 않고 뭉쳐서 반환되는 현상이 발생했습니다.
- **해결:** Nginx의 기본 설정이 지속 연결을 차단하고 버퍼링을 수행함을 파악하여, 설정 파일에 `proxy_buffering off;`, `proxy_set_header Connection '';` 옵션을 추가하고 HTTP 1.1을 적용해 지속 연결을 유지하도록 개선했습니다.

**LangChain 메모리 객체 Deprecation에 따른 대화 이력 관리 구조 개편:**
- **문제:** 챗봇 대화 이력 관리를 위해 `ConversationBufferMemory`를 사용했으나, LangChain 버전 업데이트로 인해 Deprecation 경고가 발생했습니다.
- **해결:** `ChatMessageHistory()`를 통해 세션별 메모리 객체를 독립적으로 생성하고, 이를 `RunnableWithMessageHistory`에 주입하는 최신 문법으로 리팩토링하여 멀티턴(multi-turn) 대화 기능을 안정화했습니다.

**고차원 텍스트 데이터(TF-IDF)의 유사도 연산 최적화:**
- **의사결정:** 레시피 추천 시 유클리디안 거리를 사용하면 다차원 데이터에서 거리의 차이가 모호해지는 '차원의 저주'가 발생할 우려가 있었습니다. 이를 방지하기 위해 데이터의 크기를 정규화하고 벡터의 방향성을 중점적으로 비교하는 **코사인 유사도(Cosine Similarity)** 방식을 도입하여 추천의 정확도를 높였습니다.

## 실행 방법
```bash
# 1. 저장소 클론
$ git clone https://github.com/SSU-Medifood/mefo-chat.git

# 2. 패키지 설치
$ pip install -r requirements.txt

# 3. 환경 변수 설정
# 루트 디렉토리에 .env 파일을 생성하고 필요한 API KEY 및 DB URL 값을 입력하세요.

# 4. 프로젝트 실행
$ uvicorn app.main:app --reload
```

## 라이선스
제15회 숭실 캡스톤디자인 경진대회
