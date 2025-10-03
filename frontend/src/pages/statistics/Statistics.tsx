import { Tabs } from "antd";
import { useState } from "react";

import GeneralStatsPage from "./tabs/GeneralStatistics";

export default function Statistics() {
    const [userStatsTick, setUserStatsTick] = useState(0);

    const data = [
        {
            label: "Overall Statistics",
            key: "1",
            children: <GeneralStatsPage playSignal={userStatsTick} />,
        },
        // {
        //     label: "User Analytics",
        //     key: "2",
        //     children: <UserStatsPage playSignal={userStatsTick} />,
        // },
        // {
        //     label: "Organization Analytics",
        //     key: "3",
        //     children: <></>,
        // },
    ];


    return (
        <>
            <style>
                {`
                .tabs-fill {
                    display: flex;
                    flex-direction: column;
                    height: 100%;
                }
                .tabs-fill .ant-tabs-content-holder {
                    flex: 1;
                    min-height: 0;
                    display: flex;
                }
                .tabs-fill .ant-tabs-content,
                .tabs-fill .ant-tabs-tabpane {
                    height: 100%;
                }
                `}
            </style>
            <div className="h-full flex flex-col min-h-0 pl-2.5">
                <Tabs
                    className="flex-1 min-h-0 tabs-fill"
                    type="card"
                    items={data}
                    onChange={(key) => {
                        if (key === "2") setUserStatsTick((v) => v + 1);
                        if (key === "1") setUserStatsTick((v) => v + 1);
                        if (key === "3") setUserStatsTick((v) => v + 1);
                    }}
                />
            </div>
        </>
    )
}