from typing import Literal

import httpx

from config import settings


async def revoke_token(token, token_type: Literal['access', 'refresh']) -> None:
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                settings.REVOKE_TOKEN_URL,
                data={
                    "token": token,
                    "token_type_hint": f"{token_type}_token",
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET_KEY,
                },
            )
        except Exception as e:
            print(f"Error revoking access token: {e}")
