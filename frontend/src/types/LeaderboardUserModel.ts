
export interface LeaderboardUser {
    id: number;
    name: string;
    username: string;
    type: string;
    gender: string;
    hireable: boolean;
    location: string;
    avatar_url: string;
    profile_url: string;
    following: number;
    followers: number;
    public_repos: number;
    public_gists: number;
    total_sponsors: number;
    total_sponsoring: number;
    min_sponsor_cost: number;
    estimated_earnings: number;
}

export interface Location {
    text: string;
    value: string;
}

export interface LeaderboardStatsData {
    total_users: number;
    total_sponsorships: number;
    top_sponsored: {
        username: string;
        avatar_url: string;
        total_sponsors: number;
    };
    top_sponsoring: {
        username: string;
        avatar_url: string;
        total_sponsoring: number;
    };
}