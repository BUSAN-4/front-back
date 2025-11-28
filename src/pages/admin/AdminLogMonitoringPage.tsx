import { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  List,
  ListItemText,
  Alert,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import AdminLayout from '../../layouts/AdminLayout';
import Card from '../../components/common/Card';

interface LogEntry {
  id: number;
  username: string;
  action: string;
  timestamp: string;
  ip: string;
  status: 'success' | 'error' | 'warning';
}

export default function AdminLogMonitoringPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const logs: LogEntry[] = [
    { id: 1, username: 'user01', action: '로그인', timestamp: '2025-11-25 10:45:23', ip: '192.168.1.100', status: 'success' },
    { id: 2, username: 'city1', action: '대시보드 조회', timestamp: '2025-11-25 10:42:15', ip: '192.168.1.101', status: 'success' },
    { id: 3, username: 'user02', action: '차량 등록', timestamp: '2025-11-25 10:38:47', ip: '192.168.1.102', status: 'success' },
    { id: 4, username: 'city1', action: '위반정보 수정', timestamp: '2025-11-25 10:35:12', ip: '192.168.1.101', status: 'success' },
    { id: 5, username: 'user03', action: '로그인 실패', timestamp: '2025-11-25 10:30:56', ip: '192.168.1.103', status: 'error' },
    { id: 6, username: 'admin1', action: '사용자 삭제', timestamp: '2025-11-25 10:25:33', ip: '192.168.1.104', status: 'warning' },
    { id: 7, username: 'user04', action: '로그아웃', timestamp: '2025-11-25 10:20:11', ip: '192.168.1.105', status: 'success' },
    { id: 8, username: 'city2', action: '실종자 정보 수정', timestamp: '2025-11-25 10:15:44', ip: '192.168.1.106', status: 'success' },
  ];

  const filteredLogs = logs.filter(log =>
    log.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.ip.includes(searchTerm)
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success.main';
      case 'error':
        return 'error.main';
      case 'warning':
        return 'warning.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <AdminLayout>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        로그 모니터링
      </Typography>

      <Card title="시스템 접속 및 행동 로그">
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>전체 로그 목록</Typography>
            <TextField
              variant="outlined"
              size="small"
              placeholder="사용자명, 액션, IP 검색"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ width: 300 }}
            />
          </Box>
          {filteredLogs.length === 0 ? (
            <Alert severity="info">검색 결과가 없습니다.</Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>시간</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>사용자</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>액션</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>IP 주소</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="center">상태</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredLogs.map((log) => (
                    <TableRow key={log.id} hover>
                      <TableCell>{log.timestamp}</TableCell>
                      <TableCell>{log.username}</TableCell>
                      <TableCell>{log.action}</TableCell>
                      <TableCell>{log.ip}</TableCell>
                      <TableCell align="center">
                        <Typography
                          variant="caption"
                          sx={{
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                            bgcolor: getStatusColor(log.status),
                            color: 'white',
                            fontWeight: 'bold',
                          }}
                        >
                          {log.status === 'success' ? '성공' : log.status === 'error' ? '오류' : '경고'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </AdminLayout>
  );
}

