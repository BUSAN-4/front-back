import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Trophy, Calendar, Car, MapPin, User, TrendingUp, ChevronLeft, ChevronRight } from 'lucide-react';
import { getBestDriversMonthly } from '../../../utils/api';
import type { BestDriverMonthly } from '../../../utils/api';

export default function CityBestDriversPage() {
  const [drivers, setDrivers] = useState<BestDriverMonthly[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);

  useEffect(() => {
    console.log('CityBestDriversPage mounted, fetching data...');
    fetchBestDrivers();
  }, [selectedYear, selectedMonth]);

  const fetchBestDrivers = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log(`Fetching best drivers for ${selectedYear}-${selectedMonth}`);
      const data = await getBestDriversMonthly(selectedYear, selectedMonth);
      console.log('Best drivers data:', data);
      setDrivers(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      console.error('Error fetching best drivers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePrevMonth = () => {
    if (selectedMonth === 1) {
      setSelectedMonth(12);
      setSelectedYear(selectedYear - 1);
    } else {
      setSelectedMonth(selectedMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (selectedMonth === 12) {
      setSelectedMonth(1);
      setSelectedYear(selectedYear + 1);
    } else {
      setSelectedMonth(selectedMonth + 1);
    }
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return 'bg-yellow-500 text-white';
    if (rank === 2) return 'bg-gray-400 text-white';
    if (rank === 3) return 'bg-orange-500 text-white';
    return 'bg-blue-100 text-blue-700';
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return null;
  };

  const months = [
    '1월', '2월', '3월', '4월', '5월', '6월',
    '7월', '8월', '9월', '10월', '11월', '12월'
  ];

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  // 디버깅: 컴포넌트가 렌더링되는지 확인
  console.log('CityBestDriversPage rendering', { selectedYear, selectedMonth, drivers, loading, error });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">베스트 드라이버</h1>
        <p className="text-gray-600">월별 안전 운전 우수 차량 Top 10</p>
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 font-medium">오류: {error}</p>
            <p className="text-sm text-red-500 mt-2">API 엔드포인트: /api/trips/best-drivers/monthly</p>
          </div>
        )}
      </div>

      {/* 월 선택 컨트롤 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="size-5 text-blue-600" />
            기간 선택
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">연도:</label>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}년
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">월:</label>
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {months.map((month, index) => (
                  <option key={index + 1} value={index + 1}>
                    {month}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrevMonth}
                className="flex items-center gap-1"
              >
                <ChevronLeft className="size-4" />
                이전 달
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleNextMonth}
                className="flex items-center gap-1"
                disabled={selectedYear === new Date().getFullYear() && selectedMonth === new Date().getMonth() + 1}
              >
                다음 달
                <ChevronRight className="size-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 로딩 및 에러 상태 */}
      {loading && (
        <Card>
          <CardContent className="py-12 text-center">
            <div className="text-gray-500">데이터를 불러오는 중...</div>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-12 text-center">
            <div className="text-red-600">{error}</div>
            <Button onClick={fetchBestDrivers} className="mt-4" variant="outline">
              다시 시도
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 베스트 드라이버 목록 */}
      {!loading && !error && (
        <>
          {drivers.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-gray-500">
                  {selectedYear}년 {selectedMonth}월 데이터가 없습니다.
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {/* Top 3 하이라이트 */}
              {drivers.slice(0, 3).length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {drivers.slice(0, 3).map((driver) => (
                    <Card
                      key={driver.carId}
                      className={`border-2 ${
                        driver.rank === 1
                          ? 'border-yellow-400 bg-gradient-to-br from-yellow-50 to-white'
                          : driver.rank === 2
                          ? 'border-gray-300 bg-gradient-to-br from-gray-50 to-white'
                          : 'border-orange-300 bg-gradient-to-br from-orange-50 to-white'
                      }`}
                    >
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-2xl">{getRankIcon(driver.rank)}</span>
                            <CardTitle className="text-lg">#{driver.rank}위</CardTitle>
                          </div>
                          <Badge className={getRankBadgeColor(driver.rank)}>
                            {driver.rank}위
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-sm">
                            <Car className="size-4 text-gray-500" />
                            <span className="font-medium">
                              {driver.carBrand || 'N/A'} {driver.carModel || ''}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <User className="size-4 text-gray-500" />
                            <span>
                              {driver.driverAge ? `${driver.driverAge}세` : 'N/A'}{' '}
                              {driver.driverSex || ''}
                            </span>
                          </div>
                          {driver.driverLocation && (
                            <div className="flex items-center gap-2 text-sm">
                              <MapPin className="size-4 text-gray-500" />
                              <span className="text-gray-600">{driver.driverLocation}</span>
                            </div>
                          )}
                          <div className="pt-2 border-t border-gray-200">
                            <div className="flex items-center gap-2 mb-2">
                              <Trophy className="size-4 text-blue-600" />
                              <span className="text-lg font-bold text-blue-600">
                                {driver.driverScore.toFixed(1)}점
                              </span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                              <div>세션: {driver.sessionCount}회</div>
                              <div>총점: {driver.totalScore}</div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* 전체 랭킹 테이블 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="size-5 text-blue-600" />
                    전체 랭킹
                  </CardTitle>
                  <CardDescription>
                    {selectedYear}년 {selectedMonth}월 베스트 드라이버 Top 10
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200 bg-gray-50">
                          <th className="text-left py-3 px-4 text-gray-700 font-medium">순위</th>
                          <th className="text-left py-3 px-4 text-gray-700 font-medium">차량 정보</th>
                          <th className="text-left py-3 px-4 text-gray-700 font-medium">운전자 정보</th>
                          <th className="text-center py-3 px-4 text-gray-700 font-medium">점수</th>
                          <th className="text-center py-3 px-4 text-gray-700 font-medium">급가속</th>
                          <th className="text-center py-3 px-4 text-gray-700 font-medium">급감속</th>
                          <th className="text-center py-3 px-4 text-gray-700 font-medium">눈감음</th>
                          <th className="text-center py-3 px-4 text-gray-700 font-medium">세션 수</th>
                        </tr>
                      </thead>
                      <tbody>
                        {drivers.map((driver) => (
                          <tr
                            key={driver.carId}
                            className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                          >
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                {getRankIcon(driver.rank) && (
                                  <span className="text-xl">{getRankIcon(driver.rank)}</span>
                                )}
                                <Badge className={getRankBadgeColor(driver.rank)}>
                                  {driver.rank}
                                </Badge>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                <Car className="size-4 text-gray-400" />
                                <div>
                                  <div className="font-medium text-gray-900">
                                    {driver.carBrand || 'N/A'} {driver.carModel || ''}
                                  </div>
                                  <div className="text-xs text-gray-500">{driver.carId}</div>
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <User className="size-3 text-gray-400" />
                                  <span className="text-sm">
                                    {driver.driverAge ? `${driver.driverAge}세` : 'N/A'}{' '}
                                    {driver.driverSex || ''}
                                  </span>
                                </div>
                                {driver.driverLocation && (
                                  <div className="flex items-center gap-2">
                                    <MapPin className="size-3 text-gray-400" />
                                    <span className="text-xs text-gray-600">
                                      {driver.driverLocation}
                                    </span>
                                  </div>
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <div className="flex flex-col items-center">
                                <span className="text-lg font-bold text-blue-600">
                                  {driver.driverScore.toFixed(1)}
                                </span>
                                <span className="text-xs text-gray-500">점</span>
                              </div>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span
                                className={`font-medium ${
                                  driver.totalRapidAcc > 0 ? 'text-red-600' : 'text-green-600'
                                }`}
                              >
                                {driver.totalRapidAcc}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span
                                className={`font-medium ${
                                  driver.totalRapidDeacc > 0 ? 'text-orange-600' : 'text-green-600'
                                }`}
                              >
                                {driver.totalRapidDeacc}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span
                                className={`font-medium ${
                                  driver.totalGazeClosure > 0 ? 'text-yellow-600' : 'text-green-600'
                                }`}
                              >
                                {driver.totalGazeClosure}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <Badge variant="secondary">{driver.sessionCount}회</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  );
}




