from flask import Flask, request, send_file
from flask_restplus import Api, Resource, fields
from src.dto.request.bibliography_request import BibliographyRequest
from src.dto.request.author_request import AuthorRequest
from src.dto.request.file_request import FileRequest
from src.service.bibliography_service import BibliographyService
from src.service.author_service import AuthorService
from src.service.file_service import FileService
from src.exception.exception import BibliographyAlreadyExistsException, AuthorAlreadyExistsException, \
    AuthorNotFoundByIdException, FileAlreadyExistsException, BibliographyNotFoundByIdException
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, get_jwt_identity
import os
import requests

app = Flask(__name__)
api_app = Api(app=app, version="0.1", title="Bib-Maker Main API", description="REST-full API for bibliography service")

author_namespace = api_app.namespace("author", description="Author API")
bibliography_namespace = api_app.namespace("bibliography-position", description="Bibliography Postion API")
file_namespace = api_app.namespace("file", description="File API")
hello_namespace = api_app.namespace("hello", description="Hello API")

START = "start"
LIMIT = "limit"

SECRET_KEY = "FLASK_SECRET"
SESSION_ID = "my-session-id"
ACCESS_TOKEN = "access-token"
TOKEN_EXPIRES_IN_SECONDS = 300

app.config['JWT_SECRET_KEY'] = os.environ.get(SECRET_KEY)
app.secret_key = os.environ.get(SECRET_KEY)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = TOKEN_EXPIRES_IN_SECONDS
app.config['JWT_TOKEN_LOCATION'] = ('headers', 'cookies')
app.config['JWT_COOKIE_SECURE'] = True
jwt = JWTManager(app)

NOT_EXISTING_BIBLIOGRAPHY_ID = 0


@hello_namespace.route("/")
class Hello(Resource):

    def __init__(self, args):
        super().__init__(args)

    def get(self):
        result = {"message": "Hello from the other side."}

        return result


@author_namespace.route("/")
class Author(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.author_service = AuthorService()

    new_author_model = api_app.model("Author model",
                                     {
                                         "name": fields.String(required=True, description="Author name",
                                                               help="Name cannot be blank"),
                                         "surname": fields.String(required=True, description="Author surname",
                                                                  help="Surname cannot be null")
                                     })

    @api_app.expect(new_author_model)
    @jwt_required
    def post(self):
        try:
            author_req = AuthorRequest(request)
            saved_author_id = self.author_service.add_author(author_req)

            result = {"message": "Added new author", "save_author_id": saved_author_id}

            return result

        except AuthorAlreadyExistsException as e:
            author_namespace.abort(409, e.__doc__, status="Could not save author. Already exists", statusCode=409)

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"name": "Specify author name",
                         "surname": "Specify author surname"})
    @api_app.param("name", "Specify author name.")
    @api_app.param("surname", "Specify author surname.")
    @jwt_required
    def get(self):
        try:
            name = request.args.get("name")
            surname = request.args.get("surname")

            author = self.author_service.get_author_by_names(name, surname)
            return author.__dict__

        except Exception as e:
            author_namespace.abort(400, e.__doc__, status="Could not find author by names", statusCode="400")


@author_namespace.route("/<int:id>")
class AuthorID(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.author_service = AuthorService()

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify author Id"})
    @jwt_required
    def get(self, id):
        try:
            author = self.author_service.get_author_by_id(id)
            return author.__dict__

        except Exception as e:
            author_namespace.abort(400, e.__doc__, status="Could not find author by id", statusCode="400")

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify author Id"})
    @jwt_required
    def delete(self, id):
        try:

            author_id = self.author_service.del_author_by_id(id)

            return {
                "message": "Removed author by id: {0}".format(author_id)
            }

        except Exception as e:
            author_namespace.abort(400, e.__doc__, status="Could not remove author by id", statusCode="400")


@bibliography_namespace.route("/<int:id>")
class Bibliography(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.bib_service = BibliographyService()
        self.file_service = FileService()

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify bibliography postion Id"})
    @jwt_required
    def get(self, id):
        try:
            username = get_jwt_identity()
            bib = self.bib_service.get_bib_by_id(id, username)
            return bib.__dict__

        except Exception as e:
            bibliography_namespace.abort(400, e.__doc__, status="Could not find bibliography postion by id",
                                         statusCode="400")

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify bibliography postion Id to remove"})
    @jwt_required
    def delete(self, id):
        try:
            username = get_jwt_identity()
            bib_id = self.bib_service.del_bib_by_id(id, username)

            files = self.file_service.get_all_files(username)

            for file in files:
                if file.bib_id == bib_id:
                    self.file_service.update_file(file.id, NOT_EXISTING_BIBLIOGRAPHY_ID, username)

            return {
                "message": "Removed bibliography postion by id: {0}".format(bib_id)
            }

        except Exception as e:
            bibliography_namespace.abort(400, e.__doc__, status="Could not remove bibliography postion by id",
                                         statusCode="400")


@bibliography_namespace.route("/list")
class BibliographyList(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.bib_service = BibliographyService()
        self.author_service = AuthorService()

    new_bib_model = api_app.model("Bibliography model",
                                  {
                                      "title": fields.String(required=True, description="bibliography position title",
                                                             help="Title cannot be null", example="Bieguni"),
                                      "year": fields.Integer(required=True, description="Year of publication",
                                                             help="Year cannot be null", example="2007"),
                                      "author_id": fields.Integer(required=True, description="Author's Id ",
                                                                  help="Author's Id cannot be null")

                                  })

    @api_app.param(START, "The data will be returned from this position.")
    @api_app.param(LIMIT, "The max size of returned data.")
    @api_app.doc(responses={200: "OK"})
    @jwt_required
    def get(self):
        username = get_jwt_identity()

        start = self.parse_request_arg_or_zero(request, START, "0")
        start = max(1, start)
        all_user_bibs = self.bib_service.get_all_bibs(username)
        default_limit = len(all_user_bibs)
        limit = self.parse_request_arg_or_zero(request, LIMIT, str(default_limit))

        paginated_bib_response = self.bib_service.get_paginated_bibs_response(start, limit, username)

        return paginated_bib_response.get_json(request.base_url)

    def parse_request_arg_or_zero(self, request, param, default_value):
        val = request.args.get(param, default_value)
        val = int(val) if val.isdigit() else 0
        return val

    @api_app.expect(new_bib_model)
    @jwt_required
    def post(self):
        try:
            bib_req = BibliographyRequest(request)
            author = self.author_service.get_author_by_id(bib_req.author_id)
            username = get_jwt_identity()
            saved_bib_id = self.bib_service.add_bib(bib_req, username)

            result = {"message": "Added new bibliography postion", "saved_bib_id": saved_bib_id}

            return result

        except KeyError as e:
            bibliography_namespace.abort(400, e.__doc__, status="Could not save new bibliography position",
                                         statusCode="400")

        except BibliographyAlreadyExistsException as e:
            bibliography_namespace.abort(409, e.__doc__,
                                         status="Could not save new bibliography position. Already exists",
                                         statusCode="409")

        except AuthorNotFoundByIdException as e:
            bibliography_namespace.abort(404, e.__doc__,
                                         status="Could not save new bibliography position. Author (by id) does not exist.",
                                         statusCode="404")


@file_namespace.route("/download/<int:id>")
class FileDownloadID(Resource):
    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"file_id": "Specify file Id"})
    @jwt_required
    def get(self, id):
        try:
            username = get_jwt_identity()
            file = self.file_service.get_file_by_id(id, username)
            return send_file(file.path_to_file, attachment_filename=file.org_filename, as_attachment=True)

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not find file by id",
                                 statusCode="400")


