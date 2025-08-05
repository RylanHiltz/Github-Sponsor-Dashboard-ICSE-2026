import React, { useState } from "react"
import { Input, Button } from "antd"
import { SearchOutlined } from "@ant-design/icons"

interface SearchProps {
    onSubmit: (search: string) => void;
}

const Search: React.FC<SearchProps> = ({ onSubmit }) => {

    // TODO: Add sticky text to search bar so when you come back to the page after vewing another user the seach result stays in the search bar
    const [search, setSearch] = useState("")

    return (
        <>
            <Input style={{ width: 'calc(50% - 85px)' }} className='min-w-[150px]' placeholder='Search by name or username' onChange={e => setSearch(e.target.value)} onKeyDown={
                e => {
                    if (e.key == "Enter") {
                        onSubmit(search);
                    }
                }} />
            <Button type='text' className={`p-2 flex whitespace-nowrap w-min gap-1`} iconPosition='end' size="middle" icon={<SearchOutlined className='text-[16px]' />} onClick={() => onSubmit(search)}>Search</Button >
        </>
    )
}

export default Search