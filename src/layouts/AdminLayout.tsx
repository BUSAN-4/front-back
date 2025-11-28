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
  Divider,
  Avatar,
} from '@mui/material';
import { useAuthStore } from '../store/authStore';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const getTabValue = () => {
    if (location.pathname.includes('users')) return 1;
    if (location.pathname.includes('logs')) return 2;
    return 0;
  };

  const [tabValue, setTabValue] = useState(getTabValue());

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    const routes = ['/admin/main', '/admin/users', '/admin/logs'];
    navigate(routes[newValue]);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <AppBar position="static" elevation={1} sx={{ bgcolor: '#1976d2' }}>
        <Toolbar sx={{ px: 3 }}>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
            시스템 관리자
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', mr: 1 }}>{user?.username?.[0]?.toUpperCase()}</Avatar>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
              {user?.name || user?.username}
            </Typography>
            <Divider orientation="vertical" flexItem sx={{ bgcolor: 'rgba(255,255,255,0.3)' }} />
            <Button 
              color="inherit" 
              onClick={handleLogout}
              sx={{ 
                textTransform: 'none',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }
              }}
            >
              로그아웃
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Box sx={{ bgcolor: 'white', borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          sx={{ 
            px: 3,
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 500,
              minHeight: 48,
            }
          }}
        >
          <Tab label="대시보드" />
          <Tab label="사용자 관리" />
          <Tab label="로그 모니터링" />
        </Tabs>
      </Box>
      <Box sx={{ flex: 1, p: 3 }}>{children}</Box>
    </Box>
  );
}

