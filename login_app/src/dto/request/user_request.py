class UserRequest:
    def __init__(self, reqest):
        self.firstname = reqest.json["firstname"]
        self.lastname = reqest.json["lastname"]
        self.birthdate = reqest.json["birthdate"]
        self.pesel = reqest.json["pesel"]
        self.sex = reqest.json["sex"]
        self.username = reqest.json["username"]
        self.password = reqest.json["password"]

    def __str__(self):
        return "firstname: {0}, lastname: {1}, birthdate: {2}, pesel: {3}, sex: {4}, username: {5}, password: {6}" \
            .format(self.firstname, self.lastname, self.birthdate, self.pesel, self.sex, self.username, self.password)
