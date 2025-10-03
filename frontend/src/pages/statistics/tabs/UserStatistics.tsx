import { useState } from "react";
import { theme, Skeleton } from "antd";
import styles from "../Statistics.module.css"
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { apiUrl } from "../../../api";
import { Bar, Doughnut } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';


import type { ChartData, ChartOptions } from "chart.js";
// import { MdOutlineExpandMore } from "react-icons/md";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
);


const UserStatsPage = ({ playSignal }: { playSignal: number }) => {

    interface BriefStats {
        most_sponsored_user: {
            avatar_url: string;
            total_sponsors: number;
            username: string;
        },
        most_sponsoring_user: {
            avatar_url: string;
            total_sponsors: number;
            username: string;
        },
        top_country: {
            country: string;
            sponsored_users: number;
        },
        total_users: number;
    }

    const [briefData, setBriefData] = useState<BriefStats>();
    const [isLoading, setIsLoading] = useState(true);

    const getBrief = async () => {

        try {
            const response = await fetch(`${apiUrl}/brief-user-stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json() as BriefStats;
            console.log(data)
            setBriefData(data);
        } catch (error) {
            console.log(error);
        }
        finally {
            setIsLoading(false);
        }
    }

    const containerRef = useRef<HTMLDivElement>(null);
    const { token } = theme.useToken();
    useEffect(() => {
        const ctx = gsap.context(() => {
            gsap.from(`.${styles.Card}`, {
                opacity: 0,
                y: 24,
                scale: 0.98,
                duration: 0.6,
                ease: "power2.out",
                stagger: 0.08,
            });
        }, containerRef);
        return () => ctx.revert();
    }, [playSignal]);

    useEffect(() => {
        getBrief();
    }, []);

    return (
        <>
            <section className="h-full flex flex-col min-h-0 overflow-hidden">
                {/* <div>
                    <Button type="text" className="flex items-center" >Advanced Statistics <MdOutlineExpandMore className="text-[20px]" /></Button>
                </div> */}
                <div
                    ref={containerRef}
                    className="
                    flex-1 min-h-0 h-full
                    grid gap-4 pt-2.5 pb-2
                    grid-cols-1 sm:grid-cols-2 md:grid-cols-6 xl:grid-cols-12
                    auto-rows-[minmax(120px,auto)] sm:auto-rows-[minmax(140px,auto)] md:auto-rows-fr xl:auto-rows-fr
                    overflow-y-auto md:overflow-hidden
                    "
                >
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0 p-0 overflow-y-hidden`}
                    >
                        {isLoading ? (
                            <Skeleton active />
                        ) : (
                            <>
                                <h1 className="font-medium">Total Tracked Users</h1>
                                <h2 style={{ color: token.colorTextSecondary }}>{briefData?.total_users}</h2>
                            </>
                        )}
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0 overflow-y-hidden`}
                    >
                        {isLoading ? (
                            <Skeleton active />
                        ) : (
                            <>
                                <h1 className="font-medium">Most Sponsored User</h1>
                                <span className='flex items-center justify-start gap-2'>
                                    <img src={briefData?.most_sponsored_user.avatar_url} alt={briefData?.most_sponsored_user.username} className='w-8 h-8 rounded-full' />
                                    <h2 style={{ color: token.colorTextSecondary }} className='pb-1 text-[18px] font-semibold'>{briefData?.most_sponsored_user.username}</h2>
                                </span>
                            </>
                        )}
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0 overflow-y-hidden`}
                    >
                        {isLoading ? (
                            <Skeleton active />
                        ) : (
                            <>
                                <h1 className="font-medium">Most Sponsoring User</h1>
                                <span className='flex items-center justify-start gap-2'>
                                    <img src={briefData?.most_sponsoring_user.avatar_url} alt={briefData?.most_sponsoring_user.username} className='w-8 h-8 rounded-full' />
                                    <h2 style={{ color: token.colorTextSecondary }} className='pb-1 text-[18px] font-semibold'>{briefData?.most_sponsoring_user.username}</h2>
                                </span>
                            </>
                        )}
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0 overflow-y-hidden`}
                    >
                        {isLoading ? (
                            <Skeleton active />
                        ) : (
                            <>
                                <h1 className="font-medium">Most Sponsored Country</h1>
                                <span className="flex gap-2 text-center items-center">
                                    <h2 style={{ color: token.colorTextSecondary }}>{briefData?.top_country.country}</h2>
                                    <span>·</span>
                                    <p style={{ color: token.colorTextSecondary }} className="text-[14px] font-semibold pt-0.5">{briefData?.top_country.sponsored_users} Users</p>
                                </span>
                            </>
                        )}
                    </div>

                    {/* Largest graph */}
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-4 xl:col-span-8 row-span-2 md:row-span-4 xl:row-span-6`}
                    >
                        <LocationDistributionGraph />
                    </div>

                    {/* Right-side graphs */}
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-2 xl:col-span-4 row-span-2 md:row-span-2 xl:row-span-3`}
                    >
                        <GenderDataGraph />
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-2 xl:col-span-4 row-span-2 md:row-span-2 xl:row-span-3`}
                    >
                        <SponsorshipsGraph />
                    </div>
                </div>
            </section>
        </>
    );
}
export default UserStatsPage;


