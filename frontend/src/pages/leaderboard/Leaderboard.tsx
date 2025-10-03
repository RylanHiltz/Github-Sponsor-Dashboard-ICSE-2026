import React, { useEffect, useState, useRef, useLayoutEffect, useContext } from 'react'
import styles from './Leaderboard.module.css'
import { Table, Pagination, Button } from 'antd';
import { useNavigate } from 'react-router';
import { apiUrl } from '../../api';
import { createStyles } from 'antd-style';
import Carousel from '../../components/Carousel';
import { SearchContext } from '../../context/SearchContext';
import { MdClear } from "react-icons/md";
import { useDebounce } from '../../hooks/debounce'; // Import the new hook

// Type imports 
import type { TableProps, TablePaginationConfig } from 'antd';
import type { LeaderboardUser, Location, LeaderboardStatsData } from '../../types/LeaderboardUserModel';
import type { ColumnsType } from 'antd/es/table';
import type { FilterValue, SortOrder } from 'antd/es/table/interface';


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
    const { searchTerm, setSearchTerm } = searchContext;
    const debouncedSearchTerm = useDebounce(searchTerm, 600); // Create debounced value

    // Table data consts
    const [pagination, setPagination] = useState<TablePaginationConfig>({
        current: 1,
        pageSize: 10,
        total: 0,
    });
    const [filters, setFilters] = useState<Record<string, FilterValue | null>>({});
    const [sorters, setSorters] = useState<Record<string, SortOrder | null>>({});

    const handleClearFilters = () => {
        setFilters({});
        setSorters({});
        setSearchTerm('');
        setPagination(prev => ({ ...prev, current: 1 }));
    };

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
            const response = await fetch(`${apiUrl}/users?${queryParams.toString()}`);
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
            const response = await fetch(`${apiUrl}/users/location`);
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
    const getLeaderboardStats = async (_signal?: AbortSignal) => {
        try {
            const response = await fetch(`${apiUrl}/stats/brief`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data: LeaderboardStatsData = await response.json();
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
            sortOrder: sorters.username || null,
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
            sortOrder: sorters.name || null,
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
            filteredValue: filters.type || null,
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
            filteredValue: filters.gender || null,
        },
        {
            title: "Location",
            dataIndex: "location",
            key: "location",
            width: 110,
            filters: locationFilters,
            filterSearch: true,
            filteredValue: filters.location || null,
        },
        {
            title: "Followers",
            dataIndex: "followers",
            key: "followers",
            width: 100,
            sorter: true,
            sortOrder: sorters.followers || null,
            sortDirections: ["descend", "ascend"],

        },
        {
            title: "Following",
            dataIndex: "following",
            key: "following",
            width: 100,
            sorter: true,
            sortOrder: sorters.following || null,
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Repos",
            dataIndex: "public_repos",
            key: "repos",
            width: 75,
            sorter: true,
            sortOrder: sorters.public_repos || null,
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Sponsors",
            dataIndex: "total_sponsors",
            key: "sponsors",
            width: 100,
            sorter: true,
            sortOrder: sorters.total_sponsors || null,
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Sponsoring",
            dataIndex: "total_sponsoring",
            key: "sponsoring",
            width: 110,
            sorter: true,
            sortOrder: sorters.total_sponsoring || null,
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Min. Earnings (Estimate)",
            dataIndex: "estimated_earnings",
            className: styles.nowrapHeader,
            key: "earnings",
            width: 200,
            render: (_: any, record: LeaderboardUser) => (
                <span style={{ fontWeight: 600 }}>
                    ${Math.round(record.estimated_earnings)}<span style={{ fontWeight: 400, fontSize: 12 }}>+ USD/mo</span>
                </span>
            ),
            sorter: true,
            sortOrder: sorters.estimated_earnings || null,
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
        // Reset to page 1 when filters or sorters change
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
        // Poll once immediately, then every 15s. Clean up to avoid duplicate timers in StrictMode.
        const controller = new AbortController();
        let timer: number | undefined;
        let inFlight = false;
        getLocations();

        const tick = async () => {
            if (inFlight) return; // prevent overlap
            inFlight = true;
            await getLeaderboardStats(controller.signal);
            inFlight = false;
            timer = window.setTimeout(tick, 15000);
        };

        tick(); // immediate first fetch

        return () => {
            controller.abort();                     // cancel in-flight request
            if (timer) window.clearTimeout(timer);  // clear scheduled poll
        };
    }, []);


    useEffect(() => {
        // When a new search is performed, filters or sorters are changed, reset to page 1
        if (pagination.current !== 1) {
            setPagination(prev => ({ ...prev, current: 1 }));
        } else {
            // Otherwise, fetch users with the current state
            fetchUsers(pagination, filters, sorters);
        }
    }, [debouncedSearchTerm]); // Use debouncedSearchTerm here

    useEffect(() => {
        fetchUsers(pagination, filters, sorters);

    }, [pagination.current, pagination.pageSize, filters, sorters]);


    return (
        <>
            <section className='grid grid-cols-1 grid-rows-[_1.2fr,5fr] h-full pl-2 gap-3'>
                <div className='flex flex-col flex-shrink-0 gap-2 w-full h-full'>
                    <h1 className='text-[24px] font-semibold pb-1'>Leaderboard Statistics</h1>
                    <div className='flex-1 flex'>
                        {leaderboardData && <Carousel {...leaderboardData} />}
                    </div>
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
                    <div className='flex-shrink-0 flex justify-end pt-2'>
                        <div className='flex w-full justify-between'>
                            <Button icon={<MdClear />} iconPosition='end' onClick={handleClearFilters}>Clear Filters</Button>
                            <Pagination
                                simple
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
                </div>
            </section >
        </>
    )
}
export default Leaderboard;