# Django JWT 인증 프로젝트

Django와 Django REST Framework를 사용하여 JWT 기반 인증(회원가입, 로그인)을 구현한 프로젝트입니다. Pytest 테스트 코드와 Swagger API 문서를 포함합니다.

## 주요 기능

- 사용자 회원가입 (`/signup`)
- 사용자 로그인 (`/login`) - JWT 토큰 반환
- 인증된 엔드포인트 (`/auth`) - 유효한 JWT 토큰 필요
- 커스텀 User 모델 (`nickname` 필드 포함)
- Pytest 단위 테스트
- Swagger API 문서 (`/swagger/`)

## 로컬 환경 설정

1.  **리포지토리 클론:**
    ```bash
    git clone <your-repo-url>
    cd jwt-auth-project
    ```
2.  **가상 환경 생성 및 활성화:**
    ```bash
    python -m venv venv
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    ```
3.  **의존성 설치:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **마이그레이션 적용:**
    ```bash
    python manage.py migrate
    ```
5.  **테스트 실행 (선택 사항):**
    ```bash
    pytest
    ```
6.  **개발 서버 실행:**
    ```bash
    # settings.py에 SECRET_KEY가 설정되어 있거나 환경 변수로 설정되어 있어야 함
    python manage.py runserver 0.0.0.0:8000
    ```
7.  **접근:**
    - API: `http://localhost:8000/`
    - Swagger UI: `http://localhost:8000/swagger/`

## AWS EC2 배포 (Ubuntu 예시)

다음은 일반적인 단계입니다. 특정 설정(OS, 데이터베이스 등)에 맞게 조정하세요.

1.  **EC2 인스턴스 시작:**
    *   AWS EC2 콘솔로 이동합니다.
    *   새 인스턴스를 시작합니다 (예: Ubuntu Server LTS).
    *   인스턴스 유형을 선택합니다 (예: 프리 티어용 `t2.micro`).
    *   보안 그룹 구성:
        *   SSH (포트 22): 내 IP에서 허용.
        *   HTTP (포트 80): Anywhere (0.0.0.0/0)에서 허용.
        *   HTTPS (포트 443): Anywhere (SSL 사용 시)에서 허용.
        *   (선택 사항, 테스트용) 사용자 지정 TCP (포트 8000): 내 IP에서 허용.
    *   접근 가능한 SSH 키 페어로 인스턴스를 시작합니다.

2.  **SSH로 EC2 연결:**
    ```bash
    ssh -i /path/to/your-key.pem ubuntu@<your-ec2-public-ip>
    ```

3.  **서버 의존성 설치:**
    ```bash
    sudo apt update
    sudo apt upgrade -y
    sudo apt install python3-pip python3-dev python3-venv nginx curl git -y
    # 선택 사항: RDS PostgreSQL 사용 시 PostgreSQL 클라이언트 설치
    # sudo apt install libpq-dev postgresql-client postgresql-client-common -y
    ```

4.  **프로젝트 클론:**
    ```bash
    git clone <your-public-repo-url>
    cd <your-project-directory-name> # 예: cd jwt-auth-project
    ```

