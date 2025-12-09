import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { MapPin, Award, Loader2 } from 'lucide-react';
import PowerBIEmbedView from '../../../components/common/powerbi/PowerBIEmbedView';
import {
  getBestDriversMonthlyForCity,
  type BestDriverMonthly
} from '../../../utils/api';

const POWER_BI_REPORT_URL = import.meta.env.VITE_POWER_BI_SAFE_DRIVING_URL || "";
const POWER_BI_BEST_DRIVER_URL = import.meta.env.VITE_POWER_BI_BEST_DRIVER_URL || "";

export default function CityDashboardSafeDriving() {
  const [bestDriversMonthly, setBestDriversMonthly] = useState<BestDriverMonthly[]>([]);
  const [isLoadingBestDrivers, setIsLoadingBestDrivers] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState<number | undefined>(undefined);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [bestDriversError, setBestDriversError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('map-visualization');

  // 베스트 드라이버 탭이 활성화될 때만 데이터 로드
  useEffect(() => {
    if (activeTab === 'best') {
      fetchBestDriversMonthly();
    }
  }, [selectedYear, selectedMonth, activeTab]);

  const fetchBestDriversMonthly = async () => {
    try {
      setIsLoadingBestDrivers(true);
      setBestDriversError(null);
      const month = selectedMonth || new Date().getMonth() + 1;
      const data = await getBestDriversMonthlyForCity(selectedYear, month);
      setBestDriversMonthly(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('베스트 드라이버 데이터 로딩 실패:', error);
      setBestDriversMonthly([]);
      setBestDriversError(
        error instanceof Error 
          ? error.message 
          : '베스트 드라이버 데이터를 불러오는데 실패했습니다.'
      );
    } finally {
      setIsLoadingBestDrivers(false);
    }
  };

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-5xl font-bold text-gray-950 mb-4 tracking-tight">안전운전 관리</h1>
        <p className="text-xl text-gray-700 leading-relaxed font-medium">부산시 전체 안전운전 현황 및 통계 (실시간)</p>
      </div>

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="map-visualization">
            <MapPin className="size-4 mr-2" />
            월별 구별 운전습관 지도 시각화
          </TabsTrigger>
          <TabsTrigger value="best-driver-powerbi">
            <Award className="size-4 mr-2" />
            베스트 드라이버 PowerBI
          </TabsTrigger>
          <TabsTrigger value="best">
            <Award className="size-4 mr-2" />
            베스트 드라이버
          </TabsTrigger>
        </TabsList>

        {/* 월별 구별 운전습관 지도 시각화 탭 */}
        <TabsContent value="map-visualization" className="space-y-6">
          {/* PowerBI 대시보드 영역 */}
          <Card>
            <CardHeader>
              <CardTitle>월별 구별 운전습관 지도 시각화</CardTitle>
              <CardDescription>PowerBI 대시보드 - Best/Worst Place 분석</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              {POWER_BI_REPORT_URL ? (
                <div className="w-full">
                  <PowerBIEmbedView reportUrl={POWER_BI_REPORT_URL} height="1000px" />
                </div>
              ) : (
                <div className="bg-gray-100 rounded-lg p-8 text-center m-6">
                  <div className="text-gray-500 mb-2">PowerBI 대시보드 연동 영역</div>
                  <p className="text-sm text-gray-400">PowerBI URL을 설정해주세요</p>
                  <div className="mt-4 h-64 bg-white rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
                    <MapPin className="size-12 text-gray-300" />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 베스트 드라이버 PowerBI 탭 */}
        <TabsContent value="best-driver-powerbi" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>베스트 드라이버 분석</CardTitle>
              <CardDescription>PowerBI 대시보드 - 베스트 드라이버 통계 분석</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              {POWER_BI_BEST_DRIVER_URL ? (
                <div className="w-full">
                  <PowerBIEmbedView reportUrl={POWER_BI_BEST_DRIVER_URL} height="1000px" />
                </div>
              ) : (
                <div className="bg-gray-100 rounded-lg p-8 text-center m-6">
                  <div className="text-gray-500 mb-2">PowerBI 대시보드 연동 영역</div>
                  <p className="text-sm text-gray-400">PowerBI URL을 설정해주세요</p>
                  <div className="mt-4 h-64 bg-white rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
                    <Award className="size-12 text-gray-300" />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 베스트 드라이버 탭 */}
        <TabsContent value="best" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="size-5 text-yellow-500" />
                    베스트 드라이버 TOP 10
                  </CardTitle>
                  <CardDescription>
                    {selectedYear}년 {selectedMonth || new Date().getMonth() + 1}월 월별 안전 운전 우수 차량
                  </CardDescription>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 font-medium">연도:</label>
                    <select
                      value={selectedYear}
                      onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((year) => (
                        <option key={year} value={year}>{year}년</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 font-medium">월:</label>
                    <select
                      value={selectedMonth || ''}
                      onChange={(e) => setSelectedMonth(e.target.value ? parseInt(e.target.value) : undefined)}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      <option value="">현재 월</option>
                      {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
                        <option key={month} value={month}>{month}월</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {isLoadingBestDrivers ? (
                <div className="py-8 text-center">
                  <Loader2 className="size-6 animate-spin text-blue-500 mx-auto mb-2" />
                  <div className="text-sm text-gray-500">데이터를 불러오는 중...</div>
                </div>
              ) : bestDriversError ? (
                <div className="py-8 text-center">
                  <div className="text-red-600 mb-2 font-medium">데이터 로딩 실패</div>
                  <div className="text-sm text-gray-500">{bestDriversError}</div>
                </div>
              ) : bestDriversMonthly && bestDriversMonthly.length > 0 ? (
                <div className="space-y-4">
                  {/* Top 3 하이라이트 */}
                  {bestDriversMonthly.slice(0, 3).length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      {bestDriversMonthly.slice(0, 3).map((driver) => (
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
                          <CardHeader className="pb-3">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">
                                  {driver.rank === 1 ? '🥇' : driver.rank === 2 ? '🥈' : '🥉'}
                                </span>
                                <CardTitle className="text-lg">#{driver.rank}위</CardTitle>
                              </div>
                              <Badge
                                className={
                                  driver.rank === 1
                                    ? 'bg-yellow-500 text-white'
                                    : driver.rank === 2
                                    ? 'bg-gray-400 text-white'
                                    : 'bg-orange-500 text-white'
                                }
                              >
                                {driver.rank}위
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2">
                              <div className="text-sm font-medium text-gray-900">
                                {driver.carId || 'N/A'}
                              </div>
                              <div className="text-xs text-gray-600">
                                {driver.driverAge ? `${driver.driverAge}세` : 'N/A'} {driver.driverSex || ''}
                              </div>
                              {driver.driverLocation && (
                                <div className="text-xs text-gray-500">{driver.driverLocation}</div>
                              )}
                              <div className="pt-2 border-t border-gray-200">
                                <div className="text-lg font-bold text-blue-600 mb-1">
                                  {Number(driver.driverScore ?? 0).toFixed(1)}점
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                                  <div>세션: {driver.sessionCount ?? 0}회</div>
                                  <div>총점: {driver.totalScore ?? 0}</div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}

                  {/* 전체 랭킹 테이블 */}
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
                        {bestDriversMonthly.map((driver) => (
                          <tr
                            key={driver.carId}
                            className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                          >
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                {driver.rank <= 3 && (
                                  <span className="text-xl">
                                    {driver.rank === 1 ? '🥇' : driver.rank === 2 ? '🥈' : '🥉'}
                                  </span>
                                )}
                                <Badge
                                  className={
                                    driver.rank === 1
                                      ? 'bg-yellow-500 text-white'
                                      : driver.rank === 2
                                      ? 'bg-gray-400 text-white'
                                      : driver.rank === 3
                                      ? 'bg-orange-500 text-white'
                                      : 'bg-blue-100 text-blue-700'
                                  }
                                >
                                  {driver.rank}
                                </Badge>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="font-medium text-gray-900">
                                {driver.carId || 'N/A'}
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="text-sm">
                                {driver.driverAge ? `${driver.driverAge}세` : 'N/A'} {driver.driverSex || ''}
                              </div>
                              {driver.driverLocation && (
                                <div className="text-xs text-gray-500">{driver.driverLocation}</div>
                              )}
                            </td>
                            <td className="py-3 px-4 text-center">
                              <div className="text-lg font-bold text-blue-600">
                                {Number(driver.driverScore ?? 0).toFixed(1)}
                              </div>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span
                                className={`font-medium ${
                                  (driver.totalRapidAcc ?? 0) > 0 ? 'text-red-600' : 'text-green-600'
                                }`}
                              >
                                {driver.totalRapidAcc ?? 0}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span
                                className={`font-medium ${
                                  (driver.totalRapidDeacc ?? 0) > 0 ? 'text-orange-600' : 'text-green-600'
                                }`}
                              >
                                {driver.totalRapidDeacc ?? 0}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span
                                className={`font-medium ${
                                  (driver.totalGazeClosure ?? 0) > 0 ? 'text-yellow-600' : 'text-green-600'
                                }`}
                              >
                                {driver.totalGazeClosure ?? 0}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <Badge variant="secondary">{driver.sessionCount ?? 0}회</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="py-8 text-center text-gray-500">
                  {selectedYear}년 {selectedMonth || new Date().getMonth() + 1}월 데이터가 없습니다.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

