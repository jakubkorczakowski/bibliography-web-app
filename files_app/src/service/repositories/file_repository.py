from flask import Flask
import redis
import json
from datetime import datetime

from ...service.entity.file import File
from ...exception.exception import FileAlreadyExistsException, EmptyFilenameException

app = Flask(__name__)

FILE_COUNTER = "file_counter"
FILE_ID_PREFIX = "file_"

DIR_PATH = "files/"
NOT_EXISTING_BIBLIOGRAPHY_ID = 0


class FileRepository:

    def __init__(self):
        self.db = redis.Redis(host="redis", port=6379, decode_responses=True)
        if self.db.get(FILE_COUNTER) is None:
            self.db.set(FILE_COUNTER, 0)

    def save(self, file_to_save, username):
        app.logger.debug("Saving new file: {0}.".format(file_to_save))

        if (len(file_to_save.filename) == 0):
            raise EmptyFilenameException

        id = self.db.incr(FILE_COUNTER)

        filename_prefix = FILE_ID_PREFIX + str(id)
        new_filename = filename_prefix + file_to_save.filename
        path_to_file = DIR_PATH + new_filename
        file_to_save.save(path_to_file)
        date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')

        file = File(id, new_filename, file_to_save.filename, path_to_file, date, username, NOT_EXISTING_BIBLIOGRAPHY_ID)

        file_id = FILE_ID_PREFIX + str(file.id)
        file_json = json.dumps(file.__dict__)

        self.db.set(file_id, file_json)

        app.logger.debug("Saved new file: (id: {0}).".format(file.id))
        return file.id

    def update(self, file, username):
        app.logger.debug("Updating file: {0}.".format(file.id))

        file_id = FILE_ID_PREFIX + str(file.id)
        file_json = json.dumps(file.__dict__)

        app.logger.debug(file_json)

        self.db.set(file_id, file_json)
        app.logger.debug("Updated file: {0}.".format(file.id))
        return file.id

    def find_by_id(self, file_id_to_find, username):
        n = int(self.db.get(FILE_COUNTER))

        for i in range(1, n + 1):
            file_id = FILE_ID_PREFIX + str(i)

            if not self.db.exists(file_id):
                continue

            file_json = self.db.get(file_id)
            file = File.from_json(json.loads(file_json))

            if file.id == file_id_to_find and file.username == username:
                return file
        return None

    def del_file_by_id(self, file_id_to_del, username):
        n = int(self.db.get(FILE_COUNTER))

        for i in range(1, n + 1):
            file_id = FILE_ID_PREFIX + str(i)

            if not self.db.exists(file_id):
                continue

            file_json = self.db.get(file_id)
            file = File.from_json(json.loads(file_json))

            if file.id == file_id_to_del and file.username == username:
                self.db.delete(file_id)
                return file.id

        return None

    def count_all(self):
        app.logger.debug("Starting counting all files")
        n = int(self.db.get(FILE_COUNTER))

        n_of_files = 0

        for i in range(1, n + 1):
            file_id = FILE_ID_PREFIX + str(i)

            if self.db.exists(file_id):
                n_of_files += 1

        app.logger.debug("Counted all files (n: {0})".format(n_of_files))
        return n_of_files

    def find_n_files(self, start, limit, username):
        app.logger.debug("Finding n of files (start: {0}, limit: {1}".format(start, limit))
        n = int(self.db.get(FILE_COUNTER))

        files = []
        counter = 1

        for i in range(1, n + 1):
            file_id = FILE_ID_PREFIX + str(i)

            if not self.db.exists(file_id):
                continue

            if counter < start:
                counter += 1
                continue

            file_json = self.db.get(file_id)
            file = File.from_json(json.loads(file_json))
            if file.username == username:
                files.append(file)

            if len(files) >= limit:
                break

        app.logger.debug("Found {0} files.".format(len(files)))
        return files
