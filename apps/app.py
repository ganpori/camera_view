from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from apps.config import config

db = SQLAlchemy()
csrf = CSRFProtect()
# LoginManagerをインスタンス化する
login_manager = LoginManager()
# login_view属性に未ログイン時にリダイレクトするエンドポイントを指定する
login_manager.login_view = "auth.signup"
# login_message属性にログイン後に表示するメッセージを指定する
# ここでは何も表示しないよう空を指定する
login_manager.login_message = ""


# create_app関数を作成する
def create_app(config_key):
    # Flaskインスタンス生成
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    # SQLAlchemyとアプリを連携する
    db.init_app(app)
    # Migrateとアプリを連携する
    Migrate(app, db)
    csrf.init_app(app)
    # login_managerをアプリケーションと連携する
    login_manager.init_app(app)

    # crudパッケージからviewsをimportする
    from apps.crud import views as crud_views

    # register_blueprintを使いviewsのcrudをアプリへ登録する
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    # これから作成するauthパッケージからviewsをimportする
    from apps.auth import views as auth_views

    # register_blueprintを使いviewsのauthをアプリへ登録する
    app.register_blueprint(auth_views.auth, url_prefix="/auth")
    # これから作成するdetectorパッケージからviewsをimportする
    from apps.detector import views as dt_views

    # register_blueprintを使いviewsのdtをアプリへ登録する
    app.register_blueprint(dt_views.dt)

    # カスタムエラー画面を登録する
    # app.register_error_handler(404, page_not_found)
    # app.register_error_handler(500, internal_server_error)

    return app


def app_gunicorn(env, start_response):
    # https://hogetech.info/network/web/gunicorn

    status = " 200 OK"
    response_headers = [("Content-type", "text/plain;charset=utf-8")]
    start_response(status, response_headers)
    if env.get("PATH_INFO") == "/":  # "/" パス
        return [b"Hello World\n"]  # バイト列を返す
    if env.get("PATH_INFO") == "/other":  # "/other" パス
        return [b"Other World\n"]  # バイト列を返す


# このオブジェクトをgunicorn apps.app:app_for_gunicorn として実行する
app_for_gunicorn = create_app(config_key="local")

# nginxの説明ページ。https://snowtree-injune.com/2020/10/30/nginx-static-dj014/
# You should look at the following URL's in order to grasp a solid understanding
# of Nginx configuration files in order to fully unleash the power of Nginx.
# https://www.nginx.com/resources/wiki/start/
# https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/
# https://wiki.debian.org/Nginx/DirectoryStructure


# 登録したエンドポイント名の関数を作成し、404や500が発生した際に指定したHTMLを返す
def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404


def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"), 500
