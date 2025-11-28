import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  CardContent,
} from '@mui/material';
import CityLayout from '../../layouts/CityLayout';
import Card from '../../components/common/Card';
import PowerBIEmbedView from '../../components/common/powerbi/PowerBIEmbedView';
import { usePowerBI } from '../../hooks/usePowerBI';
import { useState } from 'react';

const SAFE_DRIVING_REPORT_ID = "safe-driving-report-id";

export default function CityDashboardSafeDriving() {
  const { config: powerBIConfig, loading: powerBILoading, error: powerBIError } = usePowerBI(SAFE_DRIVING_REPORT_ID);
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const summaryData = {
    avgSafetyScore: 87.5,
    registeredVehicles: 12811,
    totalMileage: '2.4M km',
    dangerousDrivingIncidents: 1247,
  };

  return (
    <CityLayout>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        안전운전 관리
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
          <Card title="평균 안전점수">
            <Typography variant="h3" color="primary" sx={{ fontWeight: 600 }}>
              {summaryData.avgSafetyScore}점
            </Typography>
            <Typography variant="body2" color="text.secondary">
              전월 대비 +2.3점
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="등록 차량 수">
            <Typography variant="h3" sx={{ fontWeight: 600 }}>
              {summaryData.registeredVehicles.toLocaleString()}대
            </Typography>
            <Typography variant="body2" color="text.secondary">
              활성 차량 기준
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="이번 달 총 주행거리">
            <Typography variant="h3" sx={{ fontWeight: 600 }}>
              {summaryData.totalMileage}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              11월 누적
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="위험운전 감지">
            <Typography variant="h3" sx={{ fontWeight: 600, color: 'error.main' }}>
              {summaryData.dangerousDrivingIncidents.toLocaleString()}건
            </Typography>
            <Typography variant="body2" color="text.secondary">
              전월 대비 -15%
            </Typography>
          </Card>
        </Box>
      </Box>

      <Card title="안전운전 현황 대시보드">
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="PowerBI dashboard tabs">
            <Tab label="월별 추이" />
            <Tab label="차량 유형별" />
            <Tab label="성별/연령별" />
            <Tab label="지역별 분포" />
          </Tabs>
        </Box>
        <CardContent>
          {powerBILoading ? (
            <Box display="flex" justifyContent="center" alignItems="center" sx={{ height: 400 }}>
              <CircularProgress />
              <Typography variant="h6" sx={{ ml: 2 }}>PowerBI 대시보드 로딩 중...</Typography>
            </Box>
          ) : powerBIError ? (
            <Alert severity="error">PowerBI 대시보드를 불러오는 데 실패했습니다: {powerBIError.message}</Alert>
          ) : (
            <PowerBIEmbedView config={powerBIConfig} height="600px" />
          )}
        </CardContent>
      </Card>
    </CityLayout>
  );
}

