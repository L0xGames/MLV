import os

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        file = request.files["file"]
        file.save(os.path.join("uploads", file.filename))
        return render_template("home.html")
    return render_template('home.html')


if __name__ == '__main__':
    app.run()
