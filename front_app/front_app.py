from flask import Flask, request, render_template, redirect, url_for, make_response, abort, flash, jsonify
import json
import os
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, get_jwt_identity, \
    decode_token, get_raw_jwt
from authlib.integrations.flask_client import OAuth
from const_config import *
from functools import wraps

GET = "GET"
POST = "POST"
ACCESS_TOKEN = "access-token"
ACCESS_TOKEN_COOKIE = "access_token_cookie"
SECRET_KEY = "FLASK_SECRET"
USER_API_URL = "https://web_login:82/user/"
FILE_API_URL = "https://web_files:81/file/"
BIB_API_URL = "https://web_files:81/bibliography-position/"
AUTHOR_API_URL = "https://web_files:81/author/"
TOKEN_EXPIRES_IN_SECONDS = 36000

NOT_EXISTING_BIBLIOGRAPHY_ID = 0

app = Flask(__name__, static_url_path="")
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = OAUTH_CLIENT_SECRET
app.secret_key = os.environ.get(SECRET_KEY)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = TOKEN_EXPIRES_IN_SECONDS
app.config['JWT_TOKEN_LOCATION'] = ('headers', 'cookies')
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_DECODE_AUDIENCE'] = OAUTH_CLIENT_ID
app.config['JWT_IDENTITY_CLAIM'] = 'sub'

oauth = OAuth(app)

auth0 = oauth.register(
    "bib-maker-auth0",
    api_base_url=OAUTH_BASE_URL,
    client_id=OAUTH_CLIENT_ID,
    client_secret=OAUTH_CLIENT_SECRET,
    access_token_url=OAUTH_ACCESS_TOKEN_URL,
    authorize_url=OAUTH_AUTHORIZE_URL,
    client_kwargs={"scope": OAUTH_SCOPE})


@jwt.unauthorized_loader
def my_unauthorized_loader_function(callback):
    return render_template("errors/403.html"), 403


def authorization_required(f):
    @wraps(f)
    def authorization_decorator(*args, **kwds):
        try:
            access_cookie = request.cookies[ACCESS_TOKEN_COOKIE]
            return f(*args, **kwds)
        except Exception as e:
            return redirect("/login")

    return authorization_decorator


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=OAUTH_CALLBACK_URL,
        audience="")


@app.route("/logout_info")
def logout_info():
    response = make_response(render_template("./logout.html"))
    response.delete_cookie('access_token_cookie')
    return response


@app.route("/logout")
def logout():
    url_params = "returnTo=" + url_for("logout_info", _external=True)
    url_params += "&"
    url_params += "client_id=" + OAUTH_CLIENT_ID

    return redirect(auth0.api_base_url + "/v2/logout?" + url_params)


@app.route("/callback")
def oauth_callback():
    access_token = auth0.authorize_access_token()

    response = make_response(render_template("./index.html"))
    response.set_cookie('access_token_cookie', access_token['id_token'], max_age=TOKEN_EXPIRES_IN_SECONDS,
                        httponly=True, secure=True)
    return response


@app.route("/add-file/", methods=[GET, POST])
@authorization_required
@jwt_required
def add_file():
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    if (request.method == POST):
        url = FILE_API_URL + "list"
        headers = {"Authorization": "Bearer " + access_token}
        files = {"file": (request.files['file'].filename, request.files['file'].read())}

        resp = requests.post(url=url, verify=False, files=files, headers=headers)
        app.logger.debug(resp.status_code)

        if (resp.status_code == 200):
            return show_files()

    response = make_response(render_template("add_file.html"))
    return response


