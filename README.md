# 🐳 DongneBook 개발 환경

DongneBook 프로젝트는 **Django + Docker** 기반의 간단한 웹 애플리케이션 개발 환경입니다.  
로컬에서 빠르게 개발을 시작할 수 있도록 **SQLite**를 사용하며, Docker 환경에서 손쉽게 실행 가능합니다.

---

## 📁 프로젝트 구조

```plaintext
Dongnebook/
├── Dockerfile             # Django 베이스 이미지 설정
├── docker-compose.yml     # 서비스 정의 및 포트 매핑
├── requirements.txt       # 필요한 Python 패키지 목록
├── manage.py              # Django 관리 명령어 실행 스크립트
└── config/
    └── settings.py        # Django 설정 파일
```

---

## 🚀 실행 방법

### 1. 프로젝트 클론 및 디렉토리 이동

```bash
https://lab.ssafy.com/rlwhdtn97/dongnebook.git
cd dongnebook
```

### 2. Docker 이미지 빌드 및 컨테이너 실행

```bash
docker-compose up --build
```

### 3. 웹 브라우저에서 접속 확인

```bash
http://127.0.0.1:8000/
```

---

## 📌 참고 사항
명령어는 docker-compose exec를 붙혀서 사용합니다
ex) docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py runserver
    docker-compose exec web python manage.py createsuperuser



- 데이터베이스는 **SQLite(db.sqlite3)** 를 사용하며, 로컬에 저장됩니다.
- 코드 수정은 **실시간으로 반영**됩니다 (`volumes` 설정 덕분에).
- 실제 배포 시에는 **PostgreSQL, Gunicorn, Nginx** 등을 추가하는 것이 권장됩니다.
