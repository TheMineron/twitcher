from datetime import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base, engine

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(
    server_default=func.now(),
    onupdate=func.now(),
)]
user_fk = Annotated[int, mapped_column(ForeignKey('jwt_auth_customuser.id'))]


class User(Base):
    __tablename__ = 'jwt_auth_customuser'
    __table_args__ = {'autoload_with': engine}

    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str]


class Post(Base):
    __tablename__ = 'socialapp_post'

    id: Mapped[int_pk]
    author_id: Mapped[user_fk]
    content: Mapped[str] = mapped_column(Text())
    image: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    reposted_from_id: Mapped[int | None] = mapped_column(ForeignKey('socialapp_post.id'))

    reposted_from: Mapped['Post'] = relationship(back_populates='reposts', remote_side='Post.id')
    reposts: Mapped[list['Post']] = relationship(back_populates='reposted_from')
    author: Mapped['User'] = relationship('User')
    likes: Mapped[list['Like']] = relationship(back_populates='post')
    comments: Mapped[list['Comment']] = relationship(back_populates='post')


class Like(Base):
    __tablename__ = 'socialapp_like'

    id: Mapped[int_pk]
    user_id: Mapped[user_fk]
    post_id: Mapped[int] = mapped_column(ForeignKey('socialapp_post.id'))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    post: Mapped['Post'] = relationship(back_populates='likes')

class Message(Base):
    __tablename__ = 'socialapp_message'

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey('jwt_auth_customuser.id'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('jwt_auth_customuser.id'))
    content: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_read: Mapped[bool] = mapped_column(default=False)

class Comment(Base):
    __tablename__ = 'socialapp_comment'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('jwt_auth_customuser.id'))
    post_id: Mapped[int] = mapped_column(ForeignKey('socialapp_post.id'))
    content: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now())
    author: Mapped['User'] = relationship('User')

    post: Mapped['Post'] = relationship(back_populates='comments')
