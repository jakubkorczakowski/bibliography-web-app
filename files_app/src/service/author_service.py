from flask import Flask
from src.service.repositories.author_repository import AuthorRepository
from src.exception.exception import AuthorNotFoundByIdException, AuthorNotFoundByNamesException

app = Flask(__name__)


class AuthorService:

    def __init__(self):
        self.author_repo = AuthorRepository()

    def add_author(self, author_req):
        app.logger.debug("Adding author...")
        author_id = self.author_repo.save(author_req)
        app.logger.debug("Added author (id: {0})".format(author_id))
        return author_id

    def get_author_by_id(self, author_id):
        app.logger.debug("Getting author by id: {0}.".format(author_id))
        author = self.author_repo.find_by_id(author_id)

        if author == None:
            raise AuthorNotFoundByIdException("Not found author by id: {0}".format(author_id))

        app.logger.debug("Got author by id: {0}".format(author_id))
        return author

    def get_author_by_names(self, author_name, author_lastname):
        app.logger.debug("Getting author by names: {0}, {1}.".format(author_name, author_lastname))
        author = self.author_repo.find_by_names(author_name, author_lastname)

        if author == None:
            raise AuthorNotFoundByNamesException(
                "Not found author by names: {0}, {1}.".format(author_name, author_lastname))

        app.logger.debug("Got author by names: {0}, {1}.".format(author_name, author_lastname))
        return author

    def del_author_by_id(self, author_id_to_del):
        app.logger.debug("Deleting author...")
        author_id = self.author_repo.del_author_by_id(author_id_to_del)

        if author_id == None:
            raise AuthorNotFoundByIdException("Not found author by id: {0}".format(author_id))

        app.logger.debug("Deleted author (id: {0})".format(author_id))
        return author_id
