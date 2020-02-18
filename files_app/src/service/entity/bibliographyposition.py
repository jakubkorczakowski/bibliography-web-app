import json

class BibliographyPosition:
    def __init__(self, id, author_id, title, year, username):
        self.id = id
        self.author_id = author_id
        self.title = title
        self.year = year
        self.username = username

    @classmethod
    def from_json(cls, data):
        return cls(**data)
