# 베이스 이미지 설정
FROM python:3.9-slim

# 비대화 모드 설정
ENV DEBIAN_FRONTEND=noninteractive

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /code

# 의존성 파일 복사
COPY ./requirements.txt /code/requirements.txt

# 의존성 설치
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 앱 복사
COPY . /code

EXPOSE 8000

# 앱 실행
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
