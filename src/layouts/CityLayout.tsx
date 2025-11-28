import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
} from '@mui/material';
import { DirectionsCar, LocalParking, PersonSearch } from '@mui/icons-material';
import { useAuthStore } from '../store/authStore';

interface CityLayoutProps {
  children: React.ReactNode;
}

const menuItems = [
  { label: '안전운전관리', path: '/city/safe-driving', icon: DirectionsCar },
  { label: '불법주정차 단속 관리', path: '/city/illegal-parking', icon: LocalParking },
  { label: '실종자 관리', path: '/city/missing-person', icon: PersonSearch },
];

export default function CityLayout({ children }: CityLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleMenuClick = (path: string) => {
    navigate(path);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <AppBar 
        position="fixed" 
        elevation={1}
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          bgcolor: '#1976d2',
          width: '100%',
        }}
      >
        <Toolbar sx={{ px: 3 }}>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
            부산시 스마트 도시 차량 서비스
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

      <Box
        component="nav"
        sx={{
          width: 280,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: 280, boxSizing: 'border-box' },
          mt: '64px',
        }}
      >
        <Box
          sx={{
            height: 'calc(100vh - 64px)',
            bgcolor: '#2c3e50',
            color: 'white',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 2,
            pt: 2,
          }}
        >
          <List component="nav" sx={{ flexGrow: 1 }}>
            {menuItems.map((item) => (
              <ListItem key={item.label} disablePadding>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => handleMenuClick(item.path)}
                  sx={{
                    '&.Mui-selected': {
                      bgcolor: 'primary.main',
                      '&:hover': {
                        bgcolor: 'primary.dark',
                      },
                    },
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                    py: 1.5,
                    px: 3,
                  }}
                >
                  <ListItemIcon sx={{ color: 'inherit' }}>
                    <item.icon />
                  </ListItemIcon>
                  <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: 500 }} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: '64px',
          width: 'calc(100% - 280px)',
        }}
      >
        {children}
      </Box>
    </Box>
  );
}

