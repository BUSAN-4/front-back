import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Alert,
  CircularProgress,
} from '@mui/material';
import AuthLayout from '../../layouts/AuthLayout';
import { useAuthStore } from '../../store/authStore';
import type { UserRole } from '../../types/user';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    name: '',
    email: '',
    phone: '',
    role: 'general' as UserRole,
    adminCode: '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRoleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, role: e.target.value as UserRole, adminCode: '' }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }

    if (formData.role === 'city' && formData.adminCode !== 'BUSAN2024') {
      setError('부산시 관리자 인증 코드가 올바르지 않습니다.');
      return;
    }
    if (formData.role === 'admin' && formData.adminCode !== 'SYSTEM2024') {
      setError('시스템 관리자 인증 코드가 올바르지 않습니다.');
      return;
    }

    try {
      await login(formData.username, formData.password, formData.role);

      const users = JSON.parse(localStorage.getItem('users') || '[]');
      const newUser = {
        id: Date.now().toString(),
        username: formData.username,
        password: formData.password,
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        role: formData.role,
        createdAt: new Date().toISOString(),
      };
      users.push(newUser);
      localStorage.setItem('users', JSON.stringify(users));

      alert('회원가입이 완료되었습니다. 로그인되었습니다.');
      if (formData.role === 'general') navigate('/user/dashboard');
      else if (formData.role === 'city') navigate('/city/main');
      else if (formData.role === 'admin') navigate('/admin/main');
    } catch (err) {
      setError('회원가입 실패: 다시 시도해주세요.');
      console.error('Registration error:', err);
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
          width: '100%',
          maxWidth: 500,
        }}
      >
        <Typography variant="h4" gutterBottom align="center" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          회원가입
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <FormControl component="fieldset" margin="normal" fullWidth>
            <FormLabel component="legend" sx={{ fontWeight: 'bold', mb: 1 }}>사용자 유형</FormLabel>
            <RadioGroup
              row
              name="role"
              value={formData.role}
              onChange={handleRoleChange}
            >
              <FormControlLabel value="general" control={<Radio />} label="일반 사용자" />
              <FormControlLabel value="city" control={<Radio />} label="부산시 관리자" />
              <FormControlLabel value="admin" control={<Radio />} label="시스템 관리자" />
            </RadioGroup>
          </FormControl>

          <TextField
            fullWidth
            label="아이디"
            name="username"
            value={formData.username}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="이름"
            name="name"
            value={formData.name}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="비밀번호"
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="비밀번호 확인"
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="이메일"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="전화번호"
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            margin="normal"
            required
          />

          {(formData.role === 'city' || formData.role === 'admin') && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label={`${formData.role === 'city' ? '부산시 관리자' : '시스템 관리자'} 인증 코드`}
                name="adminCode"
                value={formData.adminCode}
                onChange={handleChange}
                margin="normal"
                required
              />
              <Alert severity="info" sx={{ mt: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  [임시 테스트용 인증 코드]
                </Typography>
                <Typography variant="body2">
                  {formData.role === 'city' ? '부산시 관리자: BUSAN2024' : '시스템 관리자: SYSTEM2024'}
                </Typography>
              </Alert>
            </Box>
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            sx={{ mt: 3, py: 1.5, fontWeight: 'bold' }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} color="inherit" /> : '회원가입'}
          </Button>
          <Box textAlign="center" sx={{ mt: 2 }}>
            <Link to="/login" style={{ textDecoration: 'none' }}>
              <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>
                이미 계정이 있으신가요? 로그인
              </Typography>
            </Link>
          </Box>
        </form>
      </Box>
    </AuthLayout>
  );
}

