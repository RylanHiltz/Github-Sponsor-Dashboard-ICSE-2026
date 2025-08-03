import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router'
import Dashboard from './pages/Dashboard'
import Statistics from './pages/statistics/Statistics';
import Leaderboard from './pages/leaderboard/Leaderboard';
import User from './pages/users/User';
import { ConfigProvider, theme as antdTheme } from 'antd'

import { ThemeProvider, useTheme } from './context/ThemeContext';
import { theme as appTheme } from './theme.ts';

// A new component to access the context provided by ThemeProvider
const ThemedApp = () => {
  const { theme } = useTheme();

  return (
    <ConfigProvider
      theme={{
        algorithm: theme === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        token: {
          // Primary Color
          colorPrimary: theme === 'dark'
            ? appTheme.extend.colors.primary.dark
            : appTheme.extend.colors.primary.light,

          colorBgContainer: theme === 'dark' ? '#141414' : '#fff',
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Dashboard />}>
            <Route path='' element={<Leaderboard />} />
            <Route path="/user/:id" element={<User />} />
            <Route path='statistics' element={<Statistics />} />
            <Route path='request-user' element={<Statistics />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default function App() {
  return (
    // Wrap the entire app in the ThemeProvider
    <ThemeProvider>
      <ThemedApp />
    </ThemeProvider>
  );
}
