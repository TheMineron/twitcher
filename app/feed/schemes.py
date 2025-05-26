from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserScheme(BaseModel):
    id: int
    username: str
    first_name: str | None
    last_name: str | None
    model_config = ConfigDict(from_attributes=True)


class PostBaseScheme(BaseModel):
    author_id: int
    content: str
    image: str | None = None

class PostCreateScheme(PostBaseScheme):
    reposted_from_id: int | None = None

class RepostedPostScheme(PostBaseScheme):
    id: int
    created_at: datetime
    updated_at: datetime
    author: UserScheme
    model_config = ConfigDict(from_attributes=True)

class PostReadScheme(PostBaseScheme):
    id: int
    author: UserScheme
    created_at: datetime
    updated_at: datetime
    likes_count: int
    comments_count: int
    reposts_count: int
    reposted_from: RepostedPostScheme | None = None
    likes: list['LikeScheme']
    model_config = ConfigDict(from_attributes=True)


class CommentScheme(BaseModel):
    id: int
    author: UserScheme
    content: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostDetailScheme(PostReadScheme):
    comments: list[CommentScheme] = []


class LikeScheme(BaseModel):
    post_id: int
    user_id: int

PostReadScheme.model_rebuild()
