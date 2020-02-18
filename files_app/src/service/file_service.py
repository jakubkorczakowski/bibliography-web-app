from flask import Flask
from src.service.repositories.file_repository import FileRepository
from src.exception.exception import FileNotFoundByIdException
from src.dto.response.paginated_files_response import PaginatedFilesResponse

app = Flask(__name__)


class FileService:

    def __init__(self):
        self.file_repo = FileRepository()

    def add_file(self, file, username):
        app.logger.debug("Adding file...")
        file_id = self.file_repo.save(file, username)
        app.logger.debug("Added file (id: {0})".format(file_id))
        return file_id

    def update_file(self, file_id, bib_id, username):
        app.logger.debug("Updating file...")
        file = self.file_repo.find_by_id(file_id, username)

        if file is None:
            raise FileNotFoundByIdException("Not found file by id: {0}".format(file_id, username))

        file.bib_id = bib_id

        updated_file_id = self.file_repo.update(file, username)
        app.logger.debug("Updated file by id: {0}".format(updated_file_id))
        return updated_file_id

    def get_file_by_id(self, file_id, username):
        app.logger.debug("Getting file by id: {0}.".format(file_id))
        file = self.file_repo.find_by_id(file_id, username)

        if file is None:
            raise FileNotFoundByIdException("Not found file by id: {0}".format(file_id))

        app.logger.debug("Got file by id: {0}".format(file_id))
        return file

    def del_file_by_id(self, file_id_to_del, username):
        app.logger.debug("Deleting bib...")
        file_id = self.file_repo.del_file_by_id(file_id_to_del, username)

        if file_id is None:
            raise FileNotFoundByIdException("Not found file by id: {0}".format(file_id))

        app.logger.debug("Added file (id: {0})".format(file_id))
        return file_id

    def get_paginated_files_response(self, start, limit, username):
        app.logger.debug("Getting paginated files (start: {0}, limit: {1})".format(start, limit))
        n_of_files = len(self.get_all_files(username))

        files = self.file_repo.find_n_files(start, limit, username)

        files_response = PaginatedFilesResponse(files, start, limit, n_of_files)

        app.logger.debug(
            "Got paginated files (start: {0}, limit: {1}, count: {2}, current_size: {3})".format(start, limit,
                                                                                                 n_of_files,
                                                                                                 len(files)))
        return files_response

    def get_all_files(self, username):
        app.logger.debug("Getting all files")
        n_of_files = self.file_repo.count_all()
        start = 1
        limit = n_of_files + 1

        files = self.file_repo.find_n_files(start, limit, username)

        return files
