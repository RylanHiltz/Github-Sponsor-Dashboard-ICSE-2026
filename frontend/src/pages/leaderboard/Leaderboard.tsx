import { useEffect, useState, useRef, useLayoutEffect } from 'react'
import styles from './Leaderboard.module.css'
import { Button, Space, Table, Pagination } from 'antd';
import { useNavigate } from 'react-router';
import { apiUrl } from '../../api';

import type { TableProps, TablePaginationConfig } from 'antd';
import type { LeaderboardUser } from '../../types/LeaderboardUserModel';
import type { ColumnsType } from 'antd/es/table';
import type { FilterValue, SortOrder } from 'antd/es/table/interface';
import { createStyles } from 'antd-style';


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
        }
      }
    `,
    };
});

interface Location {
    text: string,
    value: string
}

const Leaderboard: React.FC = () => {

    // Navigation handle for user pages
    const navigate = useNavigate();

    // Table consts (styles, dynamic height for scrolling, loading state)
    const tablestyles = useStyle();
    const [scrollY, setScrollY] = useState<number>();
    const ref1 = useRef<HTMLDivElement | null>(null)
    const [loading, setLoading] = useState(false);

    // Table data consts
    const [users, setUsers] = useState<LeaderboardUser[]>([]);
    const [filters, setFilters] = useState<Record<string, FilterValue | null>>({});
    const [locationFilters, setLocationFilters] = useState<Location[]>([])
    const [sorters, setSorters] = useState<Record<string, SortOrder | null>>({});

    // Default pagination values
    const [pagination, setPagination] = useState<TablePaginationConfig>({
        current: 1,
        pageSize: 10,
        total: 0,
    });

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

    useEffect(() => {
        fetchUsers(pagination, filters, sorters);
        // Add `sorters` to the dependency array
    }, [pagination.current, pagination.pageSize, filters, sorters]);


    useEffect(() => {
        async function getLocations() {
            try {
                const response = await fetch(`${apiUrl}/api/users/location`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

                const data = await response.json();
                console.log(data)

                const locationData = data.map((location: string) => ({
                    text: location,
                    value: location,
                }));
                setLocationFilters(locationData);

            } catch (error) {
            }
        }
        getLocations();
    }, []);


    const columns: ColumnsType<LeaderboardUser> = [
        {
            title: "Username",
            dataIndex: "username",
            key: "username",
            width: 30,
            sortDirections: ["descend", "ascend"],
            sorter: true,
            // You can access any property from the record in the render function:
            render: (_: any, record: LeaderboardUser) => (
                <>
                    <span className='flex items-center gap-1'>
                        <img src={record.avatar_url} alt={record.username} style={{ width: 24, borderRadius: '25%', marginRight: 8 }} />
                        {record.username && record.username.length > 15 ? `${record.username.slice(0, 13)}...` : record.username}
                    </span>
                </>
            ),
        },
        {
            title: "Name",
            dataIndex: "name",
            key: "name",
            width: 10,
            sorter: true,
            sortDirections: ["descend", "ascend"],
            render: (text: string) =>
                text && text.length > 13 ? `${text.slice(0, 11)}...` : text,
        },
        {
            title: "Type",
            dataIndex: "type",
            key: "type",
            width: 80,
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
            width: 80,
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
            width: 75,
            filters: locationFilters,
            filterSearch: true,
        },
        {
            title: "Followers",
            dataIndex: "followers",
            key: "followers",
            width: 80,
            sorter: {
                multiple: 2,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Following",
            dataIndex: "following",
            key: "following",
            width: 80,
            sorter: {
                multiple: 2,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Repos",
            dataIndex: "public_repos",
            key: "repos",
            width: 65,
            sorter: {
                multiple: 1,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Sponsors",
            dataIndex: "total_sponsors",
            key: "sponsors",
            width: 85,
            sorter: {
                multiple: 2,
            },
            sortDirections: ["descend", "ascend"]
        },
        {
            title: "Sponsoring",
            dataIndex: "total_sponsoring",
            key: "sponsoring",
            width: 95,
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
            width: 130,
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
                // Ant Design's SorterResult can have a field as Key | readonly Key[]
                // We handle both cases by joining if it's an array.
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

    return (
        <>
            <section className='grid grid-cols-1 grid-rows-[_1.5fr,5fr] h-full px-4'>
                <div className='flex flex-col gap-3 w-full pb-5'>
                    <h1 className='text-[24px] font-semibold gap-3'>Leaderboard Statistics</h1>
                    <div className={styles.carouselContainer}>
                        <div className={styles.carouselTrack}>
                            {[
                                { title: "Total Users Tracked", value: "10,000+" },
                                { title: "Unique Sponsorships", value: "25,000+" },
                                { title: "Top Sponsored", value: "Neovim" },
                                { title: "Top Sponsoring", value: "Shopify" },
                                { title: "Total Users Tracked", value: "10,000+" },
                                { title: "Unique Sponsorships", value: "25,000+" },
                                { title: "Top Sponsored", value: "Neovim" },
                                { title: "Top Sponsoring", value: "Shopify" },
                            ].map((stat, index) => (
                                <div key={index} className='flex-shrink-0 h-full w-1/4 px-2'>
                                    <div className={`${styles.stats} flex-none`}>
                                        <h3>{stat.title}</h3>
                                        <h2>{stat.value}</h2>
                                    </div>
                                </div>
                            ))}
                        </div>
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
                                onClick: () => navigate(`/user/${record.id}`),
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