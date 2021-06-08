from flask import Flask
from flask import request  # 폼으로 넘어온 데이터를 처리 하기 위함
from flask import render_template  # HTML을 렌더링 출력 하기 위함
from flask import url_for, redirect, flash, jsonify
from flask import session
# 여러가지 에러상황에 맞는 에러를 처리하기 위해 Flask 의 abort() 함수를 사용합니다.
from flask import abort
# 글작성 완료 후 문자열 형태로 넘어온 idx 값을 몽고DB 에서 사용할 수 있게 BSON 라이브러리의 ObjectId 함수를 사용합니다.
from bson.objectid import ObjectId
from flask_pymongo import PyMongo  # 몽고DB 를 사용하기 위한 라이브러리
# from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect

# 라이브러리 추가
from datetime import datetime, timedelta
import time
import math
from functools import wraps
import os

# 이미지를 통한 업로드 취약점
from PIL import Image

app = Flask(__name__)
csrf = CSRFProtect(app)
# app 생성 후 그리고 실행(run)전 환경 설정 해야합니다.
# 플라스크 환경에 몽고DB 접속 URL 설정
# 여기서 MONGO_URL 는 미리 설정되어있는 변수명
# mongodb://주소:포트/데이터베이스명
# 몽고 인스턴스는 환경 설정 후 생성 해야 합니다.(순서 중요)
# app.config["MONGO_URI"] = "mongodb://192.168.14.147:27017/myweb"   # flask-pymongo
app.config["MONGO_URI"] = "mongodb://localhost:27017/myweb"   # flask-pymongo
app.config['SECRET_KEY'] = 'password1'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
mongo = PyMongo(app)  # flask-pymongo

BOARD_IMAGE_PATH = "/home/mike_bskim/myweb/main/images" # 리눅스용, 도커파일에서 WORKDIR /app 로 설정되어있음
BOARD_ATTACH_FILE_PATH = "/home/mike_bskim/myweb/main/uploads" # 리눅스용, 도커파일에서 WORKDIR /app 로 설정되어있음
ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif", "log"])

app.config["BOARD_IMAGE_PATH"] = BOARD_IMAGE_PATH
app.config["BOARD_ATTACH_FILE_PATH"] = BOARD_ATTACH_FILE_PATH
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

if not os.path.exists(app.config["BOARD_IMAGE_PATH"]):
    os.mkdir(app.config["BOARD_IMAGE_PATH"])

if not os.path.exists(app.config["BOARD_ATTACH_FILE_PATH"]):
    os.mkdir(app.config["BOARD_ATTACH_FILE_PATH"])

# # 몽고DB
# client = MongoClient(host="192.168.14.147", port=27017)
# # myweb 데이터베이스
# db = client.myweb
# # board 컬렉션
# col = db.board

from .common import login_required, allowed_file, rand_generator, chekc_filename, hash_password, check_password
from .filter import format_datetime
from . import board
from . import member
from . import naver_api
from .telegram import messageToTelegram

app.register_blueprint(board.blueprint)
app.register_blueprint(member.blueprint)
app.register_blueprint(naver_api.blueprint)

# tele_bot.sendMessage(518558056, 'localhost test is start~~')
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
messageToTelegram('honge is start~~\n {}'.format(now))
print('__init__.py:', __name__)

