from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>파이썬 플라스크</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0")