// Graph foor location/gender distribution of sponsored devs
const LocationDistributionGraph = () => {

    // Interface for api 
    interface userLocations {
        country: string;
        genderData: {
            male: number;
            female: number;
            other: number;
            unknown: number;
        }
    }
    const { token } = theme.useToken();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [locationChartData, setLocationChartData] = useState<ChartData<'bar'>>({
        labels: [],
        datasets: [],
    });


    const chartOptions: ChartOptions<'bar'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: "top",
                align: "start",
                labels: {
                    color: token.colorTextSecondary,
                    usePointStyle: false,
                    padding: 3.5,
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
                stacked: true,
            },
            y: {
                stacked: true
            }
        }
    };

    const getGenderData = async () => {
        try {
            const response = await fetch(`${apiUrl}/user-stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const raw = await response.json();
            const users = Array.isArray(raw) ? (raw as userLocations[]) : [];

            const labels: string[] = [];
            const maleData: number[] = [];
            const femaleData: number[] = [];
            const otherData: number[] = [];
            const unknownData: number[] = [];

            for (const u of users) {
                if (!u?.country) continue;
                const { male = 0, female = 0, other = 0, unknown = 0 } = u.genderData ?? {};
                labels.push(u.country);
                maleData.push(male);
                femaleData.push(female);
                otherData.push(other);
                unknownData.push(unknown);
            }

            const newChartData: ChartData<'bar'> = {
                labels: labels,
                datasets: [
                    {
                        label: 'Unknown',
                        data: unknownData,
                        backgroundColor: 'rgba(105, 105, 105, 0.391)', // Gray
                        borderWidth: 1.5,
                        borderColor: 'rgba(90, 90, 90, 0.63)',
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.8,
                        borderRadius: 6,
                    },
                    {
                        label: 'Other',
                        data: otherData,
                        backgroundColor: 'rgba(73, 178, 178, 0.8)', // Bright Teal
                        borderWidth: 1.5,
                        borderColor: 'rgba(0, 151, 151, 1)',
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.8,
                        borderRadius: 6,
                    },
                    {
                        label: 'Male',
                        data: maleData,
                        backgroundColor: 'rgba(33, 149, 226, 0.531)', // Bright Blue
                        borderWidth: 1.5,
                        borderColor: 'rgba(0, 123, 206, 0.88)',
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.8,
                        borderRadius: 6,
                    },
                    {
                        label: 'Female',
                        data: femaleData,
                        backgroundColor: 'rgba(255, 99, 133, 0.599)', // Bright Pink
                        borderWidth: 1.5,
                        borderColor: 'rgba(209, 60, 115, 0.88)',
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.8,
                        borderRadius: 6,
                    }
                ],
            };
            setLocationChartData(newChartData);

        } catch (error) {
            console.log(error);
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        getGenderData();
    }, []);

    return (
        <div className={`relative flex-grow h-full`}>
            {isLoading ? (
                <Skeleton active />
            ) : (
                <>
                    <div className={`overflow-x-auto h-full custom-scrollbar overflow-y-hidden`}>
                        <h1 className="font-medium pl-0.5 text-nowrap pb-3">Location/Gender Distribution of Developers (Sponsors & Sponsored)</h1>
                        <div className="min-w-[3500px] h-full pb-10">
                            <Bar options={chartOptions} data={locationChartData} />
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}


const GenderDataGraph = () => {
    // Interface for api 
    interface genderData {
        count: number;
        gender: string;
    }
    const { token } = theme.useToken();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [locationChartData, setLocationChartData] = useState<ChartData<'doughnut'>>({
        labels: [],
        datasets: [],
    });

    const chartOptions: ChartOptions<'doughnut'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: "right",
                labels: {
                    color: token.colorTextSecondary
                },
                title: {
                    display: true,
                    text: 'User Gender Types',
                }
            },
            tooltip: {
                backgroundColor: '#292c30',
                titleColor: '#e5e7eb',
                bodyColor: '#fff',
                borderColor: '#4b5563',
                borderWidth: 1,
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function (context) {
                        const label = context.label || '';
                        const value = context.raw as number;
                        const total = context.chart.data.datasets[0].data.reduce((a, b) => (a as number) + (b as number), 0) as number || 1;
                        const percentage = ((value / total) * 100).toFixed(1) + '%';
                        return `${label}: ${value} (${percentage})`;
                    }
                }
            },
        },
    };

    const getGenderData = async () => {
        try {
            const response = await fetch(`${apiUrl}/gender-stats`)
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            const genderData = data as genderData[] || [];
            const labels = genderData.map(c => c.gender).filter(Boolean);
            const count = genderData.map(c => c.count);

            const newChartData: ChartData<'doughnut'> = {
                labels: labels,
                datasets: [
                    {
                        label: 'Gender',
                        data: count,
                        backgroundColor: [
                            'rgba(55, 135, 188, 0.5)', // Male
                            'rgba(75, 192, 192, 0.5)', // Other
                            'rgba(255, 99, 132, 0.5)', // Female
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 99, 132, 1)',
                        ],
                        borderWidth: 2,
                    },
                ],
            };
            setLocationChartData(newChartData);

        } catch (error) {
            console.log(error)
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        getGenderData();
    }, []);

    return (
        <div className='relative flex-grow h-full w-full pb-5'>
            {isLoading ? (
                <Skeleton active />
            ) : (
                <>
                    <h1 className="font-medium">Gender Distribution (Users With Pronouns)</h1>
                    <div className="h-full p-5">
                        <Doughnut options={chartOptions} data={locationChartData} />
                    </div>
                </>
            )}
        </div>
    )
}



const SponsorshipsGraph = () => {
    interface sponsorshipData {
        both: number;
        sponsored: number;
        sponsoring: number;
    }
    const { token } = theme.useToken();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [sponsorChartData, setSponsorChartData] = useState<ChartData<'doughnut'>>({
        labels: [],
        datasets: [],
    });

    const chartOptions: ChartOptions<'doughnut'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: "right",
                labels: {
                    color: token.colorTextSecondary
                },
                title: {
                    display: true,
                    text: "Sponsorship Type",
                }
            },
            tooltip: {
                backgroundColor: '#1f2937',
                titleColor: '#e5e7eb',
                bodyColor: '#fff',
                borderColor: '#4b5563',
                borderWidth: 1,
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function (context) {
                        const label = context.label || '';
                        const value = context.raw as number;
                        const total = context.chart.data.datasets[0].data.reduce((a, b) => (a as number) + (b as number), 0) as number || 1;
                        const percentage = ((value / total) * 100).toFixed(1) + '%';
                        return `${label}: ${value} (${percentage})`;
                    }
                }
            },
        },
    };

    const getSponsorshipData = async () => {
        try {
            const response = await fetch(`${apiUrl}/user-sponsorship-stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            const sponsorsData: sponsorshipData[] = data as sponsorshipData[] || [];
            const chartData: number[] = sponsorsData.flatMap(obj =>
                Object.values(obj)
            );
            console.log(chartData);

            const newChartData: ChartData<'doughnut'> = {
                labels: ["Both", "Sponsored", "Sponsoring"],
                datasets: [
                    {
                        label: 'Sponsoring',
                        data: chartData,
                        backgroundColor: [
                            'rgba(93, 138, 159, 0.7)',
                            'rgba(181, 97, 146, 0.7)',
                            'rgba(117, 91, 165, 0.7)',
                        ],
                        borderColor: [
                            'rgba(137, 207, 240, 1)',
                            'rgba(255, 128, 202, 1)',
                            'rgba(180, 140, 255, 1)',
                        ],
                        borderWidth: 2,
                    },
                ],
            };
            setSponsorChartData(newChartData);
        }
        catch (error) {
            console.log(error);
        }
        finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        getSponsorshipData();
    }, []);

    return (
        <div className='relative flex-grow h-full w-full pb-5'>
            {isLoading ? (
                <Skeleton active />
            ) : (
                <>
                    <h1 className="font-medium">Sponsored & Sponsoring User Percentages</h1>
                    <div className="h-full p-5">
                        <Doughnut options={chartOptions} data={sponsorChartData} />
                    </div>
                </>
            )}
        </div>
    )
}
