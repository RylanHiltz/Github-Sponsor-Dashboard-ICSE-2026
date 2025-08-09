import React, { useContext } from 'react';
import { useNavigate, useLocation, Outlet, Link } from 'react-router';
import { Layout, Menu, theme, Statistic } from 'antd';
import Search from '../components/SearchBar';
import { SearchProvider, SearchContext } from '../context/SearchContext';
import DarkmodeButton from '../components/DarkmodeButton';

import { AiFillGithub } from "react-icons/ai";
import { MdSpaceDashboard } from "react-icons/md";
import { MdPersonAddAlt1 } from "react-icons/md";
import { IoMdStats } from "react-icons/io";



const { Header, Content, Sider } = Layout;

const DashboardContent: React.FC = () => {

    const { Timer } = Statistic;
    const deadline = Date.now() + 1000 * 60 * 5;
    const navigate = useNavigate();
    const location = useLocation();
    const searchContext = useContext(SearchContext);

    if (!searchContext) {
        throw new Error('useSearch must be used within a SearchProvider');
    }
    const { setSearchTerm } = searchContext;

    const routes: { [key: string]: string } = {
        '1': '/',
        '2': '/statistics',
        '3': '/request-user',
    };

    const menuKeyMap = Object.fromEntries(
        Object.entries(routes).map(([key, path]) => [path, key])
    );

    const handleMenuClick = ({ key }: { key: string }) => {
        if (routes[key]) {
            navigate(routes[key]);
        }
    };

    const {
        token: { colorBgContainer, borderRadiusLG, colorBorder, linkHover, },
    } = theme.useToken();


    return (
        <Layout className='h-screen'>
            <Header style={{ background: colorBgContainer, borderBottom: `1px solid ${colorBorder}` }} className='items-center flex gap-3 pr-2.5 pl-5 justify-between'>
                <div className='flex items-center gap-5 w-full'>
                    <Link to={"/"} style={{ color: 'inherit' }} onMouseEnter={(e) => e.currentTarget.style.color = linkHover} onMouseLeave={(e) => e.currentTarget.style.color = 'inherit'} className="flex items-center gap-1.5 px-1">
                        <AiFillGithub className='text-[22px]' />
                        <h1 className='font-semibold text-[18px] whitespace-nowrap'>Github Sponsorships</h1>
                    </Link>
                    <span className='flex w-full gap-2'>
                        {location.pathname === '/' && (
                            <Search onSubmit={e => { setSearchTerm(e) }} />
                        )}
                    </span>
                </div>
                <div className='flex gap-3 pr-[20px] items-center'>
                    {/* Timer */}
                    <div className={`border-[1px] flex items-center p-2 rounded-md h-[32px]`} style={{ borderColor: colorBorder }}>
                        <p className='text-[12px] font-medium select-none whitespace-nowrap'>Refresh in&nbsp;</p>
                        <Timer type='countdown' value={deadline} format="m:ss" valueStyle={{ fontSize: 12 }}></Timer>
                    </div>
                    {/* Darkmode Button */}
                    <DarkmodeButton />
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
        </Layout >
    );
};

const Dashboard: React.FC = () => {
    return (
        <SearchProvider>
            <DashboardContent />
        </SearchProvider>
    );
};
export default Dashboard;