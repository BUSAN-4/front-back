import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  List,
  ListItemText,
  IconButton,
  Alert,
  CircularProgress,
  CardContent,
} from '@mui/material';
import { Search, Edit, Delete, Group, CheckCircle, Storage, Api } from '@mui/icons-material';
import AdminLayout from '../../layouts/AdminLayout';
import Card from '../../components/common/Card';
import { useAuthStore } from '../../store/authStore';

export default function AdminDashboardPage() {
  const { user } = useAuthStore();
  const [users, setUsers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      const allUsers = JSON.parse(localStorage.getItem('users') || '[]');
      setUsers(allUsers);
      setLoading(false);
    };
    fetchUsers();
  }, []);

  const userActivityLogs = [
    { id: 1, username: 'user01', action: '로그인', timestamp: '2025-11-25 10:45:23', ip: '192.168.1.100' },
    { id: 2, username: 'city1', action: '대시보드 조회', timestamp: '2025-11-25 10:42:15', ip: '192.168.1.101' },
    { id: 3, username: 'user02', action: '차량 등록', timestamp: '2025-11-25 10:38:47', ip: '192.168.1.102' },
    { id: 4, username: 'city1', action: '위반정보 수정', timestamp: '2025-11-25 10:35:12', ip: '192.168.1.101' },
    { id: 5, username: 'user03', action: '로그아웃', timestamp: '2025-11-25 10:30:56', ip: '192.168.1.103' }
  ];

  const filteredUsers = users.filter(u =>
    u.username.toLowerCase().includes(searchTerm.toLowerCase()) || u.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDeleteUser = (userId: string) => {
    if (window.confirm('정말 이 사용자를 삭제하시겠습니까?')) {
      const updatedUsers = users.filter(u => u.id !== userId);
      setUsers(updatedUsers);
      localStorage.setItem('users', JSON.stringify(updatedUsers));
      alert('사용자가 삭제되었습니다.');
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        시스템 관리자 대시보드
      </Typography>

      <Box
        sx={{
          display: 'grid',
          gap: 3,
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(4, 1fr)',
          },
          mb: 4,
        }}
      >
        <Box>
          <Card title="전체 사용자">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Group sx={{ color: '#1976d2', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {users.length}명
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              일반: {users.filter(u => u.role === 'general').length} |
              부산시: {users.filter(u => u.role === 'city').length} |
              시스템: {users.filter(u => u.role === 'admin').length}
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="시스템 상태">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <CheckCircle sx={{ color: '#4caf50', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600, color: '#4caf50' }}>
                정상
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              가동률 99.8%
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="데이터베이스">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Storage sx={{ color: '#9c27b0', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                2.4TB
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              사용률 68%
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="API 요청">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Api sx={{ color: '#ff9800', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                12.5K
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              오늘
            </Typography>
          </Card>
        </Box>
      </Box>

      <Card title="사용자 관리" sx={{ mb: 4 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>전체 사용자 목록</Typography>
            <TextField
              variant="outlined"
              size="small"
              placeholder="사용자 검색"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ width: 250 }}
            />
          </Box>
          {filteredUsers.length === 0 ? (
            <Alert severity="info">검색 결과가 없습니다.</Alert>
          ) : (
            <List>
              {filteredUsers.map((u) => (
                <Box key={u.id} sx={{
                  mb: 1, p: 2, border: 1, borderColor: 'divider', borderRadius: 1,
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  bgcolor: 'background.paper',
                }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{u.username}</Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            px: 1, py: 0.5, borderRadius: 1,
                            bgcolor: u.role === 'admin' ? 'primary.light' : u.role === 'city' ? 'info.light' : 'grey.300',
                            color: u.role === 'admin' ? 'primary.contrastText' : u.role === 'city' ? 'info.contrastText' : 'grey.800',
                            fontWeight: 'bold',
                          }}
                        >
                          {u.role === 'admin' ? '시스템 관리자' : u.role === 'city' ? '부산시 관리자' : '일반 사용자'}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.secondary" display="block">
                          {u.name} | {u.email}
                        </Typography>
                        <Typography component="span" variant="caption" color="text.secondary" display="block">
                          가입일: {new Date(u.createdAt).toLocaleDateString('ko-KR')}
                        </Typography>
                      </>
                    }
                  />
                  <Box>
                    <IconButton size="small" disabled>
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteUser(u.id)}
                      disabled={u.id === user?.id}
                    >
                      <Delete fontSize="small" color="error" />
                    </IconButton>
                  </Box>
                </Box>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Card title="사용자 활동 로그">
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>최근 활동 내역</Typography>
          <List>
            {userActivityLogs.map((log) => (
              <Box key={log.id} sx={{
                mb: 1, p: 2, border: 1, borderColor: 'divider', borderRadius: 1,
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                bgcolor: 'background.paper',
              }}>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{log.username}</Typography>
                      <Typography component="span" variant="body2" color="text.secondary">→</Typography>
                      <Typography component="span" variant="body2">{log.action}</Typography>
                    </Box>
                  }
                  secondary={
                    <Typography component="span" variant="caption" color="text.secondary" display="block">
                      {log.timestamp} | IP: {log.ip}
                    </Typography>
                  }
                />
              </Box>
            ))}
          </List>
        </CardContent>
      </Card>
    </AdminLayout>
  );
}

