from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserModel:
    github_id: int
    username: str
    name: str
    type: str
    has_pronouns: bool
    gender: Optional[str]
    location: Optional[str]
    avatar_url: str
    profile_url: str
    company: Optional[str]
    following: int
    followers: int
    hireable: Optional[bool]
    bio: Optional[str]
    public_repos: int
    public_gists: int
    twitter_username: Optional[str]
    email: Optional[str]
    private_sponsor_count: int
    last_scraped: Optional[datetime]
    is_enriched: Optional[bool]
    github_created_at: datetime

    @classmethod
    def from_api(cls, data: dict):
        return cls(
            github_id=data["id"],
            username=data["login"],
            name=data["name"],
            type=data["type"],
            has_pronouns=data.get("has_pronouns", False),
            gender=None,
            location=data["location"],
            avatar_url=data["avatar_url"],
            profile_url=data["html_url"],
            company=data.get("company"),
            following=data["following"],
            followers=data["followers"],
            hireable=data.get("hireable"),
            bio=data.get("bio"),
            public_repos=data["public_repos"],
            public_gists=data["public_gists"],
            twitter_username=data.get("twitter_username"),
            email=data.get("email"),
            private_sponsor_count=0,
            last_scraped=None,
            is_enriched=None,
            github_created_at=data["created_at"],
        )
