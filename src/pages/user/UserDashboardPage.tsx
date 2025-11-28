import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  CardContent,
} from '@mui/material';
import {
  DirectionsCar,
  Warning,
  Speed,
  AccessTime,
} from '@mui/icons-material';
import UserLayout from '../../layouts/UserLayout';
import { useVehicle } from '../../hooks/useVehicle';
import type { SafetyScore } from '../../types/vehicle';
import Card from '../../components/common/Card';

export default function UserDashboardPage() {
  const navigate = useNavigate();
  const { vehicles, selectedVehicle, selectVehicle, fetchVehicles } = useVehicle();
  const [safetyScore, setSafetyScore] = useState<SafetyScore | null>(null);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    fetchVehicles().finally(() => setLoading(false));
  }, [fetchVehicles]);

  useEffect(() => {
    if (vehicles.length > 0 && !selectedVehicle) {
      selectVehicle(vehicles[0]);
    }
  }, [vehicles, selectedVehicle, selectVehicle]);

  useEffect(() => {
    if (selectedVehicle) {
      setTimeout(() => {
        setSafetyScore({
          overall: 85.5,
          drowsiness: 80.0,
          acceleration: 90.0,
          posture: 88.0,
        });
      }, 500);
    }
  }, [selectedVehicle]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const drivingHistory = [
    { date: '11/18', score: 82, drowsy: 2, rapid: 3 },
    { date: '11/19', score: 88, drowsy: 1, rapid: 2 },
    { date: '11/20', score: 85, drowsy: 0, rapid: 4 },
    { date: '11/21', score: 91, drowsy: 0, rapid: 1 },
    { date: '11/22', score: 87, drowsy: 1, rapid: 2 },
    { date: '11/23', score: 89, drowsy: 0, rapid: 1 },
    { date: '11/24', score: 85, drowsy: 2, rapid: 3 }
  ];

  const recentTrips = [
    { id: 1, date: '2025-11-24 09:30', distance: '15.2km', duration: '25분', score: 85 },
    { id: 2, date: '2025-11-23 18:15', distance: '8.7km', duration: '18분', score: 92 },
    { id: 3, date: '2025-11-23 08:45', distance: '12.4km', duration: '22분', score: 88 },
    { id: 4, date: '2025-11-22 17:30', distance: '20.1km', duration: '35분', score: 81 },
    { id: 5, date: '2025-11-22 09:00', distance: '15.8km', duration: '28분', score: 87 }
  ];

  if (loading) {
    return (
      <UserLayout>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </UserLayout>
    );
  }

  if (vehicles.length === 0) {
    return (
      <UserLayout>
        <Box sx={{ maxWidth: 800, mx: 'auto', mt: 8 }}>
          <Card title="차량을 등록해주세요">
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                <Box
                  sx={{
                    bgcolor: 'primary.light',
                    p: 3,
                    borderRadius: '50%',
                    display: 'inline-flex',
                  }}
                >
                  <DirectionsCar sx={{ fontSize: 48, color: 'primary.main' }} />
                </Box>
              </Box>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
                안전습관 점수 및 주행 통계를 확인하려면 차량 등록이 필요합니다
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/user/mypage')}
                sx={{ mt: 2, textTransform: 'none' }}
              >
                차량 등록하기
              </Button>
            </CardContent>
          </Card>
        </Box>
      </UserLayout>
    );
  }

  return (
    <UserLayout>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        안전운전 대시보드
      </Typography>

      {vehicles.length > 1 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mb: 1 }}>
            차량 선택
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {vehicles.map((vehicle) => (
              <Button
                key={vehicle.id}
                variant={selectedVehicle?.id === vehicle.id ? 'contained' : 'outlined'}
                onClick={() => selectVehicle(vehicle)}
                sx={{ textTransform: 'none' }}
              >
                {vehicle.licensePlate}
              </Button>
            ))}
          </Box>
        </Box>
      )}

      {selectedVehicle && safetyScore && (
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
            <Card title="종합 안전점수">
              <Typography variant="h3" color="primary" sx={{ fontWeight: 600, mb: 1 }}>
                {safetyScore.overall.toFixed(1)}점
              </Typography>
              <LinearProgress
                variant="determinate"
                value={safetyScore.overall}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Card>
          </Box>

          <Box>
            <Card title="이번 주 졸음운전">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Warning sx={{ color: 'warning.main', fontSize: 20 }} />
                <Typography variant="h3" sx={{ fontWeight: 600 }}>
                  6회
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                지난주 대비 -2회
              </Typography>
            </Card>
          </Box>

          <Box>
            <Card title="이번 주 급가속">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Speed sx={{ color: 'error.main', fontSize: 20 }} />
                <Typography variant="h3" sx={{ fontWeight: 600 }}>
                  16회
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                지난주 대비 +3회
              </Typography>
            </Card>
          </Box>

          <Box>
            <Card title="총 주행시간">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <AccessTime sx={{ color: 'success.main', fontSize: 20 }} />
                <Typography variant="h3" sx={{ fontWeight: 600 }}>
                  12.5시간
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                이번 주 누적
              </Typography>
            </Card>
          </Box>
        </Box>
      )}

      {selectedVehicle && (
        <Box>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange} sx={{ '& .MuiTab-root': { textTransform: 'none' } }}>
              <Tab label="안전점수 추이" />
              <Tab label="운전 이벤트" />
              <Tab label="주행 기록" />
            </Tabs>
          </Box>

          {tabValue === 0 && (
            <Card title="주간 안전점수 추이">
              <CardContent>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  최근 7일간의 안전운전 점수
                </Typography>
                <Alert severity="info">
                  차트 기능은 recharts 라이브러리 설치 후 구현 예정입니다.
                  <br />
                  데이터: {drivingHistory.map((d) => `${d.date}(${d.score}점)`).join(', ')}
                </Alert>
              </CardContent>
            </Card>
          )}

          {tabValue === 1 && (
            <Card title="운전 이벤트 발생 횟수">
              <CardContent>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  졸음운전 및 급가속 이벤트 추이
                </Typography>
                <Alert severity="info">
                  차트 기능은 recharts 라이브러리 설치 후 구현 예정입니다.
                  <br />
                  데이터: {drivingHistory.map((d) => `${d.date}(졸음:${d.drowsy}회, 급가속:${d.rapid}회)`).join(', ')}
                </Alert>
              </CardContent>
            </Card>
          )}

          {tabValue === 2 && (
            <Card title="최근 주행 기록">
              <CardContent>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  최근 5건의 주행 내역
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {recentTrips.map((trip) => (
                    <Box
                      key={trip.id}
                      sx={{
                        p: 2,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        bgcolor: 'background.paper',
                        '&:hover': {
                          bgcolor: 'action.hover',
                        },
                      }}
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                          {trip.date}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {trip.distance} · {trip.duration}
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: 'right', ml: 2 }}>
                        <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                          {trip.score}점
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={trip.score}
                          sx={{ width: 80, height: 6, borderRadius: 3, mt: 0.5 }}
                        />
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      )}

      {selectedVehicle && (
        <Box sx={{ mt: 3 }}>
          <Button
            variant="outlined"
            fullWidth
            onClick={() => navigate(`/user/trip-detail/${selectedVehicle.id}`)}
            sx={{ textTransform: 'none', py: 1.5 }}
          >
            주행 상세 조회
          </Button>
        </Box>
      )}
    </UserLayout>
  );
}

