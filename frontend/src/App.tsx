import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router'
import Dashboard from './pages/Dashboard'
import Statistics from './pages/statistics/Statistics';
import Leaderboard from './pages/leaderboard/Leaderboard';
import User from './pages/users/User';
import { ConfigProvider, theme as antdTheme } from 'antd'


export default function App() {

  const [darkMode, setDarkMode] = useState(true); // Or get from local storage

  const theme = {
    algorithm: darkMode ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
  };

  return (
    <ConfigProvider
      theme={theme}
    //   token: {
    //   },
    //   components: {
    //     Button: {
    //       colorPrimary: "#111",
    //       algorithm: true,
    //     },
    //     Input: {
    //       activeBorderColor: "#111",
    //       hoverBorderColor: "#111",
    //       activeShadow: "0 0 0 2px rgba(0,0,0,0.1)",
    //       algorithm: true,
    //     },
    //     Select: {
    //       activeBorderColor: "#111",
    //       activeOutlineColor: "rgba(0,0,0,0.1)",
    //       hoverBorderColor: "#111",
    //       optionSelectedBg: "#ebebeb",
    //       algorithm: true,
    //     },
    //     Upload: {
    //       colorPrimary: "#111",
    //       borderRadius: 10,
    //       lineWidth: 1.2,
    //       algorithm: true,
    //     },
    //     Checkbox: {
    //       colorPrimary: "#111",
    //       colorPrimaryHover: "#111",
    //     }
    //   },
    // }}
    >
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Dashboard />}>
            <Route path='' element={<Leaderboard />}></Route>
            <Route
              path="/user/:id"
              element={<User />
              }
            />
            <Route path='statistics' element={<Statistics />}></Route>
            <Route path='request-user' element={<Statistics />}></Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider >
  )
}

