import React from "react"
import { Input } from "antd"
import { useContext } from "react"
import { SearchContext } from '../context/SearchContext';

interface SearchProps {
    onSubmit: (search: string) => void;
}

const Search: React.FC<SearchProps> = ({ onSubmit }) => {

    const searchContext = useContext(SearchContext);

    if (!searchContext) {
        throw new Error("Search component must be used within a SearchProvider");
    }

    const { searchTerm, setSearchTerm } = searchContext;

    const handleSearch = () => {
        onSubmit(searchTerm);
    };

    return (
        <>
            <Input
                value={searchTerm}
                className='min-w-[300px] w-[50%]'
                placeholder='Search by name or username'
                onChange={e => setSearchTerm(e.target.value)}
                onKeyDown={
                    e => {
                        if (e.key == "Enter") {
                            handleSearch();
                        }
                    }
                }
            />

        </>
    )
}

export default Search