@app.route("/add-bibliography/", methods=[GET, POST])
@authorization_required
@jwt_required
def add_bibliography():
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    if (request.method == POST):
        form_data = request.form.to_dict()
        headers = {"Authorization": "Bearer " + access_token}
        author_form_data = {"name": form_data["author_name"],
                            "surname": form_data["author_lastname"]}
        url = AUTHOR_API_URL
        resp = requests.get(url=url, verify=False, params=author_form_data, headers=headers)
        app.logger.debug(resp.status_code)

        if (resp.status_code == 400):
            resp = requests.post(url=url, verify=False, json=author_form_data, headers=headers)
            app.logger.debug(resp.status_code)
            app.logger.debug(resp.json())
            resp_json = resp.json()
            author_id = resp_json["save_author_id"]
        elif (resp.status_code == 200):
            resp_json = resp.json()
            author_id = resp_json["id"]

        bibliography_form_data = {"title": form_data["title"],
                                  "year": form_data["year"],
                                  "author_id": author_id}

        url = BIB_API_URL + "list"
        resp = requests.post(url=url, verify=False, json=bibliography_form_data, headers=headers)
        app.logger.debug(resp.status_code)

        if (resp.status_code == 409):
            flash("Pozycja bibliograficzna o takim tytule już istnieje.")
            response = make_response(render_template("add_bibliography.html"))
            set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
            return response

        return show_one_bibliography(resp.json()["saved_bib_id"])

    response = make_response(render_template("add_bibliography.html"))
    return response


def get_files(access_token, bib_id):
    url = FILE_API_URL + "list"
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.get(url=url, verify=False, headers=headers)
    app.logger.debug(resp.status_code)

    files = resp.json()

    if files != None:
        bib_files = []

        for file in files["files"]:
            if file["bib_id"] == bib_id:
                bib_files.append(file)

        files["files"] = bib_files
    else:
        files["files"] = []

    return files


@app.route("/files/", methods=[GET])
@authorization_required
@jwt_required
def show_files():
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    resp_json = get_files(access_token, NOT_EXISTING_BIBLIOGRAPHY_ID)

    response = make_response(render_template("files_list.html", resp_json=resp_json))

    return response


@app.route("/bibliography/", methods=[GET])
@authorization_required
@jwt_required
def show_bibliographies():
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    url = BIB_API_URL + "list"
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.get(url=url, verify=False, headers=headers)
    app.logger.debug(resp.status_code)

    resp_json = resp.json()

    response = make_response(render_template("bibliographies_list.html", resp_json=resp_json))

    return response


@app.route("/bibliography/<int:id>", methods=[GET])
@authorization_required
@jwt_required
def show_one_bibliography(id):
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    url = BIB_API_URL + str(id)
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.get(url=url, verify=False, headers=headers)
    app.logger.debug(resp.status_code)
    resp_json = resp.json()
    app.logger.debug(resp_json)

    url = AUTHOR_API_URL + str(resp_json["author_id"])
    resp = requests.get(url=url, verify=False, headers=headers)
    app.logger.debug(resp.status_code)
    resp_json_author = resp.json()

    resp_json_files = get_files(access_token, id)

    response = make_response(
        render_template("bibliography_page.html", resp_json=resp_json, resp_json_author=resp_json_author,
                        resp_json_files=resp_json_files))

    return response


@app.route("/bibliography/add-files/<int:id>", methods=[GET])
@authorization_required
@jwt_required
def show_bib_files(id):
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    resp_json_files = get_files(access_token, NOT_EXISTING_BIBLIOGRAPHY_ID)

    response = make_response(render_template("files_bib_list.html", resp_json=resp_json_files, bib_id=id))

    return response


@app.route("/bibliography/add-files/<int:bib_id>/<int:file_id>/", methods=[GET])
@authorization_required
@jwt_required
def update_file(file_id, bib_id):
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    url = FILE_API_URL + str(file_id)
    json = {"bibliography_id": bib_id}
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.post(url, json=json, headers=headers, verify=False)

    if (bib_id == NOT_EXISTING_BIBLIOGRAPHY_ID):
        return show_bibliographies()

    return show_one_bibliography(bib_id)


@app.route("/files/delete/<int:id>")
@authorization_required
@jwt_required
def delete_file(id):
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    url = FILE_API_URL + str(id)
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.delete(url, headers=headers, verify=False)

    return show_files()


@app.route("/bibliography/delete/<int:id>")
@authorization_required
@jwt_required
def delete_bibliography(id):
    access_token = request.cookies[ACCESS_TOKEN_COOKIE]

    url = BIB_API_URL + str(id)
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.delete(url, headers=headers, verify=False)

    return show_bibliographies()


@app.errorhandler(400)
def bad_reqest(error):
    return render_template("errors/400.html", error=error)


@app.errorhandler(401)
def page_unauthorized(error):
    return render_template("errors/401.html", error=error)


@app.errorhandler(403)
def page_forbidden(error):
    return render_template("errors/403.html", error=error)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html", error=error)
