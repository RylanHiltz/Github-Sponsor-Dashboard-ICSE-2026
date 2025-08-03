import { useEffect, useState } from 'react'
import { Button } from 'antd'
import { MdDarkMode, MdLightMode } from 'react-icons/md'

import { useTheme } from '../context/ThemeContext';


const DarkmodeButton = () => {

    const { theme, toggleTheme } = useTheme();
    return (
        <Button
            className='h-[32px] w-[32px] p-0 bg-[--dark-gray] flex items-center justify-center'
            onClick={toggleTheme}
        >
            {theme === 'dark' ? (
                <MdDarkMode className='text-[20px]' />
            ) : (
                <MdLightMode className='text-[20px]' />
            )}
        </Button>
    )
}
export default DarkmodeButton