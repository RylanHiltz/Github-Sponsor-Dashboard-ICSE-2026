import React, { useEffect } from 'react'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import styles from "./User.module.css"
import { Button, Skeleton, theme } from 'antd'
import { apiUrl } from '../../api'
import { Line } from 'react-chartjs-2';
import { IoChevronBackOutline } from "react-icons/io5";

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

    const { token } = theme.useToken();
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
                labels: {
                    color: token.colorTextSecondary
                }
            },
            tooltip: {
                backgroundColor: '#1f2937',
                titleColor: '#e5e7eb',
                bodyColor: '#fff',
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
                    text: 'Years Since Account Creation'
                },
                ticks: { color: '#9ca3af' },
                grid: { color: token.gridColor },
            },
            y: {
                ticks: { color: '#9ca3af' },
                grid: { color: token.gridColor },
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
            const response = await fetch(`${apiUrl}/user/${id}`)
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

            const newChartData: ChartData<'line'> = {
                labels: commitLabels,
                datasets: [
                    {
                        label: 'Commits',
                        data: commitData,
                        borderColor: '#A855F7', // Purple
                        backgroundColor: 'rgba(168, 85, 247, 0.2)',
                        fill: true,
                        tension: 0.5,
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
                    <Button className='w-min' type='text' onClick={navigateLeaderboard}><IoChevronBackOutline /> Back To Dashboard</Button>
                    <section className='flex-grow grid grid-cols-[_2fr,30em] grid-rows-[_3fr,_3fr] gap-5'>
                        <div className={`${styles.profileCard} row-span-1 flex flex-col justify-between border-solid]`} style={{ borderColor: token.colorBorder }}>
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

                                {user?.bio && <p className='text-base'>{user?.bio}</p>}

                                <div className='flex flex-col gap-1  mt-2'>
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
                            <div className='flex gap-4 text-base justify-between'>
                                <div className='flex gap-2'>
                                    <span><span className='font-bold '>{user?.followers}</span> followers</span>
                                    <span>·</span>
                                    <span><span className='font-bold '>{user?.following}</span> following</span>
                                </div>
                                <Button className='font-bold ' href={user?.profile_url} target='_blank' type='link'>Visit Profile</Button>
                            </div>
                        </div>


                        {/*  */}
                        <div className={`${styles.profileCard} row-span-3 p-6`} style={{ borderColor: token.colorBorder }}>
                            <div className="flex flex-col h-full gap-5 justify-evenly">
                                {(() => {
                                    const StatRow = ({ label, value, format }: { label: string, value: any, format?: 'currency' | 'date' | 'number' }) => {
                                        let displayValue = 'N/A';
                                        if (value != null) {
                                            switch (format) {
                                                case 'currency':
                                                    displayValue = `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                                                    break;
                                                case 'date':
                                                    displayValue = new Date(value).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
                                                    break;
                                                default:
                                                    displayValue = value.toLocaleString();
                                            }
                                        }

                                        return (
                                            <div className="flex justify-between items-center py-2.5 border-b border-[#434343] last:border-b-0">
                                                <p className="text-gray-400 text-sm">{label}</p>
                                                {isLoading ? (
                                                    <Skeleton.Input active={true} size="small" style={{ width: 100 }} />
                                                ) : (
                                                    <p className="text-base font-semibold ">{displayValue}</p>
                                                )}
                                            </div>
                                        );
                                    };

                                    return (
                                        <>
                                            <div>
                                                <h2 className="text-lg font-semibold  mb-2">User Activity</h2>
                                                <div className="rounded-lg pl-4">
                                                    <StatRow label="Total Commits" value={user?.total_commits} />
                                                    <StatRow label="Total Issues" value={user?.total_issues} />
                                                    <StatRow label="Total Pull Requests" value={user?.total_pull_requests} />
                                                    <StatRow label="Total Code Reviews" value={user?.total_reviews} />
                                                </div>
                                            </div>

                                            <div>
                                                <h2 className="text-lg font-semibold  mb-2">Sponsorships</h2>
                                                <div className="rounded-lg pl-4">
                                                    <StatRow label="Sponsors" value={user?.total_sponsors} />
                                                    <StatRow label="Sponsoring" value={user?.total_sponsoring} />
                                                    <StatRow label="Minimum Tier" value={user?.min_sponsor_cost} format="currency" />
                                                    <StatRow label="Est. Min Earnings" value={null} format="currency" />
                                                </div>
                                            </div>

                                            <div>
                                                <h2 className="text-lg font-semibold mb-2">Account Data</h2>
                                                <div className="rounded-lg pl-4">
                                                    <StatRow label="Public Repositories" value={user?.public_repos} />
                                                    <StatRow label="Public Gists" value={user?.public_gists} />
                                                    <StatRow label="Account Created" value={user?.github_created_at} format="date" />
                                                    <StatRow label="Last Checked" value={user?.last_scraped} format="date" />
                                                </div>
                                            </div>
                                        </>
                                    );
                                })()}
                            </div>
                        </div>

                        {/* Visualized user activity graph section */}
                        <div className={`${styles.profileCard} row-span-2 flex flex-col gap-5 p-5 h-full`} style={{ borderColor: token.colorBorder }}>
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