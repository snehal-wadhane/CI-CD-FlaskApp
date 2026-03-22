from flask import Flask, render_template, url_for, flash, redirect, request

def create_app():
    app = Flask(__name__)
    ########################################
    #          Main Page Route             #
    ########################################
    @app.route('/', methods=['GET','POST'])
    def home():
        return render_template("index.html")

    return app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5000, debug=False)