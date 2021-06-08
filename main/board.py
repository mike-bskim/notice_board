from main import *
from flask import Blueprint, send_from_directory


blueprint = Blueprint("board", __name__, url_prefix="/board")


def board_delete_attach_file(filename):
    abs_path = os.path.join(app.config["BOARD_ATTACH_FILE_PATH"], filename)
    if os.path.exists(abs_path):
        os.remove(abs_path)
        return True
    return False

@blueprint.route("/comment_edit", methods=["POST"])
@login_required
def comment_edit():
    if session["id"] is None or session["id"] == "":
        return redirect(url_for("member_login"))

    if request.method == "POST":

        idx = request.form.get("id")
        comment = request.form.get("comment")

        db_comment = mongo.db.comment

        data = db_comment.find_one({"_id": ObjectId(idx)})
        if data.get("writer_id") == session.get("id"):
            db_comment.update_one(
                {"_id": ObjectId(idx)}, 
                {"$set": {"comment": comment}},
            )
            return jsonify(error="success")
        else:
            return jsonify(error="error")
            
    return abort(404)


@blueprint.route("/comment_delete", methods=["POST"])
@login_required
def comment_delete():
    if request.method == "POST":
        idx = request.form.get("id")
        db_comment = mongo.db.comment
        data = db_comment.find_one({"_id": ObjectId(idx)})
        if data.get("writer_id") == session.get("id"):
            db_comment.delete_one({"_id": ObjectId(idx)})
            return jsonify(error="success")
        else:
            return jsonify(error="error")
    return abort(401)


@blueprint.route("/comment_list/<root_idx>", methods=["GET"])
@login_required
def comment_list(root_idx):
    db_comment = mongo.db.comment
    comments = db_comment.find({"root_idx": str(root_idx)}).sort([("pubdate", -1)])

    comment_list = []
    for c in comments:
        owner = True if c.get("writer_id") == session.get("id") else False
        # if c.get("writer_id") == session.get("id"):  # session["id"] 
        #     owner = True
        # else:
        #     owner = False

        comment_list.append({
            "id": str(c.get("_id")),
            "root_idx": c.get("root_idx"),
            "name": c.get("name"),
            "writer_id": c.get("writer_id"),
            "comment": c.get("comment"),
            "pubdate": format_datetime(c.get("pubdate")),
            "owner": owner,
        })
    # print("[lists] ", comment_list)
    return jsonify(error="success", lists=comment_list)


@blueprint.route("/comment_write", methods=["POST"])
@login_required
def comment_write():
    if request.method == "POST":
        name = session.get("name")
        write_id = session.get("id")
        root_idx = request.form.get("root_idx")
        comment = request.form.get("comment")
        current_utc_time = (datetime.utcnow().timestamp() * 1000)

        db_comment = mongo.db.comment
        post = {
            "root_idx": str(root_idx),
            "writer_id": write_id,
            "name": name,
            "comment": comment,
            "pubdate": current_utc_time,
        }
        db_comment.insert_one(post)

        return jsonify(error="success")
        # return redirect(url_for("board.board_view", idx=root_idx))
    # return ""
    return abort(404)


@blueprint.route("/upload_image", methods=["POST"])
def upload_image():
    if request.method == "POST":
        file = request.files["image"]
        # print('file.content_type: ', file.content_type)
        if file and allowed_file(file.filename):
            filename = "{}.jpg".format(rand_generator())
            savefilepath = os.path.join(app.config["BOARD_IMAGE_PATH"], filename)
            file.save(savefilepath)
            try:
                img = Image.open(savefilepath)
                img.close()
                return url_for("board.board_images", filename=filename)
            except:
                os.remove(savefilepath)
                return url_for("board.board_images", filename="error")


@blueprint.route("/images/<filename>")
def board_images(filename):
    return send_from_directory(app.config["BOARD_IMAGE_PATH"], filename)


@blueprint.route("/files/<filename>")
def board_files(filename):
    return send_from_directory(app.config["BOARD_ATTACH_FILE_PATH"], filename, as_attachment=True)


