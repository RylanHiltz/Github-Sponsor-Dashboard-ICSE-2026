import { createContext, useState } from 'react';
import type { ReactNode, Dispatch, SetStateAction } from 'react';

// Define the type for the context value
interface SearchContextType {
    searchTerm: string;
    setSearchTerm: Dispatch<SetStateAction<string>>;
}

// Create the context with a default value of undefined
export const SearchContext = createContext<SearchContextType | undefined>(undefined);


export const SearchProvider = ({ children }: { children: ReactNode }) => {
    const [searchTerm, setSearchTerm] = useState('');

    return (
        <SearchContext.Provider value={{ searchTerm, setSearchTerm }}>
            {children}
        </SearchContext.Provider>
    );
};