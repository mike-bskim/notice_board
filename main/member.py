from main import *
from flask import Blueprint

blueprint = Blueprint("member", __name__, url_prefix="/member")


@blueprint.route("/join", methods=["GET", "POST"])
def member_join():
    if request.method == "POST":
        name = request.form.get("name", type=str)
        email = request.form.get("email", type=str)
        pass1 = request.form.get("pass", type=str)
        pass2 = request.form.get("pass2", type=str)

        if name == "" or email == "" or pass1 == "" or pass2 == "":
            flash("입력되지 않은 값이 있습니다")
            return render_template("join.html", title="회원가입",)

        if pass1 != pass2:
            flash("비밀번호 오류")
            return render_template("join.html", title="회원가입",)

        members = mongo.db.members  # flask-pymongo
        cnt = members.find({"email": email}).count()
        if cnt > 0:
            flash("이메일 중복")
            return render_template("join.html", title="회원가입",)

        # UTC 타임스탬프를 구합니다.
        # 밀리세컨드 값을 일반 "초(sec)" 값으로 저장하기 위해 1000을 곱해 반올림합니다.
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        post = {
            "name": name,
            "email": email,
            "pass": hash_password(pass1),
            "joindate": current_utc_time,
            "logintime": "",
            "logincount": 0
        }
        members.insert_one(post)

        # return render_template("login.html", title="로그인하기",)
        return redirect(url_for("member.member_login"))

    else:
        return render_template("join.html", title="회원가입",)


@blueprint.route("/login", methods=['GET', 'POST'])
def member_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")
        next_url = request.form.get("next_url")

        members = mongo.db.members
        data = members.find_one({"email": email})

        if data is None:
            flash("사용자 없음~~")
            return render_template("login.html", title="로그인하기",)
            # return redirect(url_for("member.member_login"))
        else:
            # if data.get("pass") == password:
            if check_password(data.get("pass"), password):
                current_utc_time = round(datetime.utcnow().timestamp() * 1000)
                members.update_one({"email": email}, {
                    "$set": {"logintime": current_utc_time},
                    "$inc": {"logincount": 1}, 
                })
                session["email"] = email
                session["name"] = data.get("name")
                session["id"] = str(data.get("_id"))
                session.permanent = True

                # bot.sendMessage(chat_id=518558056, text='email({}) is logined'.format(email))
                # messageToTelegram('email({}) is logined'.format(email))

                if next_url is not None:
                    return redirect(next_url)
                # print(password, session["email"], session["name"], session["id"])
                else:
                    return redirect(url_for("board.lists"))

            else:
                flash("비번 틀림")
                return redirect(url_for("member.member_login"))

        return ""
    else:
        next_url = request.args.get("next_url", type=str)
        if next_url is not None:
            return render_template("login.html", next_url=next_url, title="로그인하기",)
        else:
            return render_template("login.html", title="로그인하기",)


@blueprint.route("/logout")
def member_logout():
    try:
        del session["name"]
        del session["id"]
        del session["email"]        
    except:
        pass

    return redirect(url_for("member.member_login"))

print('member.py:', __name__)