@file_namespace.route("/<int:id>")
class File(Resource):
    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()
        self.bib_service = BibliographyService()

    update_file_model = api_app.model("Update file model",
                                      {
                                          "bibliography_id": fields.Integer(required=True,
                                                                            description="bibliography id",
                                                                            help="Bibliography id cannot be null")

                                      })

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"file_id": "Specify file Id"})
    @jwt_required
    def get(self, id):
        try:
            username = get_jwt_identity()
            file = self.file_service.get_file_by_id(id, username)
            return file.__dict__

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not find file by id",
                                 statusCode="400")

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify file Id to remove"})
    @jwt_required
    def delete(self, id):
        try:
            username = get_jwt_identity()
            file_id = self.file_service.del_file_by_id(id, username)

            return {
                "message": "Removed bibliography postion by id: {0}".format(file_id)
            }

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not remove bibliography postion by id",
                                 statusCode="400")

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify file Id"})
    @api_app.expect(update_file_model)
    @jwt_required
    def post(self, id):
        try:
            username = get_jwt_identity()
            bib_id = request.json["bibliography_id"]

            if bib_id != NOT_EXISTING_BIBLIOGRAPHY_ID:
                bib = self.bib_service.get_bib_by_id(bib_id, username)

            updated_file_id = self.file_service.update_file(id, bib_id, username)

            result = {"message": "Updated file", "saved_file_id": updated_file_id}

            return result

        except KeyError as e:
            file_namespace.abort(400, e.__doc__, status="Could not update file by id",
                                 statusCode="400")

        except BibliographyNotFoundByIdException as e:
            file_namespace.abort(404, e.__doc__,
                                 status="Could not update new file. Bibliography (by id) does not exist.",
                                 statusCode="404")

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not update file by id",
                                 statusCode="400")


@file_namespace.route("/list")
class FileList(Resource):
    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()
        self.bib_service = BibliographyService()

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify file Id"})
    @jwt_required
    def post(self):
        try:
            file = request.files["file"]
            username = get_jwt_identity()
            saved_file_id = self.file_service.add_file(file, username)

            result = {"message": "Added new file", "saved_file_id": saved_file_id}

            return result

        except KeyError as e:
            file_namespace.abort(400, e.__doc__, status="Could not save new file",
                                 statusCode="400")

        except FileAlreadyExistsException as e:
            file_namespace.abort(409, e.__doc__,
                                 status="Could not save new file. Already exists",
                                 statusCode="409")

    @api_app.param(START, "The data will be returned from this position.")
    @api_app.param(LIMIT, "The max size of returned data.")
    @api_app.doc(responses={200: "OK"})
    @jwt_required
    def get(self):
        username = get_jwt_identity()

        start = self.parse_request_arg_or_zero(request, START, "0")
        start = max(1, start)
        all_user_files = self.file_service.get_all_files(username)
        default_limit = len(all_user_files)
        limit = self.parse_request_arg_or_zero(request, LIMIT, str(default_limit))

        paginated_files_response = self.file_service.get_paginated_files_response(start, limit, username)

        return paginated_files_response.get_json(request.base_url)

    def parse_request_arg_or_zero(self, request, param, default_value):
        val = request.args.get(param, default_value)
        val = int(val) if val.isdigit() else 0
        return val
