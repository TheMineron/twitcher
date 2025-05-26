import httpx
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, JSONResponse

from config import settings


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    SKIP_PATHS = ['/', '/news']
    SKIP_ROUTS = ['/static', '/auth']
    LOGIN_URL = "auth/login"

    async def dispatch(self, request: Request, call_next):
        url = request.url.path
        if any(url.startswith(path) for path in self.SKIP_ROUTS) or request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        access_token = request.session.get("access_token")
        if not access_token:
            return RedirectResponse(url=self.LOGIN_URL)

        try:
            response = await call_next(request)
            if response.status_code != 401:
                return response
            refresh_token = request.session.get("refresh_token")
            if not refresh_token:
                return RedirectResponse(url=self.LOGIN_URL)
            async with httpx.AsyncClient() as client:
                refresh_response = await client.post(
                    settings.ACCESS_TOKEN_URL,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": settings.CLIENT_ID,
                        "client_secret": settings.CLIENT_SECRET_KEY,
                    },
                )
            if refresh_response.status_code != 200:
                return RedirectResponse(url=self.LOGIN_URL)
            tokens = refresh_response.json()
            request.session["access_token"] = access_token
            request.session["refresh_token"] = refresh_token
            request.headers.__dict__["_headers"] = [
                (b"authorization", f"Bearer {tokens['access_token']}".encode())
            ]
            return await call_next(request)

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": str(e)}
            )
