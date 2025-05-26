from models import Post
from feed.schemes import PostReadScheme, UserScheme, RepostedPostScheme, LikeScheme


def map_post(post: Post, reposts_count: int) -> PostReadScheme:
    return PostReadScheme(
        id=post.id,
        author_id=post.author_id,
        author=UserScheme.model_validate(post.author),
        content=post.content,
        image=post.image,
        created_at=post.created_at,
        updated_at=post.updated_at,
        likes_count=len(post.likes),
        comments_count=len(post.comments),
        likes=[LikeScheme(post_id=like.post_id, user_id=like.user_id) for like in post.likes],
        reposts_count=reposts_count,
        reposted_from=(
            RepostedPostScheme(
                id=post.reposted_from.id,
                author_id=post.reposted_from.author_id,
                content=post.reposted_from.content,
                image=post.reposted_from.image,
                created_at=post.reposted_from.created_at,
                updated_at=post.reposted_from.updated_at,
                author=UserScheme.model_validate(post.reposted_from.author)
            ) if post.reposted_from else None
        )
    )
