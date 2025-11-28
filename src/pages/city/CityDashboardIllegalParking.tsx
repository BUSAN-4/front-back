import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  InputAdornment,
  List,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  CardContent,
} from '@mui/material';
import { Search, Edit, LocalParking as LocalParkingIcon, DirectionsCar, CheckCircle, ErrorOutline } from '@mui/icons-material';
import CityLayout from '../../layouts/CityLayout';
import Card from '../../components/common/Card';
import PowerBIEmbedView from '../../components/common/powerbi/PowerBIEmbedView';
import { usePowerBI } from '../../hooks/usePowerBI';

interface Violation {
  id: string;
  plateNumber: string;
  location: string;
  date: string;
  time: string;
  count: number;
  status: 'confirmed' | 'pending';
}

const ILLEGAL_PARKING_REPORT_ID = "illegal-parking-report-id";

export default function CityDashboardIllegalParking() {
  const { config: powerBIConfig, loading: powerBILoading, error: powerBIError } = usePowerBI(ILLEGAL_PARKING_REPORT_ID);

  const [violations, setViolations] = useState<Violation[]>([
    { id: '1', plateNumber: '12가3456', location: '해운대구 우동', date: '2025-11-24', time: '14:30', count: 8, status: 'confirmed' },
    { id: '2', plateNumber: '34나5678', location: '수영구 광안동', date: '2025-11-24', time: '11:20', count: 5, status: 'confirmed' },
    { id: '3', plateNumber: '56다7890', location: '남구 대연동', date: '2025-11-23', time: '16:45', count: 12, status: 'confirmed' },
    { id: '4', plateNumber: '78라1234', location: '부산진구 전포동', date: '2025-11-23', time: '09:15', count: 3, status: 'pending' },
    { id: '5', plateNumber: '90마3456', location: '동래구 명륜동', date: '2025-11-22', time: '13:50', count: 7, status: 'pending' }
  ]);

  const [editingViolation, setEditingViolation] = useState<Violation | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [openDialog, setOpenDialog] = useState(false);

  const summaryData = {
    monthlyIncidents: 1634,
    habitualViolators: 127,
    hotspotAreas: 23,
    pendingReview: 45,
  };

  const handleOpenDialog = (violation: Violation) => {
    setEditingViolation(violation);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setEditingViolation(null);
    setOpenDialog(false);
  };

  const handleEditViolation = () => {
    if (!editingViolation) return;
    setViolations(prev =>
      prev.map(v => (v.id === editingViolation.id ? editingViolation : v))
    );
    handleCloseDialog();
    alert('위반 정보가 수정되었습니다.');
  };

  const filteredViolations = violations.filter(v =>
    v.plateNumber.toLowerCase().includes(searchTerm.toLowerCase()) || v.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <CityLayout>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        불법주정차 단속 관리
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
          <Card title="이번 달 총 단속 건수">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <LocalParkingIcon sx={{ color: '#ef5350', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600, color: '#ef5350' }}>
                {summaryData.monthlyIncidents.toLocaleString()}건
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              전월 대비 -13.6%
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="상습 위반 차량">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <DirectionsCar sx={{ color: '#ff9800', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {summaryData.habitualViolators}대
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              5회 이상 위반
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="다발 구역">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <ErrorOutline sx={{ color: '#2196f3', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {summaryData.hotspotAreas}곳
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              집중 단속 필요
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="수정 대기">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <CheckCircle sx={{ color: '#4caf50', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600, color: '#4caf50' }}>
                {summaryData.pendingReview}건
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              정보 불일치
            </Typography>
          </Card>
        </Box>
      </Box>

      <Card title="불법주정차 현황 대시보드" sx={{ mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs value={0} onChange={() => {}} aria-label="PowerBI dashboard tabs">
            <Tab label="현황 대시보드" />
            <Tab label="다발 구역" />
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

      <Card title="위반 정보 관리">
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>탐지된 위반 목록</Typography>
            <TextField
              variant="outlined"
              size="small"
              placeholder="차량번호 또는 위치 검색"
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
          {filteredViolations.length === 0 ? (
            <Alert severity="info">검색 결과가 없습니다.</Alert>
          ) : (
            <List>
              {filteredViolations.map((violation) => (
                <Box key={violation.id} sx={{
                  mb: 1, p: 2, border: 1, borderColor: 'divider', borderRadius: 1,
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  bgcolor: 'background.paper',
                }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{violation.plateNumber}</Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            px: 1, py: 0.5, borderRadius: 1,
                            bgcolor: violation.status === 'confirmed' ? 'success.light' : 'warning.light',
                            color: violation.status === 'confirmed' ? 'success.contrastText' : 'warning.contrastText',
                            fontWeight: 'bold',
                          }}
                        >
                          {violation.status === 'confirmed' ? '확인됨' : '검토필요'}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.secondary" display="block">
                          {violation.location} | {violation.date} {violation.time}
                        </Typography>
                        <Typography component="span" variant="caption" color="text.secondary" display="block">
                          위반 횟수: {violation.count}회
                        </Typography>
                      </>
                    }
                  />
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => handleOpenDialog(violation)}
                    sx={{ textTransform: 'none' }}
                  >
                    수정
                  </Button>
                </Box>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', fontWeight: 'bold' }}>
          위반 정보 수정
        </DialogTitle>
        {editingViolation && (
          <DialogContent dividers>
            <TextField
              fullWidth
              label="차량 번호"
              name="plateNumber"
              value={editingViolation.plateNumber}
              onChange={(e) => setEditingViolation({ ...editingViolation, plateNumber: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="위반 위치"
              name="location"
              value={editingViolation.location}
              onChange={(e) => setEditingViolation({ ...editingViolation, location: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="날짜"
              name="date"
              type="date"
              value={editingViolation.date}
              onChange={(e) => setEditingViolation({ ...editingViolation, date: e.target.value })}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="시간"
              name="time"
              type="time"
              value={editingViolation.time}
              onChange={(e) => setEditingViolation({ ...editingViolation, time: e.target.value })}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="위반 횟수"
              name="count"
              type="number"
              value={editingViolation.count}
              onChange={(e) => setEditingViolation({ ...editingViolation, count: parseInt(e.target.value) })}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>상태</InputLabel>
              <Select
                label="상태"
                name="status"
                value={editingViolation.status}
                onChange={(e) => setEditingViolation({ ...editingViolation, status: e.target.value as Violation['status'] })}
              >
                <MenuItem value="confirmed">확인됨</MenuItem>
                <MenuItem value="pending">검토필요</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
        )}
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCloseDialog} variant="outlined" sx={{ textTransform: 'none' }}>
            취소
          </Button>
          <Button onClick={handleEditViolation} variant="contained" sx={{ textTransform: 'none' }}>
            수정 완료
          </Button>
        </DialogActions>
      </Dialog>
    </CityLayout>
  );
}

