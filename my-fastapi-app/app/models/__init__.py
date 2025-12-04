from .users import Users, UserRole ,UserStatus        # .users (số nhiều) -> Users (Class)
from .categories import Categories         # .categories (số nhiều) -> Categories (Class)
from .tags import Tags, thread_tags        # .tags (số nhiều) -> Tags (Class)
from .thread import Thread, ThreadMedia    # .thread (số ít)
from .comment import Comment               # .comment (số ít)
from .vote import Vote                     # .vote (số ít)
from ..db.connection import Base
__all__ = [
    "Base",
    "Users", "UserRole","UserStatus",
    "Categories",
    "Tags", "thread_tags",
    "Thread", "ThreadMedia",
    "Comment",
    "Vote"
]