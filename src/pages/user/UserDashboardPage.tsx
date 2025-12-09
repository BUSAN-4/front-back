import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Car, AlertTriangle, Gauge, Eye, TrendingUp, Calendar } from 'lucide-react';
import VehicleRegistrationModal from '../../components/user/VehicleRegistrationModal';
import { useVehicle } from '../../hooks/useVehicle';
import { getMonthlySafetyScores, type MonthlySafetyScore } from '../../utils/api';
import { useNavigate } from 'react-router-dom';

export default function UserDashboardPage() {
  const { vehicles, fetchVehicles } = useVehicle();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [hasVehicle, setHasVehicle] = useState(false);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock 데이터 제거됨 - 실제 API 데이터를 사용합니다
  const [safetyScore, setSafetyScore] = useState<number | null>(null);
  const [drivingStats, setDrivingStats] = useState({
    totalDrives: 0,
    drowsyCount: 0,
    rapidAccelCount: 0,
    rapidDecelCount: 0,
    totalDistance: 0,
  });
  const [recentDrives, setRecentDrives] = useState<MonthlySafetyScore[]>([]);

  useEffect(() => {
    fetchVehicles();
  }, [fetchVehicles]);

  useEffect(() => {
    setHasVehicle(vehicles.length > 0);
  }, [vehicles]);

  // 최근 30일 데이터 가져오기 (현재 월과 이전 월)
  useEffect(() => {
    if (hasVehicle && vehicles.length > 0) {
      fetchDashboardData();
    }
  }, [hasVehicle, vehicles.length]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const now = new Date();
      const currentYear = now.getFullYear();
      const currentMonth = now.getMonth() + 1;
      const lastMonth = currentMonth === 1 ? 12 : currentMonth - 1;
      const lastMonthYear = currentMonth === 1 ? currentYear - 1 : currentYear;

      // 현재 월과 이전 월 데이터 가져오기
      const [currentMonthData, lastMonthData] = await Promise.all([
        getMonthlySafetyScores(currentYear, currentMonth).catch(() => []),
        getMonthlySafetyScores(lastMonthYear, lastMonth).catch(() => []),
      ]);

      const allScores = [...currentMonthData, ...lastMonthData];
      
      // 최근 30일 데이터만 필터링
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      
      const recentScores = allScores.filter((score) => {
        if (!score.endTime) return false;
        const scoreDate = new Date(score.endTime);
        return scoreDate >= thirtyDaysAgo;
      });

      // 평균 점수 계산
      if (recentScores.length > 0) {
        const avgScore = Math.round(
          recentScores.reduce((sum, s) => sum + s.safetyScore, 0) / recentScores.length
        );
        setSafetyScore(avgScore);
      }

      // 통계 계산
      const totalDrowsy = recentScores.reduce((sum, s) => sum + (s.drowsyPenalty > 0 ? 1 : 0), 0);
      const totalRapidAccel = recentScores.reduce((sum, s) => {
        // rapidPenalty는 급가속+급감속 합계이므로 대략적으로 나눔
        return sum + Math.ceil(s.rapidPenalty / 2);
      }, 0);
      const totalRapidDecel = totalRapidAccel; // 대략적으로 동일하게 설정

      setDrivingStats({
        totalDrives: recentScores.length,
        drowsyCount: totalDrowsy,
        rapidAccelCount: totalRapidAccel,
        rapidDecelCount: totalRapidDecel,
        totalDistance: 0, // 거리 정보는 세션 상세에서 가져와야 함
      });

      // 최근 5개 세션만 표시
      setRecentDrives(
        recentScores
          .sort((a, b) => {
            const dateA = a.endTime ? new Date(a.endTime).getTime() : 0;
            const dateB = b.endTime ? new Date(b.endTime).getTime() : 0;
            return dateB - dateA;
          })
          .slice(0, 5)
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다.');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVehicleRegistration = async (vehicleData: { plateNumber: string }) => {
    try {
      const { registerVehicleByPlate } = await import('../../utils/api');
      const response = await registerVehicleByPlate(vehicleData.plateNumber);
      console.log('차량 등록 성공:', response);
      // 차량 등록 성공 후 차량 목록 새로고침
      await fetchVehicles();
      setHasVehicle(true);
      setIsModalOpen(false);
      // 차량 등록 후 대시보드 데이터 새로고침
      await fetchDashboardData();
    } catch (error) {
      console.error('차량 등록 실패:', error);
      throw error; // 모달에서 에러 처리하도록 throw
    }
  };

  if (!hasVehicle) {
    return (
      <>
        <div className="flex items-center justify-center min-h-[500px]">
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="p-4 bg-blue-100 rounded-full">
                  <Car className="size-12 text-blue-600" />
                </div>
              </div>
              <CardTitle>차량을 등록해주세요</CardTitle>
              <CardDescription>
                안전운전 관리 서비스를 이용하시려면 먼저 차량을 등록해야 합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => setIsModalOpen(true)} className="w-full" size="lg">
                차량 등록하기
              </Button>
            </CardContent>
          </Card>
        </div>
        <VehicleRegistrationModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleVehicleRegistration}
        />
      </>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number | null) => {
    if (score === null) return '--';
    if (score >= 90) return '우수';
    if (score >= 70) return '양호';
    return '주의';
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">안전 운전 대시보드</h1>
          <p className="text-gray-600">내 운전 습관을 확인하고 안전 점수를 개선하세요</p>
        </div>
        <Button 
          onClick={() => navigate('/user/safety-score')}
          variant="outline"
          className="flex items-center gap-2"
        >
          상세 보기
          <TrendingUp className="size-4" />
        </Button>
      </div>

      {/* 로딩 상태 */}
      {loading && (
        <Card className="shadow-sm">
          <CardContent className="py-16 text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <div className="text-gray-600 font-medium">데이터를 불러오는 중...</div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 에러 상태 */}
      {error && (
        <Card className="border-2 border-red-200 bg-red-50 shadow-sm">
          <CardContent className="py-8 text-center">
            <div className="flex flex-col items-center gap-4">
              <AlertTriangle className="size-8 text-red-500" />
              <div className="text-red-700 font-medium">{error}</div>
              <Button 
                onClick={fetchDashboardData} 
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                다시 시도
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 안전 점수 카드 */}
      {!loading && !error && (
        <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 via-blue-50/50 to-white shadow-lg">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-xl">
              <TrendingUp className="size-6 text-blue-600" />
              내 안전습관 점수
            </CardTitle>
            <CardDescription className="text-base">최근 30일 기준 평균 점수</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-8">
              <div className="relative">
                <div className={`text-7xl font-bold ${getScoreColor(safetyScore ?? 0)}`}>
                  {safetyScore ?? '--'}
                </div>
                {safetyScore !== null && (
                  <Badge className="absolute -top-2 -right-2" variant="secondary">
                    {getScoreLabel(safetyScore)}
                  </Badge>
                )}
              </div>
              <div className="flex-1 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-600">점수 진행률</span>
                  <span className="text-lg font-bold text-gray-900">{safetyScore ?? 0}/100</span>
                </div>
                <Progress value={safetyScore ?? 0} className="h-4" />
                <p className="text-sm text-gray-600">
                  {safetyScore !== null 
                    ? `100점 만점 중 ${safetyScore}점으로 안전운전을 실천하고 있습니다.`
                    : '주행 데이터가 없습니다. 안전운전 점수 페이지에서 데이터를 확인하세요.'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 통계 카드 그리드 */}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Calendar className="size-4 text-gray-500" />
              총 주행 횟수
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{drivingStats.totalDrives}회</div>
            <p className="text-xs text-gray-500 mt-1">최근 30일</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Eye className="size-4 text-yellow-500" />
              졸음운전 감지
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{drivingStats.drowsyCount}회</div>
            <p className="text-xs text-gray-500 mt-1">주의가 필요합니다</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Gauge className="size-4 text-red-500" />
              급가속
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{drivingStats.rapidAccelCount}회</div>
            <p className="text-xs text-gray-500 mt-1">안전 운전을 유지하세요</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <AlertTriangle className="size-4 text-orange-500" />
              급감속
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{drivingStats.rapidDecelCount}회</div>
            <p className="text-xs text-gray-500 mt-1">주행 거리 {drivingStats.totalDistance}km</p>
          </CardContent>
        </Card>
        </div>
      )}

      {/* 주행별 상세 조회 */}
      {!loading && !error && (
        <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>주행별 상세 조회</CardTitle>
          <CardDescription>최근 주행 기록 및 안전 점수</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300 bg-gray-50">
                  <th className="text-left py-4 px-4 text-gray-700 font-semibold">날짜</th>
                  <th className="text-center py-4 px-4 text-gray-700 font-semibold">안전점수</th>
                  <th className="text-center py-4 px-4 text-gray-700 font-semibold">거리(km)</th>
                  <th className="text-center py-4 px-4 text-gray-700 font-semibold">졸음운전 감점</th>
                  <th className="text-center py-4 px-4 text-gray-700 font-semibold">급가속/급감속 감점</th>
                  <th className="text-center py-4 px-4 text-gray-700 font-semibold">총 감점</th>
                </tr>
              </thead>
              <tbody>
                {recentDrives.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <Calendar className="size-12 text-gray-300" />
                        <div className="text-gray-500 font-medium">주행 기록이 없습니다.</div>
                        <p className="text-sm text-gray-400">안전운전 점수 페이지에서 더 많은 정보를 확인하세요.</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  recentDrives.map((drive) => {
                    const driveDate = drive.endTime 
                      ? new Date(drive.endTime).toLocaleDateString('ko-KR', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })
                      : '날짜 없음';
                    
                    return (
                      <tr 
                        key={drive.sessionId} 
                        className="border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer"
                        onClick={() => navigate(`/user/safety-detail/${drive.sessionId}`)}
                      >
                        <td className="py-4 px-4 text-gray-900 font-medium">{driveDate}</td>
                        <td className="py-4 px-4 text-center">
                          <Badge 
                            variant={drive.safetyScore >= 85 ? 'default' : 'secondary'}
                            className={drive.safetyScore >= 90 ? 'bg-green-500' : drive.safetyScore >= 70 ? 'bg-yellow-500' : 'bg-red-500'}
                          >
                            {drive.safetyScore}점
                          </Badge>
                        </td>
                        <td className="py-4 px-4 text-center text-gray-700">--</td>
                        <td className="py-4 px-4 text-center">
                          {drive.drowsyPenalty > 0 ? (
                            <span className="text-yellow-600 font-medium">{drive.drowsyPenalty}점 감점</span>
                          ) : (
                            <span className="text-green-600">없음</span>
                          )}
                        </td>
                        <td className="py-4 px-4 text-center">
                          {drive.rapidPenalty > 0 ? (
                            <span className="text-red-600 font-medium">{drive.rapidPenalty}점 감점</span>
                          ) : (
                            <span className="text-green-600">없음</span>
                          )}
                        </td>
                        <td className="py-4 px-4 text-center">
                          <Badge variant="outline" className="text-xs">
                            총 {drive.totalPenalty}점 감점
                          </Badge>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
        </Card>
      )}
    </div>
  );
}
