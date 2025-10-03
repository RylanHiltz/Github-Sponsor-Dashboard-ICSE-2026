import React, { useContext } from 'react';
import { useNavigate, useLocation, Outlet, Link } from 'react-router';
import { Layout, Menu, theme } from 'antd';
import Search from '../components/SearchBar';
import { SearchProvider, SearchContext } from '../context/SearchContext';
import DarkmodeButton from '../components/DarkmodeButton';

import { AiFillGithub } from "react-icons/ai";
import { MdSpaceDashboard } from "react-icons/md";
import { IoMdStats } from "react-icons/io";


const { Header, Content, Sider } = Layout;

const DashboardContent: React.FC = () => {

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
        // '3': '/request-user',
        // '4': '/docs'
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
                                label: 'Overview',
                                icon: <MdSpaceDashboard />
                            },
                            {
                                key: '2',
                                label: 'Analytics',
                                icon: <IoMdStats />
                            },
                            // {
                            //     key: '3',
                            //     label: 'Request User',
                            //     icon: <MdPersonAddAlt1 />
                            // },
                            // {
                            //     key: '4',
                            //     label: 'Docs',
                            //     icon: <IoDocumentText />
                            // },
                        ]}
                    />
                </Sider>
                <Content style={{ padding: '0 10px', minHeight: 280, }}>
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