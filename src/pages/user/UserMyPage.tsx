import { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  CardContent,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import { Add, Edit, Delete, DirectionsCar } from '@mui/icons-material';
import UserLayout from '../../layouts/UserLayout';
import { useVehicle } from '../../hooks/useVehicle';
import { useAuthStore } from '../../store/authStore';
import type { Vehicle } from '../../types/vehicle';
import { VEHICLE_TYPES } from '../../utils/constants';
import { validateLicensePlate } from '../../utils/validators';
import Card from '../../components/common/Card';

export default function UserMyPage() {
  const { user } = useAuthStore();
  const { vehicles, registerVehicle, updateVehicle, deleteVehicle, fetchVehicles } = useVehicle();
  const [openDialog, setOpenDialog] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [currentVehicleData, setCurrentVehicleData] = useState<Omit<Vehicle, 'id' | 'userId' | 'createdAt'>>({
    licensePlate: '',
    vehicleType: 'private',
    model: '',
    year: undefined,
  });

  useEffect(() => {
    fetchVehicles();
  }, [fetchVehicles]);

  const handleOpenDialog = (vehicle?: Vehicle) => {
    if (vehicle) {
      setEditingVehicle(vehicle);
      setCurrentVehicleData({
        licensePlate: vehicle.licensePlate,
        vehicleType: vehicle.vehicleType,
        model: vehicle.model || '',
        year: vehicle.year,
      });
    } else {
      setEditingVehicle(null);
      setCurrentVehicleData({
        licensePlate: '',
        vehicleType: 'private',
        model: '',
        year: undefined,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingVehicle(null);
    setCurrentVehicleData({
      licensePlate: '',
      vehicleType: 'private',
      model: '',
      year: undefined,
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setCurrentVehicleData((prev) => ({
      ...prev,
      [name as string]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateLicensePlate(currentVehicleData.licensePlate)) {
      alert('올바른 차량번호 형식이 아닙니다.');
      return;
    }
    if (!currentVehicleData.vehicleType) {
      alert('차량 유형을 선택해주세요.');
      return;
    }

    try {
      if (editingVehicle) {
        await updateVehicle(editingVehicle.id, currentVehicleData);
      } else {
        await registerVehicle(currentVehicleData);
      }
      handleCloseDialog();
      fetchVehicles();
    } catch (error) {
      console.error('차량 등록/수정 실패:', error);
      alert('차량 등록/수정 실패');
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('정말 삭제하시겠습니까?')) {
      try {
        await deleteVehicle(id);
        fetchVehicles();
      } catch (error) {
        console.error('차량 삭제 실패:', error);
        alert('차량 삭제 실패');
      }
    }
  };

  return (
    <UserLayout>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        마이페이지
      </Typography>
      <Box
        sx={{
          display: 'grid',
          gap: 3,
          gridTemplateColumns: {
            xs: '1fr',
            md: 'repeat(2, 1fr)',
          },
        }}
      >
        <Box>
          <Card title="계정 정보">
            <CardContent>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <Typography component="span" sx={{ fontWeight: 'bold' }}>아이디:</Typography> {user?.username}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <Typography component="span" sx={{ fontWeight: 'bold' }}>이메일:</Typography> {user?.email}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <Typography component="span" sx={{ fontWeight: 'bold' }}>이름:</Typography> {user?.name || '-'}
              </Typography>
              <Typography variant="body1">
                <Typography component="span" sx={{ fontWeight: 'bold' }}>전화번호:</Typography> {user?.phone || '-'}
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box>
          <Card title="등록된 차량">
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>등록된 차량</Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => handleOpenDialog()}
                  sx={{ textTransform: 'none' }}
                >
                  차량 추가
                </Button>
              </Box>
              {vehicles.length === 0 ? (
                <Alert severity="info" sx={{ mt: 2 }}>
                  등록된 차량이 없습니다. 차량을 등록해주세요.
                </Alert>
              ) : (
                <Box sx={{ mt: 2 }}>
                  {vehicles.map((vehicle) => (
                    <Box key={vehicle.id} sx={{
                      mb: 2, p: 2, border: 1, borderColor: 'divider', borderRadius: 1,
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      bgcolor: 'background.paper',
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <DirectionsCar sx={{ color: 'primary.main', fontSize: 30 }} />
                        <Box>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{vehicle.licensePlate}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {VEHICLE_TYPES[vehicle.vehicleType.toUpperCase() as keyof typeof VEHICLE_TYPES]} | {vehicle.model || '-'} | {vehicle.year || '-'}년식
                          </Typography>
                        </Box>
                      </Box>
                      <Box>
                        <IconButton size="small" onClick={() => handleOpenDialog(vehicle)}>
                          <Edit fontSize="small" />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDelete(vehicle.id)}>
                          <Delete fontSize="small" color="error" />
                        </IconButton>
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', fontWeight: 'bold' }}>
          {editingVehicle ? '차량 수정' : '차량 등록'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent dividers>
            <TextField
              fullWidth
              label="차량번호"
              name="licensePlate"
              value={currentVehicleData.licensePlate}
              onChange={handleInputChange}
              margin="normal"
              required
              error={!validateLicensePlate(currentVehicleData.licensePlate) && currentVehicleData.licensePlate !== ''}
              helperText={!validateLicensePlate(currentVehicleData.licensePlate) && currentVehicleData.licensePlate !== '' ? '올바른 차량번호 형식이 아닙니다' : ''}
            />
            <FormControl fullWidth margin="normal" required>
              <InputLabel>차량 유형</InputLabel>
              <Select
                label="차량 유형"
                name="vehicleType"
                value={currentVehicleData.vehicleType}
                onChange={handleInputChange}
              >
                {Object.entries(VEHICLE_TYPES).map(([key, value]) => (
                  <MenuItem key={key} value={value}>
                    {value === 'taxi' ? '택시' : value === 'private' ? '승용차' : '렌터카'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="모델명"
              name="model"
              value={currentVehicleData.model}
              onChange={handleInputChange}
              margin="normal"
            />
            <TextField
              fullWidth
              type="number"
              label="연식"
              name="year"
              value={currentVehicleData.year || ''}
              onChange={handleInputChange}
              margin="normal"
            />
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={handleCloseDialog} variant="outlined" sx={{ textTransform: 'none' }}>
              취소
            </Button>
            <Button type="submit" variant="contained" sx={{ textTransform: 'none' }}>
              {editingVehicle ? '수정' : '등록'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </UserLayout>
  );
}

