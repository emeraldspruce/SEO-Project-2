from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def first():
    return render_template("first.html")

@app.route("/second.html")
def second():
    return render_template("second.html")

@app.route("/third.html")
def third():
    return render_template("third.html")

if __name__ == "__main__":
    app.run(debug=True)