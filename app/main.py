import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from config import settings
from feed.router import api_router
from oauth.middleware import TokenRefreshMiddleware
from oauth.router import auth_router

app = FastAPI(title="Feed social app")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.add_middleware(TokenRefreshMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session_cookie",
    max_age=3600 * 24 * 14,
    same_site="lax",
)

app.include_router(auth_router)
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=81)
