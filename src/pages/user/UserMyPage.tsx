import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { useAuth } from '../../contexts/AuthContext';
import { User, Car, Edit, Plus, Trash2 } from 'lucide-react';
import VehicleRegistrationModal from '../../components/user/VehicleRegistrationModal';
import { useVehicle } from '../../hooks/useVehicle';
import { useEffect } from 'react';

export default function UserMyPage() {
  const { user } = useAuth();
  const { vehicles, fetchVehicles, registerVehicle, deleteVehicle } = useVehicle();
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [isVehicleModalOpen, setIsVehicleModalOpen] = useState(false);

  useEffect(() => {
    fetchVehicles();
  }, [fetchVehicles]);

  const handleVehicleAdd = async (data: any) => {
    try {
      await registerVehicle({
        licensePlate: data.plateNumber,
        vehicleType: 'private',
        model: `${data.manufacturer} ${data.model}`,
        year: parseInt(data.year) || undefined,
      });
      setIsVehicleModalOpen(false);
      fetchVehicles();
    } catch (error) {
      console.error('차량 등록 실패:', error);
      alert('차량 등록에 실패했습니다.');
    }
  };

  const handleVehicleDelete = async (id: string) => {
    if (window.confirm('차량 정보를 삭제하시겠습니까?')) {
      try {
        await deleteVehicle(id);
        fetchVehicles();
      } catch (error) {
        console.error('차량 삭제 실패:', error);
        alert('차량 삭제에 실패했습니다.');
      }
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">마이페이지</h1>
        <p className="text-gray-600">개인정보 및 차량 정보를 관리하세요</p>
      </div>

      {/* 개인정보 카드 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <User className="size-5" />
                개인정보
              </CardTitle>
              <CardDescription>회원 정보를 확인하고 수정할 수 있습니다</CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditingProfile(!isEditingProfile)}
            >
              <Edit className="size-4 mr-2" />
              {isEditingProfile ? '취소' : '수정'}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {!isEditingProfile ? (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-600">이름</Label>
                  <p className="text-gray-900 mt-1 font-medium">{user?.name || '-'}</p>
                </div>
                <div>
                  <Label className="text-gray-600">이메일</Label>
                  <p className="text-gray-900 mt-1 font-medium">{user?.email || '-'}</p>
                </div>
              </div>
              <div>
                <Label className="text-gray-600">사용자 유형</Label>
                <div className="mt-1">
                  <Badge>일반 사용자</Badge>
                </div>
              </div>
            </>
          ) : (
            <form className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">이름</Label>
                  <Input id="name" defaultValue={user?.name} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">이메일</Label>
                  <Input id="email" type="email" defaultValue={user?.email} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="currentPassword">현재 비밀번호</Label>
                <Input id="currentPassword" type="password" placeholder="현재 비밀번호" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="newPassword">새 비밀번호</Label>
                  <Input id="newPassword" type="password" placeholder="새 비밀번호" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">비밀번호 확인</Label>
                  <Input id="confirmPassword" type="password" placeholder="비밀번호 확인" />
                </div>
              </div>
              <Button type="button" onClick={() => setIsEditingProfile(false)}>
                저장하기
              </Button>
            </form>
          )}
        </CardContent>
      </Card>

      {/* 차량 정보 카드 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Car className="size-5" />
                등록된 차량
              </CardTitle>
              <CardDescription>차량 정보를 등록하고 관리하세요</CardDescription>
            </div>
            <Button size="sm" onClick={() => setIsVehicleModalOpen(true)}>
              <Plus className="size-4 mr-2" />
              차량 추가
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {vehicles.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              등록된 차량이 없습니다. 차량을 추가해주세요.
            </div>
          ) : (
            <div className="space-y-4">
              {vehicles.map((vehicle) => (
                <div
                  key={vehicle.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <Car className="size-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-gray-900 font-medium">
                        {vehicle.licensePlate}
                      </p>
                      <p className="text-sm text-gray-500">
                        {vehicle.model || '-'} · {vehicle.year || '-'}년식
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Edit className="size-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleVehicleDelete(vehicle.id)}
                    >
                      <Trash2 className="size-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <VehicleRegistrationModal
        isOpen={isVehicleModalOpen}
        onClose={() => setIsVehicleModalOpen(false)}
        onSubmit={handleVehicleAdd}
      />
    </div>
  );
}
