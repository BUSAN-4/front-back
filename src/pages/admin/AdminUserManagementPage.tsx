import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  InputAdornment,
  List,
  ListItemText,
  IconButton,
  Alert,
  CircularProgress,
  CardContent,
} from '@mui/material';
import { Search, Edit, Delete, Add } from '@mui/icons-material';
import AdminLayout from '../../layouts/AdminLayout';
import Card from '../../components/common/Card';
import { useAuthStore } from '../../store/authStore';

export default function AdminUserManagementPage() {
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

  const filteredUsers = users.filter(u =>
    u.username.toLowerCase().includes(searchTerm.toLowerCase()) || 
    u.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchTerm.toLowerCase())
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
        사용자 관리
      </Typography>

      <Card title="사용자 계정 관리">
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>전체 사용자 목록</Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
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
              <Button
                variant="contained"
                startIcon={<Add />}
                sx={{ textTransform: 'none' }}
                disabled
              >
                사용자 추가
              </Button>
            </Box>
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
                          {u.name} | {u.email} | {u.phone || '-'}
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
    </AdminLayout>
  );
}

