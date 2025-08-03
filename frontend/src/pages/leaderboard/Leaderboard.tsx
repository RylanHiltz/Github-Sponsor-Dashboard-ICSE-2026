import React, { useEffect, useState, useRef, useLayoutEffect, useContext } from 'react'
import styles from './Leaderboard.module.css'
import { Table, Pagination } from 'antd';
import { useNavigate } from 'react-router';
import { apiUrl } from '../../api';
import { createStyles } from 'antd-style';
import Carousel from '../../components/Carousel';

// Type imports 
import type { TableProps, TablePaginationConfig } from 'antd';
import type { LeaderboardUser, Location, LeaderboardStatsData } from '../../types/LeaderboardUserModel';
import type { ColumnsType } from 'antd/es/table';
import type { FilterValue, SortOrder } from 'antd/es/table/interface';

import { SearchContext } from '../../context/SearchContext';

const useStyle = createStyles(({ css, prefixCls }) => {
    return {
        customTable: css`
      .${prefixCls}-table {
        .${prefixCls}-table-container {
          .${prefixCls}-table-body,
          .${prefixCls}-table-content {
            scrollbar-width: thin;
            scrollbar-color: #474747 transparent;
            scrollbar-gutter: stable;
          }
        }
        /* Add this rule to prevent header text from wrapping */
        .${prefixCls}-table-thead > tr > th {
          white-space: nowrap;
          user-select: none;
        }
        .${prefixCls}-ant-table-column-title {
        }
      }
    `,
    };
});

