import { useState } from "react";
import { Button, theme, Skeleton } from "antd";
import styles from "../Statistics.module.css"
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { apiUrl } from "../../../api";
import { Bar, Pie, Doughnut } from "react-chartjs-2";
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

const GeneralStatistics = ({ playSignal }: { playSignal: number }) => {
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
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0 p-0`}
                    >
                        <h1 className="font-medium">Total Tracked Users</h1>
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0`}
                    >
                        <h1 className="font-medium">Most Sponsored User</h1>
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0`}
                    >
                        <h1 className="font-medium">Most Sponsoring User</h1>
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-1 md:col-span-3 xl:col-span-3 min-h-[120px] md:min-h-0`}
                    >
                        <h1 className="font-medium">Most Sponsored Country</h1>
                    </div>

                    {/* Largest graph */}
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-4 xl:col-span-8 row-span-2 md:row-span-4 xl:row-span-6`}
                    >
                    </div>

                    {/* Right-side graphs */}
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-2 xl:col-span-4 row-span-2 md:row-span-2 xl:row-span-3`}
                    >
                    </div>
                    <div
                        style={{ borderColor: token.colorBorder, backgroundColor: token.cardBg }}
                        className={`${styles.Card} col-span-1 sm:col-span-2 md:col-span-2 xl:col-span-4 row-span-2 md:row-span-2 xl:row-span-3`}
                    >
                    </div>
                </div>
            </section>
        </>
    );
}

export default GeneralStatistics
