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
            github_id=data["databaseId"],
            username=data["login"],
            name=data["name"],
            type=data["__typename"],
            has_pronouns=data.get("has_pronouns", False),
            gender=None,
            location=data["location"],
            avatar_url=data["avatarUrl"],
            profile_url=data["url"],
            company=data.get("company"),
            following=data["following"]["totalCount"],
            followers=data["followers"]["totalCount"],
            hireable=data.get("isHireable"),
            bio=data.get("bio"),
            public_repos=(
                data["originalRepositories"]["totalCount"]
                + data["forkedRepositories"]["totalCount"]
            ),
            public_gists=data["gists"]["totalCount"],
            twitter_username=data.get("twitterUsername"),
            email=data.get("email"),
            private_sponsor_count=0,
            last_scraped=None,
            is_enriched=None,
            github_created_at=data["createdAt"],
        )
