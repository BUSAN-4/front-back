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
  CardContent,
} from '@mui/material';
import { Search, Edit, PersonSearch as PersonSearchIcon, CheckCircle, ErrorOutline } from '@mui/icons-material';
import CityLayout from '../../layouts/CityLayout';
import Card from '../../components/common/Card';
import PowerBIEmbedView from '../../components/common/powerbi/PowerBIEmbedView';
import { usePowerBI } from '../../hooks/usePowerBI';

interface MissingPerson {
  id: string;
  name: string;
  age: number;
  gender: string;
  detectedLocation: string;
  detectedDate: string;
  detectedTime: string;
  status: 'confirmed' | 'false-positive' | 'pending';
}

const MISSING_PERSON_REPORT_ID = "missing-person-report-id";

export default function CityDashboardMissingPerson() {
  const { config: powerBIConfig, loading: powerBILoading, error: powerBIError } = usePowerBI(MISSING_PERSON_REPORT_ID);

  const [missingPersons, setMissingPersons] = useState<MissingPerson[]>([
    { id: '1', name: '김○○', age: 12, gender: '여', detectedLocation: '해운대구 우동', detectedDate: '2025-11-24', detectedTime: '15:30', status: 'confirmed' },
    { id: '2', name: '이○○', age: 78, gender: '남', detectedLocation: '수영구 광안동', detectedDate: '2025-11-23', detectedTime: '18:45', status: 'confirmed' },
    { id: '3', name: '박○○', age: 45, gender: '여', detectedLocation: '남구 대연동', detectedDate: '2025-11-23', detectedTime: '10:20', status: 'false-positive' },
    { id: '4', name: '최○○', age: 8, gender: '남', detectedLocation: '부산진구 전포동', detectedDate: '2025-11-22', detectedTime: '14:15', status: 'pending' },
    { id: '5', name: '정○○', age: 82, gender: '여', detectedLocation: '동래구 명륜동', detectedDate: '2025-11-22', detectedTime: '09:30', status: 'confirmed' }
  ]);

  const [editingPerson, setEditingPerson] = useState<MissingPerson | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [openDialog, setOpenDialog] = useState(false);

  const summaryData = {
    monthlyReport: 25,
    foundCount: 21,
    avgFoundTime: 4.2,
    pendingReview: 8,
  };

  const handleOpenDialog = (person: MissingPerson) => {
    setEditingPerson(person);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setEditingPerson(null);
    setOpenDialog(false);
  };

  const handleEditPerson = () => {
    if (!editingPerson) return;
    setMissingPersons(prev =>
      prev.map(p => (p.id === editingPerson.id ? editingPerson : p))
    );
    handleCloseDialog();
    alert('실종자 정보가 수정되었습니다.');
  };

  const filteredPersons = missingPersons.filter(p =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) || p.detectedLocation.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <CityLayout>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        실종자 관리
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
          <Card title="이번 달 실종 신고">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <PersonSearchIcon sx={{ color: '#ff9800', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600, color: '#ff9800' }}>
                {summaryData.monthlyReport}건
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              전월 대비 -13.8%
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="발견 건수">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <CheckCircle sx={{ color: '#4caf50', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600, color: '#4caf50' }}>
                {summaryData.foundCount}건
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              발견율 84%
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="평균 발견 시간">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {summaryData.avgFoundTime}시간
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              전월 대비 -1.3시간
            </Typography>
          </Card>
        </Box>

        <Box>
          <Card title="검토 필요">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <ErrorOutline sx={{ color: '#2196f3', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontWeight: 600, color: '#2196f3' }}>
                {summaryData.pendingReview}건
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              오탐지 확인 중
            </Typography>
          </Card>
        </Box>
      </Box>

      <Card title="실종자 현황 대시보드" sx={{ mb: 4 }}>
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

      <Card title="탐지 정보 관리">
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>탐지된 실종자 목록</Typography>
            <TextField
              variant="outlined"
              size="small"
              placeholder="이름 또는 위치 검색"
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
          {filteredPersons.length === 0 ? (
            <Alert severity="info">검색 결과가 없습니다.</Alert>
          ) : (
            <List>
              {filteredPersons.map((person) => (
                <Box key={person.id} sx={{
                  mb: 1, p: 2, border: 1, borderColor: 'divider', borderRadius: 1,
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  bgcolor: 'background.paper',
                }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{person.name}</Typography>
                        <Typography component="span" variant="body2" color="text.secondary">
                          ({person.age}세, {person.gender})
                        </Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            px: 1, py: 0.5, borderRadius: 1,
                            bgcolor: person.status === 'confirmed' ? 'success.light' : person.status === 'false-positive' ? 'error.light' : 'warning.light',
                            color: person.status === 'confirmed' ? 'success.contrastText' : person.status === 'false-positive' ? 'error.contrastText' : 'warning.contrastText',
                            fontWeight: 'bold',
                          }}
                        >
                          {person.status === 'confirmed' ? '확인됨' : person.status === 'false-positive' ? '오탐지' : '검토필요'}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.secondary" display="block">
                          탐지 위치: {person.detectedLocation}
                        </Typography>
                        <Typography component="span" variant="caption" color="text.secondary" display="block">
                          {person.detectedDate} {person.detectedTime}
                        </Typography>
                      </>
                    }
                  />
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => handleOpenDialog(person)}
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
          실종자 정보 수정
        </DialogTitle>
        {editingPerson && (
          <DialogContent dividers>
            <TextField
              fullWidth
              label="이름"
              name="name"
              value={editingPerson.name}
              onChange={(e) => setEditingPerson({ ...editingPerson, name: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="나이"
              name="age"
              type="number"
              value={editingPerson.age}
              onChange={(e) => setEditingPerson({ ...editingPerson, age: parseInt(e.target.value) })}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>성별</InputLabel>
              <Select
                label="성별"
                name="gender"
                value={editingPerson.gender}
                onChange={(e) => setEditingPerson({ ...editingPerson, gender: e.target.value as string })}
              >
                <MenuItem value="남">남</MenuItem>
                <MenuItem value="여">여</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="탐지 위치"
              name="detectedLocation"
              value={editingPerson.detectedLocation}
              onChange={(e) => setEditingPerson({ ...editingPerson, detectedLocation: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="날짜"
              name="detectedDate"
              type="date"
              value={editingPerson.detectedDate}
              onChange={(e) => setEditingPerson({ ...editingPerson, detectedDate: e.target.value })}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="시간"
              name="detectedTime"
              type="time"
              value={editingPerson.detectedTime}
              onChange={(e) => setEditingPerson({ ...editingPerson, detectedTime: e.target.value })}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>상태</InputLabel>
              <Select
                label="상태"
                name="status"
                value={editingPerson.status}
                onChange={(e) => setEditingPerson({ ...editingPerson, status: e.target.value as MissingPerson['status'] })}
              >
                <MenuItem value="confirmed">확인됨</MenuItem>
                <MenuItem value="pending">검토필요</MenuItem>
                <MenuItem value="false-positive">오탐지</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
        )}
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCloseDialog} variant="outlined" sx={{ textTransform: 'none' }}>
            취소
          </Button>
          <Button onClick={handleEditPerson} variant="contained" sx={{ textTransform: 'none' }}>
            수정 완료
          </Button>
        </DialogActions>
      </Dialog>
    </CityLayout>
  );
}