@blueprint.route("/list")
def lists():
    # 페이지 값 (값이 없는 경우 기본값은 1)
    page = request.args.get("page", default=1, type=int)
    # 한페이지당 몇개의 게시물을 출력할지, 10개의 개시물을 표시
    limit = request.args.get("limit", 10, type=int)

    search = request.args.get("search", -1, type=int)
    keyword = request.args.get("keyword", "", type=str)
    # 최종 쿼리문.
    query = {}
    # 검색어 상태를 추가할 리스트 변수
    search_list = []

    if search == 0:
        search_list.append({"title": {"$regex": keyword}})
    elif search == 1:
        search_list.append({"contents": {"$regex": keyword}})
    elif search == 2:
        search_list.append({"title": {"$regex": keyword}})
        search_list.append({"contents": {"$regex": keyword}})
    elif search == 3:
        search_list.append({"name": {"$regex": keyword}})

    # 검색 대상이 한개라도 존재할 경우 query 변수에 $or 리스트를 쿼리 합니다
    if len(search_list) > 0:
        query = {"$or": search_list}
    # print(query)

    board = mongo.db.board  # flask-pymongo
    # board = col

    # 개시물의 총개수,
    tot_count = board.find(query).count()
    # 마지막 페이지의 수를 구함, 올림처리.
    last_page = math.ceil(tot_count / limit)
    # 블럭당 5개씩 표시
    block_size = 5
    # 블럭의 위치, 버림처리. 0 부터 시작.
    block_num = int((page - 1) / block_size)
    # 블럭의 시작위치
    block_start = int((block_size * block_num) + 1)
    # 블럭의 끝 위치
    block_last = math.ceil(block_start + (block_size - 1))

    datas = board.find(query).skip((page - 1) * limit).limit(limit).sort("pubdate", -1)
    # print('datas: ', str(datas))
    # datas = board.find({})

    return render_template(
        "list.html",
        datas=datas,
        limit=limit,
        page=page,
        block_start=block_start,
        block_last=block_last,
        last_page=last_page,
        search=search,
        keyword=keyword,
        title="게시판 리스트",
    )


@blueprint.route("/view/<idx>") # 팬시 url 방법임. idx 라고 표시하지 않고 , <idx> 라고 표시하면 됨.
@login_required
def board_view(idx):
    # idx = request.args.get("idx") # 팬시 url 로 처리하여 주석처리함. ?idx=~~ 으로 표시되지 않고, /~~ 직접 표시됨.
    if idx is not None:
        page = request.args.get("page")
        keyword = request.args.get("keyword")
        search = request.args.get("search")

        board = mongo.db.board  # flask-pymongo
        # board = col
        # data = board.find_one({"_id": ObjectId(idx)})
        # return_document=True 면 업데이트 결과를 data에 다시 넣어준다.
        data = board.find_one_and_update({"_id": ObjectId(idx)}, {"$inc": {"view": 1}}, return_document=True) # true면 1 증가후, 화면에 표시
        # print("aa", idx)

        if data is not None:
            result = {
                "id": data.get("_id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "pubdate": data.get("pubdate"),
                "view": data.get("view"),
                "writer_id": data.get("writer_id", ""),
                "attachfile": data.get("attachfile", ""),
            }
            # print("data.get('contents')", data.get("contents"))
            # db_comment = mongo.db.comment
            # comments = db_comment.find({"root_idx": str(data.get("_id"))})

            return render_template(
                "view.html",
                result=result,
                page=page,
                search=search,
                keyword=keyword,
                title="상세 보기",
                # comments=comments,
            )

    return abort(404)


# /write URL 은 GET, POST 두가지 방식 모두 접근 가능
@blueprint.route("/write", methods=["GET", "POST"])
@login_required
def board_write():

    # if session.get("id") is None:
    #     return redirect(url_for("member.member_login"))
    # method가 POST 인경우에는 글 작성 후의 데이터 처리
    if request.method == "POST":
        filename = None
        # print('request.files', request.files)
        # print('request.files["attachfile"]', request.files["attachfile"])
        if "attachfile" in request.files:
            file = request.files["attachfile"]
            # print("board_write/file: ", file)
            # print(file.filename)
            if file and allowed_file(file.filename):
                filename = chekc_filename(file.filename)
                file.save(os.path.join(app.config["BOARD_ATTACH_FILE_PATH"], filename))

        name = request.form.get("name")
        title = request.form.get("title")
        contents = request.form.get("contents")
        
        # UTC 타임스탬프를 구합니다.
        # 밀리세컨드 값을 일반 "초(sec)" 값으로 저장하기 위해 1000을 곱해 반올림합니다.
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)

        board = mongo.db.board  # flask-pymongo
        # board = col

        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "pubdate": current_utc_time,
            "writer_id": session.get("id"),
            "view": 0
        }

        if filename is not None:
            post["attachfile"] = filename

        # flash("테스트1")
        x = board.insert_one(post)
        # print(contents)

        # 여기서 메세지를 플래시 하면 이 다음 연결되는 페이지에서 메세지를 처리해야 합니다.
        flash("정상적으로 작성 되었습니다.")

        # 작성 완료 후 board_view 함수가 가르키는 URL로 redirect 시키며
        # 저장된 몽고DB의 데이터의 _id 값을 idx 라는 이름의 인자값으로 board_view 함수로 넘깁니다.
        print('x.inserted_id: ', x.inserted_id)
        return redirect(url_for("board.board_view", idx=x.inserted_id))

    # method 가 GET 인 경우에는 글 작성을 위한 페이지 호출
    else:
        return render_template("write.html", title="글쓰기",)


