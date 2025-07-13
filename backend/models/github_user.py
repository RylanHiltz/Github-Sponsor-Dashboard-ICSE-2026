from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserModel:
    username: str
    name: str
    type: str
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
    last_scraped: Optional[datetime]
    is_enriched: Optional[bool]

    @classmethod
    def from_api(cls, data: dict):
        return cls(
            username=data["login"],
            name=data["name"],
            type=data["type"],
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
            last_scraped=None,
            is_enriched=None,
        )
