import os
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import HTTPException, UploadFile, APIRouter
from fastapi.params import Depends, File, Form
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from feed.crud import (
    get_user_posts,
    get_posts,
    get_post_with_comments,
    create_post,
    create_comment,
    create_like,
    delete_like
)
from feed.dependencies import get_session
from feed.schemes import UserScheme
from models import User, Post
from oauth.dependencies import get_current_user

api_router = APIRouter(prefix="")
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "media/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@api_router.get('/')
async def index(request: Request, user=Depends(get_current_user)):
    return RedirectResponse(url="/news")


@api_router.get('/news')
async def news(
        request: Request,
        user: Annotated[UserScheme, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    posts = get_posts(session)
    return templates.TemplateResponse(
        "news.html",
        {
            "request": request,
            'user': user,
            'profile_owner': user,
            'posts': posts
        },
    )


@api_router.get('/feed/me')
async def my_posts(
        request: Request,
        user: Annotated[UserScheme, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    posts = get_user_posts(session, user.id)
    return templates.TemplateResponse(
        "feed.html",
        {
            "request": request,
            'user': user,
            'profile_owner': user,
            'posts': posts,
            'is_own_feed': True
        },
    )


@api_router.get('/feed/user/{user_id}')
async def user_posts(
        request: Request,
        user_id: int,
        user: Annotated[UserScheme, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    posts = get_user_posts(session, user_id)
    profile_owner = session.get(User, user_id)
    if not profile_owner:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "feed.html",
        {
            "request": request,
            'user': user,
            'profile_owner': UserScheme.model_validate(profile_owner),
            'posts': posts,
            'is_own_feed': (user.id == user_id)
        },
    )


@api_router.get('/posts/{post_id}')
async def get_post_detail(
        request: Request,
        post_id: int,
        user: Annotated[UserScheme, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    post = get_post_with_comments(session, post_id)

    return templates.TemplateResponse(
        "post_detail.html",
        {
            "request": request,
            'user': user,
            'post': post,
            'comments': post.comments,
            'is_owner': (user.id == post.author_id)
        },
    )


@api_router.post("/posts")
async def make_post(
        request: Request,
        content: str = Form(...),
        original_post_id: int = Form(None),
        image: UploadFile = File(None),
        user: UserScheme = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    image_path = None
    if image and image.filename:
        file_ext = Path(image.filename).suffix
        file_name = f"{uuid.uuid4()}{file_ext}"
        image_path = f"{UPLOAD_DIR}/{file_name}"

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    create_post(
        session=session,
        author_id=user.id,
        content=content,
        image=f"/{image_path}" if image_path else None,
        reposted_from_id=original_post_id
    )

    return RedirectResponse(url=request.headers.get('referer', '/feed/me'), status_code=303)


@api_router.post("/posts/{post_id}/comments")
async def make_comment(
        request: Request,
        post_id: int,
        content: str = Form(...),
        user: UserScheme = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    create_comment(
        session=session,
        post_id=post_id,
        content=content,
        author_id=user.id,
    )
    return RedirectResponse(url=request.headers.get('referer', f"/posts/{post_id}"), status_code=303)


@api_router.post("/posts/{post_id}/likes")
async def make_like(
        request: Request,
        post_id: int,
        user: UserScheme = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    create_like(
        session=session,
        post_id=post_id,
        sender_id=user.id
    )

    post = session.get(Post, post_id)
    return JSONResponse({
        "success": True,
        "new_count": len(post.likes)
    })


@api_router.delete("/posts/{post_id}/likes")
async def remove_like(
        request: Request,
        post_id: int,
        user: UserScheme = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    delete_like(
        session=session,
        post_id=post_id,
        sender_id=user.id
    )

    post = session.get(Post, post_id)
    return JSONResponse({
        "success": True,
        "new_count": len(post.likes)
    })
