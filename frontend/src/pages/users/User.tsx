import React, { useEffect } from 'react'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import styles from "./User.module.css"
import { Button, Skeleton } from 'antd'
import { apiUrl } from '../../api'
import { Line } from 'react-chartjs-2';

import type { UserModel, YearlyActivityData } from '../../types/UserModel'
import type { ChartData, ChartOptions } from 'chart.js';

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const User: React.FC = () => {

    const { id } = useParams<{ id: string }>();
    const [user, setUser] = useState<UserModel>();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const navigate = useNavigate();

    const [chartData, setChartData] = useState<ChartData<'line'>>({
        labels: [],
        datasets: [],
    });

    const chartOptions: ChartOptions<'line'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
            },
            tooltip: {
                backgroundColor: '#1f2937',
                titleColor: '#e5e7eb',
                bodyColor: '#d1d5db',
                borderColor: '#4b5563',
                borderWidth: 1,
                mode: 'index',
                intersect: false
            },
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Years'
                },
                ticks: { color: '#9ca3af' },
                grid: { color: '#374151' },
            },
            y: {
                ticks: { color: '#9ca3af' },
                grid: { color: '#374151' },
                suggestedMin: 0,
            },
        },
    };

    if (!id) {
        console.log("User ID is missing, cannot fetch data.");
        return;
    }

    const navigateLeaderboard = () => {
        navigate("/");
    };

    const getUserData = async () => {

        try {
            const response = await fetch(`${apiUrl}/api/user/${id}`)
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            setUser(data);
            console.log(data);

            const yearlyActivity = data?.yearly_activity_data;

            let commitLabels: string[] = [];
            let commitData: number[] = [];
            let issuesData: number[] = [];
            let pullRequestsData: number[] = [];
            let codeReviewsData: number[] = [];

            (yearlyActivity ?? []).slice().reverse().forEach((d: YearlyActivityData) => {
                commitLabels.push(d.year.toString());
                commitData.push(d.activity_data.commits);
                issuesData.push(d.activity_data.issues);
                pullRequestsData.push(d.activity_data.pull_requests);
                codeReviewsData.push(d.activity_data.reviews);
            });

            const newChartData = {
                labels: commitLabels,
                datasets: [
                    {
                        label: 'Commits',
                        data: commitData,
                        borderColor: '#A855F7', // Purple
                        backgroundColor: 'rgba(168, 85, 247, 0.2)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#A855F7',
                        pointRadius: 3,
                    },
                    {
                        label: 'Issues',
                        data: issuesData,
                        borderColor: '#EC4899', // Pink
                        backgroundColor: 'rgba(236, 72, 153, 0.2)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#EC4899',
                        pointRadius: 3,
                    },
                    {
                        label: 'Pull Requests',
                        data: pullRequestsData,
                        borderColor: '#22D3EE', // Cyan
                        backgroundColor: 'rgba(34, 211, 238, 0.2)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#22D3EE',
                        pointRadius: 3,
                    },
                    {
                        label: 'Code Reviews',
                        data: codeReviewsData,
                        borderColor: '#60A5FA', // Blue
                        backgroundColor: 'rgba(96, 165, 250, 0.2)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#60A5FA',
                        pointRadius: 3,
                    },
                ],
            };
            console.log(newChartData);
            setChartData(newChartData);

        } catch (error) {
            console.log(error)
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        getUserData();
    }, [id]);

    return (
        <>

            <div className='h-full'>
                <div className="flex flex-col h-full px-5 gap-5">
                    <Button className='w-min' type='text' onClick={navigateLeaderboard}> Back To Dashboard</Button>
                    <section className='flex-grow grid grid-cols-[_2fr,34em] grid-rows-[_3fr,_3fr] gap-5'>
                        <div className={`${styles.profileCard} row-span-1 flex flex-col justify-between`}>
                            <div className='flex flex-col gap-3'>
                                <div className='flex items-center gap-4'>
                                    {isLoading == false ? (
                                        <img src={user?.avatar_url} alt="user profile image" className='w-[5em] h-[5em] rounded-full' />
                                    ) :
                                        (
                                            <Skeleton />
                                        )}
                                    <div>
                                        {user?.name ? (
                                            <span className='flex items-center gap-2'>
                                                <h1 className='text-2xl font-semibold'>{user.name}</h1>
                                            </span>
                                        ) : (
                                            <span className='flex items-center gap-2'>
                                                <h1 className='text-2xl font-semibold'>{user?.username}</h1>
                                            </span>
                                        )}
                                        <p className='text-lg font-light text-gray-400'>{user?.username}</p>
                                    </div>
                                </div>

                                {user?.bio && <p className='text-gray-300 text-base'>{user?.bio}</p>}

                                <div className='flex flex-col gap-1 text-gray-300 mt-2'>
                                    {user?.company && (
                                        <span className='flex items-center gap-2'>
                                            <p>Company</p>
                                            <p className='font-medium'>{user.company}</p>
                                        </span>
                                    )}
                                    {user?.location && (
                                        <span className='flex items-center gap-2'>
                                            <p>Location: </p>
                                            <p className='font-medium'>{user.location}</p>
                                        </span>
                                    )}
                                    {user?.email && (
                                        <span className='flex items-center gap-2'>
                                            <p>Email: </p>
                                            <a href={`mailto:${user.email}`} className='hover:underline'>{user.email}</a>
                                        </span>
                                    )}
                                    {user?.profile_url && (
                                        <span className='flex items-center gap-2'>
                                            <p>Github: </p>
                                            <a href={`${user.profile_url}`}>{user?.username}</a>
                                        </span>
                                    )}
                                    {user?.twitter_username && (
                                        <span className='flex items-center gap-2'>
                                            <p>Twitter: </p>
                                            <a href={`https:twitter.com/${user.twitter_username}`}>{user.twitter_username}</a>
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div className='flex gap-4 text-base text-gray-300 justify-between'>
                                <div className='flex gap-2'>
                                    <span><span className='font-bold text-white'>{user?.followers}</span> followers</span>
                                    <span>·</span>
                                    <span><span className='font-bold text-white'>{user?.following}</span> following</span>
                                </div>
                                <Button className='font-bold text-white' href={user?.profile_url} target='_blank' type='link'>Visit Profile</Button>
                            </div>
                        </div>


                        <div className={`${styles.profileCard} row-span-3`}>
                            <div className='flex flex-col gap-5'>
                                <div className='flex flex-col gap-3 flex-grow'>
                                    <h2 className="text-xl font-semibold">User Activity Statistics</h2>
                                    <div className='grid grid-cols-2 gap-5 grow'>
                                        {([
                                            {
                                                label: "Total Commits", value: user?.total_commits, color: {
                                                    bg: 'rgba(168, 85, 247, 0.2)', border: '#A855F7', text: '#A855F7',
                                                }
                                            },
                                            {
                                                label: "Total Issues", value: user?.total_issues, color: {
                                                    bg: 'rgba(236, 72, 153, 0.2)', border: '#EC4899', text: '#EC4899',
                                                }
                                            },
                                            {
                                                label: "Total PRs", value: user?.total_pull_requests, color: {
                                                    bg: 'rgba(34, 211, 238, 0.2)', border: '#22D3EE', text: '#22D3EE',
                                                }
                                            },
                                            {
                                                label: "Total Reviews", value: user?.total_reviews, color: {
                                                    bg: 'rgba(96, 165, 250, 0.2)', border: '#60A5FA', text: '#60A5FA',
                                                }
                                            },
                                        ]).map((stat, index) => (
                                            <div
                                                key={index}
                                                className="p-4 rounded-xl flex flex-col justify-center items-center text-center"
                                                style={{
                                                    backgroundColor: stat.color.bg,
                                                    // border: `1.5px solid ${stat.color.border}`
                                                }}
                                            >
                                                <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                                                {isLoading ? (
                                                    <Skeleton.Input active={true} size="small" />
                                                ) : (
                                                    <p
                                                        className="text-xl font-bold"
                                                        style={{ color: stat.color.text }}
                                                    >
                                                        {stat.value?.toLocaleString() ?? 'N/A'}
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className='flex flex-col gap-3'>
                                    <h2 className="text-xl font-semibold">Sponsorship Statistics</h2>
                                    <div className='grid grid-cols-2 gap-5 grow'>
                                        {([
                                            { label: "Total User Sponsors", value: user?.total_sponsors },
                                            { label: "Total Users Sponsoring", value: user?.total_sponsoring },
                                            { label: "Private Sponsors", value: user?.private_sponsor_count },
                                            { label: "Minimum Sponsor Tier", value: user?.min_sponsor_cost },
                                        ]).map((stat, index) => (
                                            <div key={index} className="bg-[#262626] p-4 rounded-xl flex flex-col justify-center items-center text-center">
                                                <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                                                {isLoading ? (
                                                    <Skeleton.Input active={true} size="small" />
                                                ) : (
                                                    <p className="text-xl font-bold">
                                                        {stat.value != null ?
                                                            (stat.label === "Minimum Sponsor Tier" ? `$${stat.value.toLocaleString()}.00` : stat.value.toLocaleString())
                                                            : 'N/A'
                                                        }
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className='flex flex-col gap-3 flex-grow'>
                                    <h2 className="text-xl font-semibold">{user?.type} Account Statistics</h2>
                                    <div className='grid grid-cols-2 gap-5 grow'>
                                        {([
                                            { label: "Total Repos", value: user?.public_repos },
                                            { label: "Total Gists", value: user?.public_gists },
                                        ]).map((stat, index) => (
                                            <div key={index} className="bg-[#262626] p-4 rounded-xl flex flex-col justify-center items-center text-center">
                                                <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                                                {isLoading ? (
                                                    <Skeleton.Input active={true} size="small" />
                                                ) : (
                                                    <p className="text-xl font-bold">{stat.value?.toLocaleString() ?? 'N/A'}</p>
                                                )}
                                            </div>
                                        ))}
                                        {([
                                            { label: "Account Created", value: user?.github_created_at },
                                            { label: "Last Checked", value: user?.last_scraped },
                                        ]).map((stat, index) => (
                                            <div key={index} className="bg-[#262626] p-4 rounded-xl flex flex-col justify-center items-center text-center">
                                                <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                                                {isLoading ? (
                                                    <Skeleton.Input active={true} size="small" />
                                                ) : (
                                                    <p className="text-xl font-bold">
                                                        {stat.value ? new Date(stat.value).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A'}
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>


                            </div>
                        </div>
                        <div className={`${styles.profileCard} row-span-2 flex flex-col gap-5 p-5 h-full`}>
                            <h2 className="text-xl font-semibold">Visualized User Activity</h2>
                            <div className='relative flex-grow'>
                                {isLoading ? (
                                    <Skeleton active />
                                ) : (
                                    <Line options={chartOptions} data={chartData} />
                                )}
                            </div>
                        </div>

                    </section>
                </div >
            </div >
        </>
    )
}

export default User