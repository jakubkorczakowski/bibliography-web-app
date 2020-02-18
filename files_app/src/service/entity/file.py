import json


class File:
    def __init__(self, id, new_filename, org_filename, path_to_file, date, username, bib_id):
        self.id = id
        self.new_filename = new_filename
        self.org_filename = org_filename
        self.path_to_file = path_to_file
        self.date = date
        self.username = username
        self.bib_id = bib_id

    @classmethod
    def from_json(cls, data):
        return cls(**data)
