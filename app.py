from flask import Flask, render_template, session, redirect, request, url_for, flash


app = Flask(__name__)


@app.route('/')
def home():
    return 'testing'


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)