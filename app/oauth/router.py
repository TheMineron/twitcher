import secrets

from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from config import settings
from oauth.oauth import oauth
from oauth.helpers import revoke_token

auth_router = APIRouter(prefix="/auth")


@auth_router.get("/login")
async def login(request: Request):
    request.session.clear()
    code_verifier = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(16)

    request.session["oauth_state"] = state
    request.session["code_verifier"] = code_verifier

    redirect_uri = request.url_for('callback')
    auth_url = await oauth.default.authorize_redirect(
        request,
        redirect_uri,
        state=state,
        code_verifier=code_verifier
    )

    return auth_url


@auth_router.get("/callback", name="callback")
async def callback(request: Request):
    state = request.query_params.get('state')
    if state != request.session.get("oauth_state"):
        raise HTTPException(status_code=400, detail="Invalid state")

    try:
        token = await oauth.default.authorize_access_token(
            request
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    request.session["access_token"] = token["access_token"]
    if 'refresh_token' in token:
        request.session["refresh_token"] = token["refresh_token"]

    try:
        resp = await oauth.default.get(settings.USERINFO_URL, token=token)
        userinfo = resp.json()
        request.session["user_data"] = userinfo
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch user info: {str(e)}")

    return RedirectResponse(url="/", status_code=302)


@auth_router.get("/logout")
async def logout(request: Request):
    access_token = request.session.get("access_token")
    refresh_token = request.session.get("refresh_token")

    if access_token:
        await revoke_token(access_token, 'access')

    if refresh_token:
        await revoke_token(refresh_token, 'refresh')

    request.session.clear()
    return RedirectResponse(url="/")
