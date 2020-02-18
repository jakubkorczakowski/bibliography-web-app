import json


class User:
    def __init__(self, firstname, lastname, birthdate, pesel, sex, username, password_hash):
        self.firstname = firstname
        self.lastname = lastname
        self.birthdate = birthdate
        self.pesel = pesel
        self.sex = sex
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def from_json(cls, data):
        return cls(**data)
