FROM python:3.12-slim

WORKDIR /app

# OpenCV 등 이미지 처리에 필요한 시스템 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 코드 복사
COPY . .

# FastAPI/Uvicorn 서버 실행 포트
EXPOSE 8000

# 서버 실행 명령어
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]