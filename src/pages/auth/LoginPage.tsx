import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import AuthLayout from '../../layouts/AuthLayout';
import { useAuthStore } from '../../store/authStore';
import type { UserRole } from '../../types/user';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('general');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(username, password, role);
      if (role === 'general') navigate('/user/dashboard');
      else if (role === 'city') navigate('/city/main');
      else if (role === 'admin') navigate('/admin/main');
    } catch (err) {
      setError('로그인 실패: 아이디 또는 비밀번호를 확인해주세요.');
      console.error('Login error:', err);
    }
  };

  return (
    <AuthLayout>
      <Box
        sx={{
          bgcolor: 'white',
          p: 4,
          borderRadius: 2,
          boxShadow: 3,
        }}
      >
        <Typography variant="h4" gutterBottom align="center" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          로그인
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
          테스트 계정: 아이디 (user1, city1, admin1 등 아무거나), 비밀번호 (아무거나)
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="아이디"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="비밀번호"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
          />
          <TextField
            select
            fullWidth
            label="역할 선택"
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            margin="normal"
            sx={{ mb: 3 }}
            SelectProps={{
              native: true,
            }}
          >
            <option value="general">일반 사용자</option>
            <option value="city">부산시 관리자</option>
            <option value="admin">시스템 관리자</option>
          </TextField>
          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            sx={{ mb: 2, py: 1.5, fontWeight: 'bold' }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} color="inherit" /> : '로그인'}
          </Button>
          <Box textAlign="center">
            <Link to="/register" style={{ textDecoration: 'none' }}>
              <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>
                계정이 없으신가요? 회원가입
              </Typography>
            </Link>
          </Box>
        </form>
      </Box>
    </AuthLayout>
  );
}