const Leaderboard: React.FC = () => {

    // Navigation handle for user pages
    const navigate = useNavigate();

    // Table consts (styles, dynamic height for scrolling, loading state)
    const tablestyles = useStyle();
    const [scrollY, setScrollY] = useState<number>();
    const ref1 = useRef<HTMLDivElement | null>(null)
    const [loading, setLoading] = useState(false);

    const [users, setUsers] = useState<LeaderboardUser[]>([]);
    const [locationFilters, setLocationFilters] = useState<Location[]>([])
    const [leaderboardData, setLeaderboardData] = useState<LeaderboardStatsData | null>(null);

    const searchContext = useContext(SearchContext);
    if (!searchContext) {
        throw new Error('Leaderboard must be used within a SearchProvider');
    }
    const { searchTerm } = searchContext;

    // Table data consts
    const [pagination, setPagination] = useState<TablePaginationConfig>({
        current: 1,
        pageSize: 10,
        total: 0,
    });
    const [filters, setFilters] = useState<Record<string, FilterValue | null>>({});
    const [sorters, setSorters] = useState<Record<string, SortOrder | null>>({});

    const fetchUsers = async (
        currentPagination: TablePaginationConfig,
        currentFilters: Record<string, FilterValue | null>,
        currentSorters: Record<string, SortOrder | null>
    ) => {
        setLoading(true);

        const queryParams = new URLSearchParams({
            page: (currentPagination.current || 1).toString(),
            per_page: (currentPagination.pageSize || 10).toString(),
        });

        // Check if search term has been provided
        if (searchTerm) {
            queryParams.append("search", searchTerm);
        }

        Object.entries(currentFilters).forEach(([key, value]) => {
            // Safely handle null/undefined filter values from Ant Design
            if (value && Array.isArray(value) && value.length > 0) {
                (value as string[]).forEach(v => queryParams.append(key, v));
            }
        });

        Object.entries(currentSorters).forEach(([field, order]) => {
            if (order) { // Only add if an order is set (not null)
                queryParams.append("sortField", field);
                queryParams.append("sortOrder", order);
            }
        });

        try {
            const response = await fetch(`${apiUrl}/api/users?${queryParams.toString()}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json(); // Expects { users: [], total: number }

            const mappedUsers = data.users.map((user: LeaderboardUser) =>
                Object.fromEntries(
                    Object.entries(user).map(([key, value]) => [
                        key,
                        value === null ? "None" : value === "Organization" ? "Org" : value,
                    ])
                ) as LeaderboardUser
            );

            setUsers(mappedUsers);
            setPagination(prev => ({
                ...prev,
                total: data.total, // Set total from the API response
            }));

        } catch (error) {
            console.error("Error fetching users:", error);
        } finally {
            setLoading(false);
        }
    };

    async function getLocations() {
        try {
            const response = await fetch(`${apiUrl}/api/users/location`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            const locationData = data.map((location: string) => ({
                text: location,
                value: location,
            }));
            setLocationFilters(locationData);

        } catch (error) {
        }
    }

    // Get leaderboard statistics every 15 seconds for live updating carousel
    const getLeaderboardStats = async () => {
        try {
            const response = await fetch(`${apiUrl}/api/stats/brief`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data: LeaderboardStatsData = await response.json();

            setTimeout(getLeaderboardStats, 15000);
            setLeaderboardData(data);

        } catch (error) {
            console.error("Error fetching leaderboard stats:", error);
        }
    };

    const columns: ColumnsType<LeaderboardUser> = [
        {
            title: "Username",
            dataIndex: "username",
            key: "username",
            width: 115,
            sortDirections: ["descend", "ascend"],
            sorter: true,
            render: (_: any, record: LeaderboardUser) => (
                <>
                    <span className='flex items-center gap-1'>
                        <img src={record.avatar_url} alt={record.username} style={{ width: 24, borderRadius: '25%', marginRight: 8 }} />
                        {record.username && record.username.length > 15 ? `${record.username.slice(0, 13)}...` : record.username}
                    </span>
                </>
            ),
            onCell: () => ({
                style: {
                    whiteSpace: 'normal',
                    textOverflow: "hidden",
                },
            }),
        },
        {
            title: "Name",
            dataIndex: "name",
            key: "name",
            width: 110,
            sorter: true,
            sortDirections: ["descend", "ascend"],
            render: (text: string) =>
                text && text.length > 13 ? `${text.slice(0, 11)}...` : text,
        },
        {
            title: "Type",
            dataIndex: "type",
            key: "type",
            width: 70,
            filters: [
                {
                    text: 'User',
                    value: 'User',
                },
                {
                    text: 'Organization',
                    value: 'Organization',
                },
            ],
        },
        {
            title: "Gender",
            dataIndex: "gender",
            key: "gender",
            width: 85,
            filters: [
                {
                    text: 'Male',
                    value: 'Male',
                },
                {
                    text: 'Female',
                    value: 'Female',
                },
                {
                    text: 'Other',
                    value: 'Other',
                },
                {
                    text: 'Unknown',
                    value: 'Unknown',
                },
            ],
        },
        {
            title: "Location",
            dataIndex: "location",
            key: "location",
            width: 110,
            filters: locationFilters,
            filterSearch: true,
        },
        {
            title: "Followers",
            dataIndex: "followers",
            key: "followers",
            width: 100,
            sorter: {
                multiple: 2,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Following",
            dataIndex: "following",
            key: "following",
            width: 100,
            sorter: {
                multiple: 2,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Repos",
            dataIndex: "public_repos",
            key: "repos",
            width: 75,
            sorter: {
                multiple: 1,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Sponsors",
            dataIndex: "total_sponsors",
            key: "sponsors",
            width: 100,
            sorter: {
                multiple: 2,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Sponsoring",
            dataIndex: "total_sponsoring",
            key: "sponsoring",
            width: 110,
            sorter: {
                multiple: 2,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Earnings (Estimate)",
            dataIndex: "estimated_earnings",
            className: styles.nowrapHeader,
            key: "earnings",
            width: 165,
            render: (_: any, record: LeaderboardUser) => (
                <span style={{ fontWeight: 600 }}>
                    ${Math.round(record.estimated_earnings)}<span style={{ fontWeight: 400, fontSize: 12 }}>+ USD/mo</span>
                </span>
            ),
            sorter: {
                multiple: 3,
            },
            sortDirections: ["descend", "ascend"]
        },
    ];

    const handleTableChange: TableProps<LeaderboardUser>['onChange'] = (
        _pagination,
        newFilters,
        newSorters
    ) => {
        const sortersArray = Array.isArray(newSorters) ? newSorters : [newSorters];
        const formattedSorters = sortersArray.reduce((acc, s) => {
            if (s.field && s.order) {
                const key = Array.isArray(s.field) ? s.field.join('.') : String(s.field);
                acc[key] = s.order;
            }
            return acc;
        }, {} as Record<string, SortOrder>);

        setSorters(formattedSorters);
        setFilters(newFilters);
        setPagination(prev => ({
            ...prev,
            current: 1,
        }));
    };

    const getDynamicHeight = () => {
        let height = ref1.current?.clientHeight;
        console.log(height);
        if (height) {
            setScrollY(height - 47);
        }
    }

    useLayoutEffect(() => {
        getDynamicHeight();
        window.addEventListener('resize', getDynamicHeight);
        return () => {
            window.removeEventListener('resize', getDynamicHeight);
        }
    }, []);

    useEffect(() => {
        getLeaderboardStats();
        getLocations();
    }, []);


    useEffect(() => {
        // When a new search is performed, filters or sorters are changed, reset to page 1
        if (pagination.current !== 1) {
            setPagination(prev => ({ ...prev, current: 1 }));
        } else {
            // Otherwise, fetch users with the current state
            fetchUsers(pagination, filters, sorters);
        }
    }, [searchTerm, filters, sorters]);

    useEffect(() => {
        fetchUsers(pagination, filters, sorters);

    }, [pagination.current, pagination.pageSize, filters, sorters,]);


    return (
        <>
            <section className='grid grid-cols-1 grid-rows-[_1.2fr,5fr] h-full px-4 gap-3'>
                <div className='flex flex-col flex-shrink-0 gap-2 w-full h-full'>
                    <h1 className='text-[24px] font-semibold pb-1'>Leaderboard Statistics</h1>
                    <div className='flex-1 flex'>
                        {leaderboardData && <Carousel {...leaderboardData} />}
                    </div>
                    {/* <div className={styles.carouselContainer}>
                        <div className={styles.carouselTrack}>
                            {leaderboardData && [...Array(2)].map((_, i) => (
                                <React.Fragment key={i}>
                                    <div className='flex-shrink-0 h-full w-1/4 px-2'>
                                        <div className={`${styles.stats} flex-none`}>
                                            <h3>Total Users Tracked</h3>
                                            <h2 id="total-users-stat">{leaderboardData.total_users.toLocaleString()}</h2>
                                        </div>
                                    </div>
                                    <div className='flex-shrink-0 h-full w-1/4 px-2'>
                                        <div className={`${styles.stats} flex-none`}>
                                            <h3>Unique Sponsorships</h3>
                                            <h2 id="total-sponsorships-stat">{leaderboardData.total_sponsorships.toLocaleString()}</h2>
                                        </div>
                                    </div>
                                    <div className='flex-shrink-0 h-full w-1/4 px-2'>
                                        <div className={`${styles.stats} flex-none`}>
                                            <h3>Top Sponsored</h3>
                                            <h2>
                                                <span className='flex items-center justify-start gap-2'>
                                                    <img src={leaderboardData.top_sponsored.avatar_url} alt={leaderboardData.top_sponsored.username} className='w-8 h-8 rounded-full' />
                                                    <p className='pb-1 text-[30px]'>{leaderboardData.top_sponsored.username}</p>
                                                </span>
                                            </h2>
                                        </div>
                                    </div>
                                    <div className='flex-shrink-0 h-full w-1/4 px-2'>
                                        <div className={`${styles.stats} flex-none`}>
                                            <h3>Top Sponsoring</h3>
                                            <h2>
                                                <span className='flex items-center justify-start gap-2'>
                                                    <img src={leaderboardData.top_sponsoring.avatar_url} alt={leaderboardData.top_sponsoring.username} className='w-8 h-8 rounded-full' />
                                                    <p className='pb-1 text-[30]'>{leaderboardData.top_sponsoring.username}</p>
                                                </span>
                                            </h2>
                                        </div>
                                    </div>
                                </React.Fragment>
                            ))}
                        </div>
                    </div> */}
                </div>
                <div className='row-span-2 flex flex-col'>
                    <div ref={ref1} className='flex-grow overflow-y-hidden custom-scrollbar'>
                        <Table
                            className={tablestyles.styles.customTable}
                            columns={columns}
                            dataSource={users}
                            loading={loading}
                            showSorterTooltip={{ target: 'sorter-icon' }}
                            tableLayout='fixed'
                            onRow={(record) => ({
                                onClick: () => navigate(`/user/${record.id}`, { state: record }),
                                style: { cursor: "pointer" }
                            })}
                            onChange={handleTableChange}
                            scroll={{ x: 'max-content', y: scrollY }}
                            size="middle"
                            pagination={false}

                        />
                    </div>
                    <div className='flex-shrink-0 flex justify-end p-4'>
                        <Pagination
                            current={pagination.current}
                            pageSize={pagination.pageSize}
                            total={pagination.total} // Use total from state
                            showSizeChanger
                            pageSizeOptions={['10', '20', '50', '100']}
                            onChange={(page, size) => {
                                setPagination(prev => ({
                                    ...prev,
                                    current: page,
                                    pageSize: size,
                                }));
                            }}
                        />
                    </div>
                </div>
            </section >
        </>
    )
}
export default Leaderboard;