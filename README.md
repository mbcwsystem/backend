megabox/
├── Dockerfile                  # FastAPI 앱을 Docker 이미지로 빌드하기 위한 설정 파일
├── docker-compose.yml          # API 서버, DB 등 여러 컨테이너를 동시에 실행하는 설정 파일
├── requirements.txt            # FastAPI, SQLAlchemy, Pydantic 등 필요한 패키지 목록
├── .env                        # 환경 변수 파일 (DB_URL, JWT_SECRET 등)
├── README.md                   # 프로젝트 설명서 (팀 소개, 실행법 등)
│
├── app/
│   ├── main.py                 # FastAPI 실행 진입점, 모든 라우터 등록
│   │
│   ├── core/                   # 프로젝트의 핵심 설정 관리
│   │   ├── config.py           # 환경변수 로드 및 전역 설정 (CORS, DB 등)
│   │   ├── database.py         # SQLAlchemy DB 연결 및 세션 관리
│   │   ├── security.py         # 비밀번호 해싱, JWT 토큰 생성/검증
│   │   └── __init__.py         # 패키지 인식용 파일
│   │
│   ├── utils/                  # 전역 공용 유틸리티 (중복 코드 방지)
│   │   ├── response_utils.py   # API 응답 형식(성공/에러) 통일
│   │   ├── date_utils.py       # 날짜, 시간 계산 (근무시간, 휴무일 등)
│   │   └── permission_utils.py # 사용자 권한(관리자/직원) 검증
│   │
│   ├── modules/                # 기능별 독립 모듈 (팀원별 개발 단위)
│   │   ├── auth/               # 로그인, 회원가입, 인증 관련 기능
│   │   │   ├── models.py       # User 모델 (직원/관리자 등)
│   │   │   ├── schemas.py      # Pydantic 스키마 (요청/응답 구조 정의)
│   │   │   ├── routers.py      # /auth 관련 API 라우터 정의
│   │   │   ├── services.py     # 인증, JWT, 로그인 로직 처리
│   │   │   └── __init__.py
│   │   │
│   │   ├── schedule/           # 스케줄 관리 (근무표, 일정)
│   │   │   ├── models.py       # Schedule 모델 (근무일자, 시간 등)
│   │   │   ├── schemas.py      # 요청/응답 스키마
│   │   │   ├── routers.py      # /schedule 관련 API 라우터
│   │   │   ├── services.py     # 스케줄 생성, 수정, 조회 비즈니스 로직
│   │   │   └── __init__.py
│   │   │
│   │   ├── shift/              # 근무교대 관리
│   │   │   ├── models.py       # Shift 모델 (교대 요청, 승인 상태 등)
│   │   │   ├── schemas.py      # 교대 관련 요청/응답 스키마
│   │   │   ├── routers.py      # /shift 관련 라우터
│   │   │   ├── services.py     # 교대 신청/승인 처리 로직
│   │   │   └── __init__.py
│   │   │
│   │   ├── dayoff/             # 휴무신청 관리
│   │   │   ├── models.py       # DayOff 모델 (휴가일, 사유 등)
│   │   │   ├── schemas.py      # 휴무 요청/응답 스키마
│   │   │   ├── routers.py      # /dayoff 관련 라우터
│   │   │   ├── services.py     # 휴무 신청/승인/취소 로직
│   │   │   └── __init__.py
│   │   │
│   │   ├── payroll/            # 급여 관리
│   │   │   ├── models.py       # Payroll 모델 (급여, 세금, 근무시간)
│   │   │   ├── schemas.py      # 급여 요청/응답 스키마
│   │   │   ├── routers.py      # /payroll 관련 API
│   │   │   ├── services.py     # 급여 계산 및 지급 로직
│   │   │   └── __init__.py
│   │   │
│   │   ├── community/          # 커뮤니티 (게시판, 댓글)
│   │   │   ├── models.py       # Post, Comment 모델
│   │   │   ├── schemas.py      # 게시글/댓글 요청/응답 스키마
│   │   │   ├── routers.py      # /community 관련 API
│   │   │   ├── services.py     # 게시글 작성, 수정, 삭제, 댓글 처리
│   │   │   └── __init__.py
│   │   │
│   │   ├── mainpage/           # 메인페이지 + (출근용 페이지)
│   │   │   ├── routers.py      # /mainpage 관련 API
│   │   │   ├── services.py     # 출근/퇴근 표시, 근무 현황 로직
│   │   │   ├── templates/      # 출근용 프론트 HTML 페이지
│   │   │   └── __init__.py
│   │   │
│   │   └── admin/              # 관리자 기능
│   │       ├── models.py       # 관리자 전용 테이블 (공지, 승인 로그 등)
│   │       ├── schemas.py      # 관리자 요청/응답 스키마
│   │       ├── routers.py      # /admin 관련 API
│   │       ├── services.py     # 관리자 승인, 통계, 전체 조회 로직
│   │       └── __init__.py
│   │
│   └── tests/                  # 🔍 기능별 테스트 코드 (pytest)
│       ├── test_auth.py        # 로그인/회원가입 테스트
│       ├── test_schedule.py    # 스케줄 기능 테스트
│       ├── test_shift.py       # 근무교대 테스트
│       ├── test_dayoff.py      # 휴무신청 테스트
│       ├── test_payroll.py     # 급여 계산 테스트
│       ├── test_community.py   # 커뮤니티 기능 테스트
│       ├── test_mainpage.py    # 메인(출근) 페이지 테스트
│       ├── test_admin.py       # 관리자 기능 테스트
│       └── __init__.py