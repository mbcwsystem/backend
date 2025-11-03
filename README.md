# 📁 프로젝트 구조 (megabox)

> **개발 환경:**  
> Python **3.13**  
> FastAPI (ASGI 기반 비동기 웹 프레임워크)  
> Docker 사용 (컨테이너 기반 개발/배포 환경)  
> MySQL **8.0** (SQLAlchemy ORM 연동)

```
megabox/
├── requirements.txt             # FastAPI, SQLAlchemy 등 필요한 패키지 목록
├── README.md                    # 프로젝트 소개 및 실행 방법 문서
├── .gitignore                   # Git에 올리지 않을 파일 설정 (env, __pycache__ 등)
├── .dockerignore                # Docker 빌드 시 제외할 파일 설정 (venv, .env 등)
│
├── .github/                     # GitHub 이슈·PR 템플릿 관리 폴더
│   ├── ISSUE_TEMPLATE/          # 이슈 생성 시 템플릿
│   │   ├── bug_report.md        # 버그 리포트 템플릿
│   │   ├── etc-template.md      # 기타 설정/문서 템플릿
│   │   └── feature_request.md   # 기능 추가 요청 템플릿
│   └── PULL_REQUEST_TEMPLATE    # PR 생성 시 기본 템플릿
│
├── envs/                        # 환경 변수 파일 보관 폴더 (Git 미포함)
│   ├── .env.dev                 # 개발 환경 변수 (로컬 실행용)
│   └── .env.prod                # 배포 환경 변수 (서버 실행용)
│
├── docker/                      # Docker 관련 설정 폴더
│   ├── Dockerfile.dev           # 개발용 도커파일 (uvicorn --reload 사용)
│   ├── Dockerfile.prod          # 배포용 도커파일 (gunicorn 사용)
│   ├── docker-compose.dev.yml   # 개발용 Docker Compose (FastAPI + MySQL)
│   └── docker-compose.prod.yml  # 배포용 Docker Compose (FastAPI + MySQL)
│
├── app/                         # FastAPI 애플리케이션 전체 코드
│   ├── main.py                  # FastAPI 실행 진입점 (모든 라우터 등록)
│   │
│   ├── core/                    # 핵심 설정 관리 폴더
│   │   ├── config.py            # .env 로드 및 환경 변수 설정 (Settings 클래스)
│   │   ├── database.py          # SQLAlchemy DB 연결 및 세션 관리
│   │   ├── routers.py           # 전체 라우터 통합 등록
│   │   ├── security.py          # JWT 토큰 생성/검증, 비밀번호 해싱
│   │   └── __init__.py          # 패키지 인식용 (비워두기)
│   │
│   ├── utils/                   # 공용 유틸리티 함수 모음
│   │   ├── response_utils.py    # 표준화된 API 응답 포맷 정의
│   │   ├── date_utils.py        # 날짜/시간 관련 계산 함수
│   │   └── permission_utils.py  # 관리자/직원 권한 검증 함수
│   │
│   ├── modules/                 # 주요 기능별 모듈 (팀 단위 개발 영역)
│   │   ├── auth/                # 로그인/회원 인증 기능
│   │   │   ├── models.py        # User 모델 정의
│   │   │   ├── schemas.py       # 요청/응답용 Pydantic 스키마
│   │   │   ├── routers.py       # /auth 관련 라우터
│   │   │   ├── services.py      # JWT·로그인 로직 처리
│   │   │   └── __init__.py
│   │   │
│   │   ├── schedule/            # 근무 스케줄 관리 기능
│   │   ├── shift/               # 근무 교대 기능
│   │   ├── dayoff/              # 휴무 신청 기능
│   │   ├── payroll/             # 급여 계산 기능
│   │   ├── community/           # 게시판/댓글 기능
│   │   ├── mainpage/            # 메인 출근 페이지 기능
│   │   └── admin/               # 관리자 기능 (회원관리, 공지 등)
│   │
│   └── tests/                   # pytest 기반 기능별 테스트 코드
│       ├── test_auth.py         # 인증 관련 테스트
│       ├── test_schedule.py     # 스케줄 기능 테스트
│       ├── test_shift.py        # 근무교대 테스트
│       ├── test_dayoff.py       # 휴무신청 테스트
│       ├── test_payroll.py      # 급여 기능 테스트
│       ├── test_community.py    # 커뮤니티 테스트
│       ├── test_mainpage.py     # 메인페이지 테스트
│       ├── test_admin.py        # 관리자 기능 테스트
│       └── __init__.py
```
