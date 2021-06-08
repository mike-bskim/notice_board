from functools import wraps
from main import session, redirect, request, url_for, ALLOWED_EXTENSIONS
from string import digits, ascii_uppercase, ascii_lowercase
import random
import re  # 정규식.
import os
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    return generate_password_hash(password)


def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)


def chekc_filename(filename): # 첨부파일 이름 변경 함수
    reg = re.compile("[^A-Za-z0-9_.가-힝-]")
    for s in os.path.sep, os.path.altsep:
        if s:
            filename = filename.replace(s,' ')
            filename = str(reg.sub('', '_'.join(filename.split()) ) ).strip("._")
    return filename


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None or session.get("id") == "":
            return redirect(url_for("member.member_login", next_url=request.url))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def rand_generator(length=8):
    char = ascii_lowercase + ascii_uppercase + digits
    return "".join(random.sample(char, length))

print('common.py:', __name__)