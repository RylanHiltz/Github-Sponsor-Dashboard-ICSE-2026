import { useState } from "react";
import { Button, theme, Skeleton } from "antd";
import styles from "../Statistics.module.css"
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { apiUrl } from "../../../api";
import { Bar, Pie } from "react-chartjs-2";
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
// new SimpleBar(document.querySelector('[data-simplebar]'));

const UserStatsPage = ({ playSignal }: { playSignal: number }) => {
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
                        style={{ borderColor: token.colorBorder, background: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0 p-0`}
                    >
                        <h1>Total Tracked Users</h1>
                        <h2></h2>
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, background: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0`}
                    >
                        <h1>Most Sponsored User</h1>
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, background: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0`}
                    >
                        <h1>Most Sponsoring User</h1>
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, background: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0`}
                    >
                        <h1></h1>
                    </div>

                    {/* Largest graph */}
                    <div
                        style={{ borderColor: token.colorBorder, background: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-4 xl:col-span-8 row-span-2 md:row-span-4 xl:row-span-6`}
                    >
                        <LocationDistributionGraph />
                    </div>

                    {/* Right-side graphs */}
                    <div
                        style={{ borderColor: token.colorBorder, background: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-2 xl:col-span-4 row-span-2 md:row-span-2 xl:row-span-3`}
                    >
                        <GenderDistGraph />
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, background: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-2 xl:col-span-4 row-span-2 md:row-span-2 xl:row-span-3`}
                    >
                        <h1>Sponsored Devs VS Sponsoring Devs</h1>
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
                position: "chartArea",
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
                stacked: true,
            },
            y: {
                stacked: true
            }
        }
    };

    const getGenderData = async () => {
        try {
            const response = await fetch(`${apiUrl}/api/user-stats`)
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();

            const genderData = data as userLocations[];
            console.log("API Response:", genderData);

            const genderDist = genderData ?? [];

            const labels = genderDist.map(c => c.country).filter(Boolean);
            const maleData = genderDist.map(c => c.genderData.male);
            const femaleData = genderDist.map(c => c.genderData.female);
            const otherData = genderDist.map(c => c.genderData.other);
            const unknownData = genderDist.map(c => c.genderData.unknown);
            const totals = genderDist.map(c => c.genderData.male + c.genderData.female + c.genderData.other + c.genderData.unknown);

            const newChartData: ChartData<'bar'> = {
                labels: labels,
                datasets: [
                    {
                        label: 'Total',
                        data: totals,
                        // This dataset is not rendered but used by the datalabels plugin to show totals
                        // @ts-ignore
                        datalabels: {
                            color: token.colorText,
                            anchor: 'end',
                            align: 'top',
                            font: {
                                weight: 'bold'
                            },
                            formatter: (value: number) => value > 0 ? value : ''
                        },
                        // Make it invisible
                        stack: 'Stack 1', // Use a different stack to not interfere with rendering
                    },
                    {
                        label: 'Unknown',
                        data: unknownData,
                        backgroundColor: 'rgba(156, 163, 175, 0.8)', // Gray
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.9,
                    },
                    {
                        label: 'Other',
                        data: otherData,
                        backgroundColor: 'rgba(75, 192, 192, 0.8)', // Bright Teal
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.9,
                    },
                    {
                        label: 'Male',
                        data: maleData,
                        backgroundColor: 'rgba(54, 162, 235, 0.8)', // Bright Blue
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.9,
                    },
                    {
                        label: 'Female',
                        data: femaleData,
                        backgroundColor: 'rgba(255, 99, 132, 0.8)', // Bright Pink
                        stack: 'Stack 0',
                        barPercentage: 1,
                        categoryPercentage: 0.9,
                    }
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
        <div className='relative flex-grow h-full pb-5'>
            {isLoading ? (
                <Skeleton active />
            ) : (
                <>
                    <h1>Location/Gender Distribution of Developers (Sponsors & Sponsored)</h1>
                    <div className={`overflow-x-auto h-full custom-scrollbar`}>
                        <div className="min-w-[1200px] h-full">
                            <Bar options={chartOptions} data={locationChartData} />
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}


const GenderDistGraph = () => {
    // Interface for api 
    interface genderData {
        count: number;
        gender: string;
    }
    const { token } = theme.useToken();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [locationChartData, setLocationChartData] = useState<ChartData<'pie'>>({
        labels: [],
        datasets: [],
    });

    const chartOptions: ChartOptions<'pie'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: "right",
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
    };

    const getGenderData = async () => {
        try {
            const response = await fetch(`${apiUrl}/api/gender-stats`)
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            const genderData = data as genderData[];
            const genderDist = genderData ?? [];
            const labels = genderDist.map(c => c.gender).filter(Boolean);
            const count = genderDist.map(c => c.count);

            console.log(count);

            const newChartData: ChartData<'pie'> = {
                labels: labels,
                datasets: [
                    {
                        label: 'Gender',
                        data: count,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.5)', // Male
                            'rgba(75, 192, 192, 0.5)', // Other
                            'rgba(255, 99, 132, 0.5)', // Female
                            'rgba(156, 163, 175, 0.5)', // Unknown
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(156, 163, 175, 1)',
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
                        <Pie options={chartOptions} data={locationChartData} />
                    </div>
                </>
            )}
        </div>
    )
}



const SponsorshipsGraph = () => {
    return (
        <div>UserStatistics</div>
    )
}
