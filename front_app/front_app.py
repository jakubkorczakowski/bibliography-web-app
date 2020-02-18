from flask import Flask, request, render_template, redirect, url_for, make_response, abort, flash, jsonify
import json
import os
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, get_jwt_identity

GET = "GET"
POST = "POST"
ACCESS_TOKEN = "access-token"
ACCESS_TOKEN_COOKIE = "access_token_cookie"
SECRET_KEY = "FLASK_SECRET"
USER_API_URL = "https://web_login:82/user/"
FILE_API_URL = "https://web_files:81/file/"
BIB_API_URL = "https://web_files:81/bibliography-position/"
AUTHOR_API_URL = "https://web_files:81/author/"
TOKEN_EXPIRES_IN_SECONDS = 300

NOT_EXISTING_BIBLIOGRAPHY_ID = 0

app = Flask(__name__, static_url_path="")
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = os.environ.get(SECRET_KEY)
app.secret_key = os.environ.get(SECRET_KEY)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = TOKEN_EXPIRES_IN_SECONDS
app.config['JWT_TOKEN_LOCATION'] = ('headers', 'cookies')
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = False


@jwt.unauthorized_loader
def my_unauthorized_loader_function(callback):
    return render_template("errors/403.html"), 403


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout/", methods=[GET])
@jwt_required
def logout():
    response = make_response(render_template("index.html"))
    response.delete_cookie(ACCESS_TOKEN_COOKIE)
    return response


@app.route("/login/", methods=[GET, POST])
def login():
    if (request.method == POST):
        form_data = request.form.to_dict()
        url = USER_API_URL + 'login/'

        resp = requests.post(url=url, verify=False, json=form_data)
        app.logger.debug(resp.status_code)

        if (resp.status_code == 200):
            access_token = resp.json()["access_token"]
            response = make_response(render_template("index.html"))
            set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
            return response
        elif (resp.status_code == 403):
            flash("Błędne hasło.")
            return render_template("login.html")
        elif (resp.status_code == 400):
            flash("Błędna nazwa użytkownika.")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/register/", methods=[GET, POST])
def register():
    if (request.method == POST):
        form_data = request.form.to_dict()
        url = USER_API_URL

        resp = requests.post(url=url, verify=False, json=form_data)
        app.logger.debug(resp.status_code)

        if (resp.status_code == 200):
            return render_template("index.html")
        elif (resp.status_code == 409):
            flash("Użytkownik już istnieje.")
            return render_template("registration.html")

    return render_template("registration.html")


def get_access_token(access_token):
    headers = {"Authorization": "Bearer " + access_token}

    url = USER_API_URL + 'login/'
    resp = requests.get(url=url, verify=False, headers=headers)
    app.logger.debug(resp.status_code)
    new_access_token = resp.json()["access_token"]
    return new_access_token


@app.route("/add-file/", methods=[GET, POST])
@jwt_required
def add_file():
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

    if (request.method == POST):
        url = FILE_API_URL + "list"
        headers = {"Authorization": "Bearer " + access_token}
        files = {"file": (request.files['file'].filename, request.files['file'].read())}

        resp = requests.post(url=url, verify=False, files=files, headers=headers)
        app.logger.debug(resp.status_code)

        if (resp.status_code == 200):
            return show_files()

    response = make_response(render_template("add_file.html"))
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
    return response


@app.route("/add-bibliography/", methods=[GET, POST])
@jwt_required
def add_bibliography():
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

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
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
    return response


def get_files(access_token, bib_id):
    url = FILE_API_URL + "list"
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.get(url=url, verify=False, headers=headers)
    app.logger.debug(resp.status_code)

    files = resp.json()
    bib_files = []

    for file in files["files"]:
        if file["bib_id"] == bib_id:
            bib_files.append(file)

    files["files"] = bib_files

    return files


@app.route("/files/", methods=[GET])
@jwt_required
def show_files():
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

    resp_json = get_files(access_token, NOT_EXISTING_BIBLIOGRAPHY_ID)

    response = make_response(render_template("files_list.html", resp_json=resp_json))
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)

    return response


@app.route("/bibliography/", methods=[GET])
@jwt_required
def show_bibliographies():
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

    url = BIB_API_URL + "list"
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.get(url=url, verify=False, headers=headers)
    app.logger.debug(resp.status_code)

    resp_json = resp.json()

    response = make_response(render_template("bibliographies_list.html", resp_json=resp_json))
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)

    return response


@app.route("/bibliography/<int:id>", methods=[GET])
@jwt_required
def show_one_bibliography(id):
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

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
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)

    return response


@app.route("/bibliography/add-files/<int:id>", methods=[GET])
@jwt_required
def show_bib_files(id):
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

    resp_json_files = get_files(access_token, NOT_EXISTING_BIBLIOGRAPHY_ID)

    response = make_response(render_template("files_bib_list.html", resp_json=resp_json_files, bib_id=id))
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)

    return response


@app.route("/bibliography/add-files/<int:bib_id>/<int:file_id>/", methods=[GET])
@jwt_required
def update_file(file_id, bib_id):
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

    url = FILE_API_URL + str(file_id)
    json = {"bibliography_id": bib_id}
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.post(url, json=json, headers=headers, verify=False)

    if (bib_id == NOT_EXISTING_BIBLIOGRAPHY_ID):
        return show_bibliographies()

    return show_one_bibliography(bib_id)


@app.route("/files/delete/<int:id>")
@jwt_required
def delete_file(id):
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

    url = FILE_API_URL + str(id)
    headers = {"Authorization": "Bearer " + access_token}

    resp = requests.delete(url, headers=headers, verify=False)

    return show_files()


@app.route("/bibliography/delete/<int:id>")
@jwt_required
def delete_bibliography(id):
    old_access_token = request.cookies[ACCESS_TOKEN_COOKIE]
    access_token = get_access_token(old_access_token)

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
