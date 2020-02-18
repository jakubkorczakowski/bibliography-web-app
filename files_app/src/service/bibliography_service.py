from flask import Flask
from src.service.repositories.bibliography_repository import BibliographyRepository
from src.service.repositories.author_repository import AuthorRepository
from src.dto.response.paginated_bibliography_response import PaginatedBibliographyResponse
from src.exception.exception import BibliographyNotFoundByIdException

app = Flask(__name__)


class BibliographyService:

    def __init__(self):
        self.bib_repo = BibliographyRepository()
        self.author_repo = AuthorRepository()

    def add_bib(self, bib_req, username):
        app.logger.debug("Adding bib...")
        bib_id = self.bib_repo.save(bib_req, username)
        app.logger.debug("Added bib (id: {0})".format(bib_id))
        return bib_id

    def get_bib_by_id(self, bib_id, username):
        app.logger.debug("Getting bib by id: {0}.".format(bib_id))
        bib = self.bib_repo.find_by_id(bib_id, username)

        if bib is None:
            raise BibliographyNotFoundByIdException("Not found bib by id: {0}".format(bib_id))

        app.logger.debug("Got bib by id: {0}".format(bib_id))
        return bib

    def get_paginated_bibs_response(self, start, limit, username):
        app.logger.debug("Getting paginated bibs (start: {0}, limit: {1})".format(start, limit))
        n_of_bibs = len(self.get_all_bibs(username))

        bibs = self.bib_repo.find_n_bibs(start, limit, username)

        bibs_response = PaginatedBibliographyResponse(bibs, start, limit, n_of_bibs)

        app.logger.debug(
            "Got paginated bibs (start: {0}, limit: {1}, count: {2}, current_size: {3})".format(start, limit, n_of_bibs,
                                                                                                len(bibs)))
        return bibs_response

    def del_bib_by_id(self, bib_id_to_del, username):
        app.logger.debug("Deleting bib...")
        bib_id = self.bib_repo.del_bib_by_id(bib_id_to_del, username)

        if bib_id is None:
            raise BibliographyNotFoundByIdException("Not found bib by id: {0}".format(bib_id))

        app.logger.debug("Added bib (id: {0})".format(bib_id))
        return bib_id

    def get_all_bibs(self, username):
        app.logger.debug("Getting all bibs")
        n_of_bibs = self.bib_repo.count_all()
        start = 1
        limit = n_of_bibs + 1

        bibs = self.bib_repo.find_n_bibs(start, limit, username)

        return bibs
