from flask import Flask
from src.service.repositories.user_repository import UserRepository
from src.exception.exception import UserNotFoundByUsernameException
from src.exception.exception import UserPasswordIsInvalidException
import hashlib

app = Flask(__name__)


class UserService:

    def __init__(self):
        self.user_repo = UserRepository()

    def add_user(self, user_req):
        app.logger.debug("Adding user...")
        user_username = self.user_repo.save(user_req)
        app.logger.debug("Added user (username: {0})".format(user_username))
        return user_username

    def get_user_by_username(self, user_username):
        app.logger.debug("Getting user by username: {0}.".format(user_username))
        user = self.user_repo.find_by_username(user_username)

        if user == None:
            raise UserNotFoundByUsernameException("Not found user by username: {0}".format(user_username))

        app.logger.debug("Got user by username: {0}".format(user_username))
        return user

    def del_user_by_username(self, user_username_to_del):
        app.logger.debug("Deleting user...")
        user_username = self.user_repo.del_user_by_username(user_username_to_del)

        if user_username == None:
            raise UserNotFoundByUsernameException("Not found user by username: {0}".format(user_username))

        app.logger.debug("Deleted user (username: {0})".format(user_username))
        return user_username

    def get_user_by_username_and_password(self, user_username_to_check, user_password_to_check):
        app.logger.debug("Checking user with username: {0} password.".format(user_username_to_check))
        user = self.get_user_by_username(user_username_to_check)

        password_to_check = user_password_to_check.encode("utf-8")
        password_to_check_hash = hashlib.sha512(password_to_check).hexdigest()

        if password_to_check_hash != user.password_hash:
            raise UserPasswordIsInvalidException("User: {0} password is invalid.".format(user_username_to_check))

        app.logger.debug("Checked user with username: {0} password.".format(user_username_to_check))
        return user
