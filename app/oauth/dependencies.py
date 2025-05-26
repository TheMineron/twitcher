import httpx
from fastapi import HTTPException, Request

from config import settings
from app.oauth.schemes import UserScheme


async def get_current_user(request: Request) -> UserScheme | None:
    user_data = request.session.get('user_data')

    if not user_data:
        access_token = request.session.get('access_token')
        if not access_token:
            return None
        async with httpx.AsyncClient() as client:
            userinfo = await client.get(
                settings.USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if userinfo.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")

        request.session["user_data"] = userinfo.json()

    return UserScheme(**user_data)
