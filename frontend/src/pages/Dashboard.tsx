import React from 'react';
import { Outlet } from "react-router"
import { Layout, Menu, theme, Input, Button, Statistic, Space } from 'antd';
import type { StatisticTimerProps } from 'antd';
import { useNavigate, useLocation } from 'react-router';
import { AiFillGithub } from "react-icons/ai";
import { MdSpaceDashboard } from "react-icons/md";
import { IoMdStats } from "react-icons/io";
import { MdPersonAddAlt1 } from "react-icons/md";
import { MdDarkMode } from "react-icons/md";
import { IoMdSearch } from "react-icons/io";
import { SearchOutlined } from '@ant-design/icons';

const { Header, Content, Sider } = Layout;

const Dashboard: React.FC = () => {
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    const { Timer } = Statistic;
    const deadline = Date.now() + 1000 * 60 * 5;
    const navigate = useNavigate();
    const location = useLocation();

    const routes: { [key: string]: string } = {
        '1': '/',
        '2': '/statistics',
    };

    const menuKeyMap = Object.fromEntries(
        Object.entries(routes).map(([key, path]) => [path, key])
    );

    const handleMenuClick = ({ key }: { key: string }) => {
        if (routes[key]) {
            navigate(routes[key]);
        }
    };

    // On countdown finish 
    const onFinish: StatisticTimerProps['onFinish'] = () => {
        console.log('finished!');
    };

    return (
        <Layout className='h-screen'>
            <Header className='bg-[#111111] items-center flex gap-3 px-[20px] justify-between'>
                <div className='flex items-center gap-5 w-full'>
                    <span className='flex items-center gap-1.5 px-1'>
                        <AiFillGithub className='text-[22px]' />
                        <h1 className='font-semibold text-[18px] whitespace-nowrap'>Github Sponsorships</h1>
                    </span>
                    <span className='flex w-full gap-2'>
                        {location.pathname === '/' && (
                            <>
                                <Input style={{ width: 'calc(50% - 85px)' }} className='min-w-[150px]' placeholder='Search by name or username' />
                                <Button type='text' className={`p-2 flex whitespace-nowrap w-min gap-1 bg-[--button-bg]`} iconPosition='end' size="middle" icon={<SearchOutlined className='text-[16px]' />}>Search
                                </Button>
                            </>
                        )}
                    </span>
                </div>
                <div className='flex gap-3 pr-[20px] items-center'>
                    {/* Timer */}
                    <div className='border-[#303030] border-[1px] flex items-center p-2 rounded-md bg-[--dark-gray] h-[32px]'>
                        <p className='text-[12px] font-medium select-none whitespace-nowrap'>Refresh in&nbsp;</p>
                        <Timer type='countdown' value={deadline} format="m:ss" valueStyle={{ fontSize: 12 }}></Timer>
                    </div>
                    {/* Darkmode Button */}
                    <Button className='h-[32px] w-[32px] p-0 bg-[--dark-gray]'>
                        <MdDarkMode className='text-[20px]' />
                    </Button>
                </div>
            </Header>
            <Layout
                style={{ background: colorBgContainer, borderRadius: borderRadiusLG }} className='h-full px-[20px] py-[20px]'
            >
                <Sider style={{ background: colorBgContainer }} width={220} collapsed>
                    <Menu
                        mode='inline'
                        defaultSelectedKeys={['1']}
                        defaultOpenKeys={['sub1']}
                        style={{ height: '100%', paddingRight: 15 }}
                        selectedKeys={[menuKeyMap[location.pathname]]} // Highlight active menu item
                        onClick={handleMenuClick}
                        items={[
                            {
                                key: '1',
                                label: 'Dashboard',
                                icon: <MdSpaceDashboard />
                            },
                            {
                                key: '2',
                                label: 'Statistics',
                                icon: <IoMdStats />
                            },
                            {
                                key: '3',
                                label: 'Request User',
                                icon: <MdPersonAddAlt1 />
                            },
                        ]}
                    />
                </Sider>
                <Content style={{ padding: '0 10px', minHeight: 280 }}>
                    <Outlet />
                </Content>
            </Layout>
        </Layout>
    );
};

export default Dashboard;