@blueprint.route("/edit/<idx>", methods=["GET", "POST"])
def board_edit(idx):
    if request.method == "GET":
        # print("board_edit/idx-GET: ", idx)
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})

        # print('board_edit/data.get("contents"): ', data.get("contents"))
        # edit_contents = data.get("contents")

        if data is None:
            flash("해당 게시물이 존재하지 않습니다")
            return redirect(url_for("board.lists"))
        else:
            if session["id"] == data.get("writer_id"):
                return render_template("edit.html", data=data, title="수정하기",)
            else:
                flash("글 수정 권한이 없습니다")
                return redirect(url_for("board.lists"))
    else:
        # print("idx-POST: ", idx)
        title = request.form.get("title")
        contents = request.form.get("contents")
        deleteoldfile = request.form.get("deleteoldfile", "")
        # print(title, contents)
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})

        if session["id"] == data.get("writer_id"):

            filename = None
            # if "attachfile" in request.files: # 첨부파일이 없어도 있는것으로 착각함.
            if request.files["attachfile"]:
                file = request.files["attachfile"]
                print("attachfile-yes, file: ", file)
                if file and allowed_file(file.filename):
                    filename = chekc_filename(file.filename)
                    file.save(os.path.join(app.config["BOARD_ATTACH_FILE_PATH"], filename))
                    print("attached filename", filename)
                    
                    if data.get("attachfile"):
                        print('deleteoldfile: ', data.get("attachfile"))
                        board_delete_attach_file(data.get("attachfile"))
            else:
                print("attachfile-no")
                if deleteoldfile == "on":
                    print("delete-yes")
                    filename = None
                    if data.get("attachfile"):
                        board_delete_attach_file(data.get("attachfile"))
                else:
                    print("delete-no")
                    filename = data.get("attachfile")

            board.update_one({"_id": ObjectId(idx)}, {
                "$set": {
                    "title": title,
                    "contents": contents,
                    "attachfile": filename
                }
            })
            flash("수정 완료")
            return redirect(url_for("board.board_view", idx=idx))
        else:
            flash("글 수정 권한이 없습니다")
            return redirect(url_for("board.lists"))


@blueprint.route("/delete/<idx>", methods=["GET", "POST"])
def board_delete(idx):
    board = mongo.db.board
    data = board.find_one({"_id": ObjectId(idx)})
    if data.get("writer_id") == session.get("id"):
        board.delete_one({"_id": ObjectId(idx)})
        flash("삭제완료")
    else:
        flash("권한없음")
    return redirect(url_for("board.lists"))

print('board.py:', __name__)