5.  **Python 환경 설정:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install gunicorn # 가상 환경 내에 Gunicorn 설치
    # PostgreSQL 사용 시: pip install psycopg2-binary (또는 빌드 도구 설치 시 psycopg2)
    ```

6.  **운영 환경용 Django 설정 구성:**
    *   **`SECRET_KEY`**: 운영용 비밀 키를 코드에 하드코딩하지 **마세요**. 환경 변수나 비밀 관리 시스템을 사용하세요.
        ```bash
        # 예시: 새 키 생성
        python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
        # 생성된 키를 안전하게 저장 (예: ~/.bashrc, systemd 서비스 파일, AWS Parameter Store)
        export SECRET_KEY='your-generated-secret-key'
        ```
    *   **`DEBUG`**: `settings.py`에서 `DEBUG = False`로 설정합니다.
    *   **`ALLOWED_HOSTS`**: `settings.py`의 `ALLOWED_HOSTS`에 EC2 인스턴스의 퍼블릭 IP 주소와 도메인 이름(있는 경우)을 추가합니다.
        ```python
        ALLOWED_HOSTS = ['<your-ec2-public-ip>', 'yourdomain.com']
        ```
    *   **데이터베이스**: `DATABASES` 설정을 운영 데이터베이스(예: AWS RDS)에 연결하도록 구성합니다. 자격 증명에는 환경 변수를 사용하세요.
    *   **정적 파일**: `STATIC_URL`이 설정되었는지 확인합니다 (예: `/static/`). `STATIC_ROOT`를 정의합니다:
        ```python
        STATIC_ROOT = BASE_DIR / 'staticfiles'
        ```

7.  **Django 애플리케이션 준비:**
    ```bash
    # 가상 환경 활성화: source venv/bin/activate
    # 환경 변수 설정 (SECRET_KEY, DB 설정 등)
    export SECRET_KEY='your-production-secret-key'
    export DATABASE_URL='your-production-db-url' # dj-database-url 사용 예시
    # ... 기타 환경 변수

    python manage.py check --deploy # 배포 전 검사 실행
    python manage.py collectstatic --noinput # 정적 파일 수집
    python manage.py migrate # 데이터베이스 마이그레이션 적용
    ```

8.  **Gunicorn 설정:**
    *   Gunicorn 수동 테스트:
        ```bash
        gunicorn --bind 0.0.0.0:8000 jwt_auth_project.wsgi:application
        # 브라우저에서 http://<your-ec2-ip>:8000 접근 (포트 8000이 열려 있는 경우)
        # 중지하려면 CTRL+C 누름
        ```
    *   프로세스 관리를 위한 Gunicorn systemd 서비스 파일 생성:
        ```bash
        sudo nano /etc/systemd/system/gunicorn.service
        ```
        다음 내용을 붙여넣고 수정합니다 (플레이스홀더 교체):
        ```ini
        [Unit]
        Description=gunicorn daemon for jwt_auth_project
        After=network.target

        [Service]
        User=ubuntu # 또는 생성한 다른 사용자
        Group=www-data # 웹 서버에서 자주 사용되는 그룹
        WorkingDirectory=/home/ubuntu/<your-project-directory-name> # 경로 수정
        # 파일에서 환경 변수 로드 (선택 사항이지만 권장)
        # EnvironmentFile=/home/ubuntu/env/jwt_auth.env
        # 또는 직접 설정 (비밀 정보에는 덜 안전):
        # Environment="SECRET_KEY=your-production-secret-key"
        # Environment="DATABASE_URL=your-production-db-url"
        ExecStart=/home/ubuntu/<your-project-directory-name>/venv/bin/gunicorn \
                  --access-logfile - \
                  --error-logfile - \
                  --workers 3 \ # CPU 코어 수에 따라 조정
                  --bind unix:/run/gunicorn.sock \ # Unix 소켓 사용
                  jwt_auth_project.wsgi:application

        [Install]
        WantedBy=multi-user.target
        ```
    *   Gunicorn 시작 및 활성화:
        ```bash
        sudo systemctl start gunicorn
        sudo systemctl enable gunicorn # 부팅 시 시작되도록 설정
        sudo systemctl status gunicorn # 상태 확인
        # 소켓 확인: sudo systemctl status gunicorn.socket (소켓 활성화 사용 시)
        # 로그 확인: sudo journalctl -u gunicorn
        ```

9.  **Nginx를 리버스 프록시로 설정:**
    *   Nginx 서버 블록 구성 파일 생성:
        ```bash
        sudo nano /etc/nginx/sites-available/jwt_auth_project
        ```
        다음 내용을 붙여넣고 수정합니다:
        ```nginx
        server {
            listen 80;
            server_name <your-ec2-public-ip> yourdomain.com; # IP/도메인으로 교체

            location = /favicon.ico { access_log off; log_not_found off; }

            location /static/ {
                # collectstatic으로 수집된 파일이 있는 경로
                root /home/ubuntu/<your-project-directory-name>;
            }

            location / {
                include proxy_params;
                # Gunicorn 소켓으로 요청 프록시
                proxy_pass http://unix:/run/gunicorn.sock;
            }
        }
        ```
    *   심볼릭 링크를 생성하여 사이트 활성화:
        ```bash
        sudo ln -s /etc/nginx/sites-available/jwt_auth_project /etc/nginx/sites-enabled/
        # 선택 사항: 기본 Nginx 설정과 충돌하는 경우 제거
        # sudo rm /etc/nginx/sites-enabled/default
        ```
    *   Nginx 구성 테스트:
        ```bash
        sudo nginx -t
        ```
    *   Nginx 재시작:
        ```bash
        sudo systemctl restart nginx
        ```

10. **애플리케이션 접근:**
    웹 브라우저를 열고 `http://<your-ec2-public-ip>` 또는 `http://yourdomain.com`으로 이동합니다.

11. **문제 해결:**
    *   Gunicorn 상태 확인: `sudo systemctl status gunicorn`
    *   Gunicorn 로그 확인: `sudo journalctl -u gunicorn`
    *   Nginx 상태 확인: `sudo systemctl status nginx`
    *   Nginx 오류 로그 확인: `sudo tail -n 50 /var/log/nginx/error.log`
    *   AWS 콘솔에서 보안 그룹 확인.
    *   Gunicorn이 환경 변수를 올바르게 로드했는지 확인.
    *   파일 권한 확인 (Nginx는 정적 파일을 읽을 수 있어야 하고, Gunicorn 소켓은 올바른 권한 필요).

12. **추가 단계 (권장):**
    *   Let's Encrypt (Certbot)를 사용하여 HTTPS 설정.
    *   로깅을 적절하게 구성.
    *   자동 배포 설정 (예: GitHub Actions, Jenkins, AWS CodeDeploy 사용).
    *   AWS RDS와 같은 관리형 데이터베이스 서비스 사용.
    *   AWS Secrets Manager 또는 Parameter Store를 사용하여 민감한 자격 증명 보호.