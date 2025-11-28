import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Tabs,
  Tab,
  Avatar,
  Divider,
} from '@mui/material';
import { useAuthStore } from '../store/authStore';

interface UserLayoutProps {
  children: React.ReactNode;
}

export default function UserLayout({ children }: UserLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [tabValue, setTabValue] = useState(
    location.pathname.includes('mypage') ? 1 : 0
  );

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    if (newValue === 0) {
      navigate('/user/dashboard');
    } else {
      navigate('/user/mypage');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static" sx={{ bgcolor: 'primary.main' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            부산시 스마트 도시 차량 서비스
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: 'secondary.main', mr: 1 }}>{user?.username?.[0]?.toUpperCase()}</Avatar>
            <Typography sx={{ mr: 2 }}>{user?.name || user?.username}</Typography>
            <Button color="inherit" onClick={handleLogout} sx={{ bgcolor: 'rgba(255,255,255,0.1)', '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' } }}>
              로그아웃
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Tabs
        value={tabValue}
        onChange={handleTabChange}
        sx={{
          bgcolor: 'white',
          borderBottom: 1,
          borderColor: 'divider',
          '& .MuiTab-root': {
            fontWeight: 'bold',
            color: 'text.secondary',
            '&.Mui-selected': {
              color: 'primary.main',
            },
          },
          '& .MuiTabs-indicator': {
            backgroundColor: 'primary.main',
          },
        }}
      >
        <Tab label="메인" />
        <Tab label="마이페이지" />
      </Tabs>
      <Box sx={{ flex: 1, p: 3 }}>{children}</Box>
    </Box>
  );
}

