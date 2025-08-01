export interface UserModel {
    id: number;
    github_id: number;
    username: string;
    name: string;
    type: string;
    has_pronouns: boolean;
    gender: string | null;
    location: string | null;
    avatar_url: string;
    profile_url: string;
    company: string | null;
    following: number;
    followers: number;
    hireable: boolean | null;
    bio: string | null;
    public_repos: number;
    public_gists: number;
    email: string | null;
    twitter_username: string | null;
    private_sponsor_count: number;
    created_at: string; 
    last_scraped: string; 
    is_enriched: boolean;
    total_sponsoring: number;
    total_sponsors: number;
    yearly_activity_data: YearlyActivityData[] | null;
    github_created_at: string;
    min_sponsor_cost: number | null;
    total_commits: number;
    total_issues: number;
    total_pull_requests: number;
    total_reviews: number;
}

export interface YearlyActivityData {
    activity_data: {
        commits: number;
        issues: number;
        pull_requests: number;
        reviews: number;
    };
    year: number;
}
