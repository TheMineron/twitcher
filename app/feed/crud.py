from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload, selectinload

from feed.mappers import map_post
from models import Post, Comment, Like
from feed.schemes import PostReadScheme, UserScheme, PostDetailScheme, CommentScheme


def get_posts(session: Session) -> list[PostReadScheme]:
    query = (
        select(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.reposted_from).joinedload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .order_by(Post.created_at.desc())
    )
    return _process_posts_query(session, query)


def get_user_posts(session: Session, user_id: int) -> list[PostReadScheme]:
    query = (
        select(Post)
        .where(Post.author_id == user_id)
        .options(
            joinedload(Post.author),
            joinedload(Post.reposted_from).joinedload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .order_by(Post.created_at.desc())
    )
    return _process_posts_query(session, query)


def _process_posts_query(session: Session, query) -> list[PostReadScheme]:
    result = session.execute(query)
    posts = result.unique().scalars().all()

    return [
        map_post(post, get_reposts_count(session, post.id))
        for post in posts
    ]


def get_reposts_count(session: Session, post_id: int) -> int:
    count = session.scalar(
        select(func.count())
        .select_from(Post)
        .where(Post.reposted_from_id == post_id)
    )
    return count or 0


def get_likes_count(session: Session, post_id: int) -> int:
    count = session.scalar(
        select(func.count())
        .select_from(Like)
        .where(Like.post_id == post_id)
    )
    return count or 0


def get_comments_count(session: Session, post_id: int) -> int:
    count = session.scalar(
        select(func.count())
        .select_from(Comment)
        .where(Comment.post_id == post_id)
    )
    return count or 0


def get_post_with_comments(session: Session, post_id: int):
    query = (
        select(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.reposted_from).joinedload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments).joinedload(Comment.author)
        )
        .filter_by(id=post_id)
    )
    result = session.execute(query)
    post = result.unique().scalars().first()

    comments_schemes = [CommentScheme(
        id=comment.id,
        author=UserScheme.model_validate(comment.author),
        content=comment.content,
        created_at=comment.created_at
    ) for comment in sorted(post.comments, key=lambda post: post.created_at, reverse=True)]
    post_scheme = map_post(post, get_reposts_count(session, post.id))
    return PostDetailScheme(
        **post_scheme.model_dump(),
        comments=comments_schemes
    )


def create_post(
        session: Session,
        author_id: int,
        content: str,
        image: str = None,
        reposted_from_id: int = None
) -> PostReadScheme:
    post = Post(
        author_id=author_id,
        content=content,
        image=image,
        reposted_from_id=reposted_from_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(post)
    session.commit()
    session.refresh(post)

    return map_post(post, 0)


def create_comment(session: Session, post_id: int, author_id: int, content: str):
    comment = Comment(
        post_id=post_id,
        author_id=author_id,
        content=content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(comment)
    session.commit()
    return comment


def create_like(session: Session, post_id: int, sender_id: int):
    like = Like(
        post_id=post_id,
        user_id=sender_id,
        created_at=datetime.utcnow(),
    )

    session.add(like)
    session.commit()


def delete_like(session: Session, post_id: int, sender_id: int):
    like = session.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == sender_id
    ).first()

    if like:
        session.delete(like)
        session.commit()