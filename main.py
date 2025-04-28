from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/app')
def app_page():
    return render_template('app.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
