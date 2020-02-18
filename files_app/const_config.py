import os

OAUTH_BASE_URL = "https://dev-jakubkor.eu.auth0.com"
OAUTH_ACCESS_TOKEN_URL = OAUTH_BASE_URL + "/oauth/token"
OAUTH_AUTHORIZE_URL = OAUTH_BASE_URL + "/authorize"
OAUTH_CALLBACK_URL = "https://localhost:8080/callback"
OAUTH_CLIENT_ID = "e6VrlKC76saMKUVGAZfEEZ9erF8j8SrA"
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")
OAUTH_SCOPE = "openid profile"
SECRET_KEY = os.environ.get("FLASK_SECRET")
