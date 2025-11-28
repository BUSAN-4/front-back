import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
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
import { ArrowBack } from '@mui/icons-material';
import UserLayout from '../../layouts/UserLayout';
import { useVehicle } from '../../hooks/useVehicle';
import { formatDateTime } from '../../utils/helpers';
import Card from '../../components/common/Card';

export default function UserTripDetailPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const navigate = useNavigate();
  const { selectedVehicle, tripRecords, fetchTripRecords, isLoading } = useVehicle();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (vehicleId) {
      fetchTripRecords(vehicleId).finally(() => setLoading(false));
    }
  }, [vehicleId, fetchTripRecords]);

  if (loading || isLoading) {
    return (
      <UserLayout>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </UserLayout>
    );
  }

  if (!selectedVehicle) {
    return (
      <UserLayout>
        <Alert severity="error">차량 정보를 찾을 수 없습니다.</Alert>
      </UserLayout>
    );
  }

  return (
    <UserLayout>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/user/dashboard')}
          sx={{ textTransform: 'none' }}
        >
          뒤로가기
        </Button>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          주행 상세 조회 - {selectedVehicle.licensePlate}
        </Typography>
      </Box>

      {tripRecords.length === 0 ? (
        <Alert severity="info">주행 기록이 없습니다.</Alert>
      ) : (
        <Card title="주행 기록">
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>시작 시간</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>종료 시간</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="right">주행 거리 (km)</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="right">주행 시간 (분)</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="right">안전 점수</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="right">졸음 횟수</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="right">급가속 횟수</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>위치</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tripRecords.map((record) => (
                    <TableRow key={record.id} hover>
                      <TableCell>{formatDateTime(record.startTime)}</TableCell>
                      <TableCell>{formatDateTime(record.endTime)}</TableCell>
                      <TableCell align="right">{record.distance.toFixed(1)}</TableCell>
                      <TableCell align="right">{Math.floor(record.duration / 60)}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold', color: record.safetyScore >= 90 ? 'success.main' : record.safetyScore >= 80 ? 'warning.main' : 'error.main' }}>
                        {record.safetyScore.toFixed(1)}
                      </TableCell>
                      <TableCell align="right">{record.drowsinessCount}</TableCell>
                      <TableCell align="right">{record.suddenAccelerationCount}</TableCell>
                      <TableCell>{record.location || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </UserLayout>
  );
}

