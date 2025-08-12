
import { Tabs } from "antd";

export default function Statistics() {

    const data = [
        {
            label: "Overall Statistics",
            key: "1",
            children: <></>,
        },
        {
            label: "User Stats",
            key: "2",
            children: <UserStatsPage />,
        },
        {
            label: "Organization Stats",
            key: "3",
            children: <></>,
        },
    ];


    return (
        <Tabs
            type="card"
            items={data}
        />
    )
}

const UserStatsPage = () => {
    return (
        <>
            <div>User Statistics</div>
        </>
    )
}