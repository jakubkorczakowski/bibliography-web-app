from flask import Flask
import redis
import json

from ...service.entity.bibliographyposition import BibliographyPosition
from ...exception.exception import BibliographyAlreadyExistsException

app = Flask(__name__)

BIBLIOGRAPHY_COUNTER = "bib_counter"
BIBLIOGRAPHY_ID_PREFIX = "bib_"


class BibliographyRepository:

    def __init__(self):
        self.db = redis.Redis(host="redis", port=6379, decode_responses=True)
        if self.db.get(BIBLIOGRAPHY_COUNTER) is None:
            self.db.set(BIBLIOGRAPHY_COUNTER, 0)

    def save(self, bib_req, username):
        app.logger.debug("Saving new bib: {0}.".format(bib_req))
        bib = self.find_bib_by_title(bib_req.title, username)

        if bib != None:
            raise BibliographyAlreadyExistsException("bib title \"{0}\" already exist.".format(bib_req.title))

        bib = BibliographyPosition(self.db.incr(BIBLIOGRAPHY_COUNTER), bib_req.author_id, bib_req.title, bib_req.year,
                                   username)

        bib_id = BIBLIOGRAPHY_ID_PREFIX + str(bib.id)
        bib_json = json.dumps(bib.__dict__)

        self.db.set(bib_id, bib_json)

        app.logger.debug("Saved new bib: (id: {0}).".format(bib.id))
        return bib.id

    def find_bib_by_title(self, title, username):
        n = int(self.db.get(BIBLIOGRAPHY_COUNTER))

        for i in range(1, n + 1):
            bib_id = BIBLIOGRAPHY_ID_PREFIX + str(i)

            if not self.db.exists(bib_id):
                continue

            bib_json = self.db.get(bib_id)
            bib = BibliographyPosition.from_json(json.loads(bib_json))

            if bib.title == title and bib.username == username:
                return bib

        return None

    def find_by_id(self, bib_id_to_find, username):
        n = int(self.db.get(BIBLIOGRAPHY_COUNTER))

        for i in range(1, n + 1):
            bib_id = BIBLIOGRAPHY_ID_PREFIX + str(i)

            if not self.db.exists(bib_id):
                continue

            bib_json = self.db.get(bib_id)
            bib = BibliographyPosition.from_json(json.loads(bib_json))

            if bib.id == bib_id_to_find and bib.username == username:
                return bib
        return None

    def count_all(self):
        app.logger.debug("Starting counting all bibs")
        n = int(self.db.get(BIBLIOGRAPHY_COUNTER))

        n_of_bibs = 0

        for i in range(1, n + 1):
            bib_id = BIBLIOGRAPHY_ID_PREFIX + str(i)

            if self.db.exists(bib_id):
                n_of_bibs += 1

        app.logger.debug("Counted all bibs (n: {0})".format(n_of_bibs))
        return n_of_bibs

    def find_n_bibs(self, start, limit, username):
        app.logger.debug("Finding n of bibs (start: {0}, limit: {1}".format(start, limit))
        n = int(self.db.get(BIBLIOGRAPHY_COUNTER))

        bibs = []
        counter = 1

        for i in range(1, n + 1):
            bib_id = BIBLIOGRAPHY_ID_PREFIX + str(i)

            if not self.db.exists(bib_id):
                continue

            if counter < start:
                counter += 1
                continue

            bib_json = self.db.get(bib_id)
            bib = BibliographyPosition.from_json(json.loads(bib_json))
            if bib.username == username:
                bibs.append(bib)

            if len(bibs) >= limit:
                break

        app.logger.debug("Found {0} bibs.".format(len(bibs)))
        return bibs

    def del_bib_by_id(self, bib_id_to_del, username):
        n = int(self.db.get(BIBLIOGRAPHY_COUNTER))

        for i in range(1, n + 1):
            bib_id = BIBLIOGRAPHY_ID_PREFIX + str(i)

            if not self.db.exists(bib_id):
                continue

            bib_json = self.db.get(bib_id)
            bib = BibliographyPosition.from_json(json.loads(bib_json))

            if bib.id == bib_id_to_del and bib.username == username:
                self.db.delete(bib_id)
                return bib.id

        return None
