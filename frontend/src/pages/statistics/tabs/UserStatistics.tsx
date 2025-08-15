import { Card, Button } from "antd";
import { theme } from "antd";
import styles from "../Statistics.module.css"
import { useEffect, useRef } from "react";
import gsap from "gsap";


const UserStatsPage = ({ playSignal }: { playSignal: number }) => {
    const containerRef = useRef<HTMLDivElement>(null);

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

    const { token } = theme.useToken();

    return (
        <>
            <section className="h-full flex flex-col min-h-0 overflow-hidden">
                <div>
                    <Button>Advanced Statistics</Button>
                </div>
                <div
                    ref={containerRef}
                    className="
                    flex-1 min-h-0
                    grid grid-flow-dense gap-5 pt-2.5 pb-2
                    grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4
                    auto-rows-[minmax(140px,auto)]
                    xl:[grid-template-rows:110px] xl:auto-rows-[minmax(180px,auto)]
                    overflow-y-hidden
                    "
                >
                    <Card
                        style={{ backgroundColor: token.cardBg }}
                        className={`${styles.Card} stat-card h-full`}
                    >
                        <h1>Total Tracked Users</h1>
                    </Card>
                    <Card
                        style={{ backgroundColor: token.cardBg }}
                        className={`${styles.Card} stat-card h-full`}
                    >
                        <h1></h1>
                    </Card>
                    <Card
                        style={{ backgroundColor: token.cardBg }}
                        className={`${styles.Card} stat-card h-full`}
                    >
                        <h1></h1>
                    </Card>
                    <Card
                        style={{ backgroundColor: token.cardBg }}
                        className={`${styles.Card} stat-card h-full`}
                    >
                        <h1></h1>
                    </Card>

                    {/* Largest graph */}
                    <Card
                        style={{ backgroundColor: token.cardBg }}
                        className={`${styles.Card} stat-card h-full col-span-1 sm:col-span-4 lg:col-span-3 xl:col-span-3 xl:row-span-2`}
                    >
                        <h1>Location Distribution of Users</h1>
                    </Card>

                    {/* Right-side graphs */}
                    <Card
                        style={{ backgroundColor: token.cardBg }}
                        className={`${styles.Card} stat-card h-full col-span-1 col-start-4 xl:col-span-1`}
                    >
                        <h1>Gender Distribution</h1>
                    </Card>
                    <Card
                        style={{ backgroundColor: token.cardBg }}
                        className={`${styles.Card} stat-card h-full col-span-1 col-start-4 xl:col-span-1`}
                    >
                        <h1>card</h1>
                    </Card>
                </div>
            </section>
        </>
    );
}
export default UserStatsPage;