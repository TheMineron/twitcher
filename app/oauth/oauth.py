from authlib.integrations.starlette_client import OAuth

from config import settings

oauth = OAuth()

oauth.register(
    name='default',
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET_KEY,
    authorize_url=settings.AUTHORIZE_URL,
    access_token_url=settings.ACCESS_TOKEN_URL,
    client_kwargs={
        'scope': 'read write',
        'code_challenge_method': 'S256',
    },
)
print(dir(oauth.default))