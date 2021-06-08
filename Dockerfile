# static 폴더 위치를 main과 같은 레벨에 넣어줄것.
# 도커 이미지를 생성할 원본 도커 이미지
FROM tiangolo/uwsgi-nginx-flask:python3.6

# 필요한 라이브러릴 설치 해야 합니다.
RUN pip install --upgrade pip
# RUN pip install flask flask-pymongo flask-wtf

# 현재 호스트 경로에서 도커내부의 폴더로 파일을 복사 합니다.
COPY . /app

# 아래 명령어는 소스파일을 먼저 복사해야 함.아래 삭제 재설치 필수임
RUN pip install -r requirements_min.txt

RUN pip uninstall -y pymongo
RUN pip install pymongo==3.7.2

# 작업 경로를 /app 으로 설정합니다.
WORKDIR /app

