import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card } from '../../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Car, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState('user');
  const [organization, setOrganization] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const hasRedirected = useRef(false);

  // 이미 로그인된 경우 대시보드로 리다이렉트
  useEffect(() => {
    if (user) {
      const redirectPath = getRedirectPath(user.role, user.organization);
      navigate(redirectPath, { replace: true });
    }
  }, [user, navigate]);

  // 회원가입 후 전달된 메시지 및 이메일 처리
  useEffect(() => {
    if (location.state) {
      const state = location.state as { message?: string; email?: string };
      if (state.message) {
        setSuccessMessage(state.message);
      }
      if (state.email) {
        setEmail(state.email);
      }
      // state를 사용했으므로 제거하여 뒤로가기 시 다시 표시되지 않도록
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location, navigate]);

  const getRedirectPath = (role: string, organization?: string): string => {
    if (role === 'ADMIN') {
      // organization에 따라 다른 관리자 페이지로 이동
      switch (organization) {
        case 'busan':
          return '/admin/city/safe-driving';
        case 'nts':
          return '/admin/nts';
        case 'police':
          return '/admin/police';
        case 'system':
          return '/admin/system';
        default:
          return '/admin/system'; // 기본값
      }
    } else {
      return '/user/dashboard';
    }
  };

  // 이미 로그인된 사용자는 자동으로 리다이렉트 (한 번만)
  useEffect(() => {
    if (user && location.pathname === '/login' && !hasRedirected.current) {
      hasRedirected.current = true;
      const redirectPath = getRedirectPath(user.role, user.organization);
      navigate(redirectPath, { replace: true });
    }
  }, [user, location.pathname, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 로그인하고 사용자 정보 받기
      const userData = await login(email, password, userType, organization || undefined);
      
      // 로그인 성공 시 로딩 상태 해제
      setLoading(false);
      
      // 로그인 성공 시 직접 리다이렉트 (DB에 저장된 organization 사용)
      hasRedirected.current = true;
      const redirectPath = getRedirectPath(userData.role, userData.organization);
      navigate(redirectPath, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : '로그인에 실패했습니다.');
      console.error('로그인 에러:', err);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* 왼쪽 브랜드 영역 */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItaDJ2LTJoLTJ6bTAgNGgtMnYyaDJ2LTJ6bTQtNHYyaDJ2LTJoLTJ6bTAtNGgydi0yaC0ydjJ6bS0yLTJ2LTJoLTJ2Mmgyem0tMiAyaC0ydjJoMnYtMnptMiAydjJoMnYtMmgtMnptMC00aDJ2LTJoLTJ2MnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>
        
        <div className="relative z-10 flex flex-col justify-center px-20 text-white">
          <div className="mb-12">
            <div className="inline-flex items-center gap-4 bg-white/10 backdrop-blur-md px-8 py-4 rounded-2xl border border-white/20 shadow-apple-lg">
              <Car className="size-10" />
              <span className="text-3xl font-bold tracking-tight">SMART BUSAN</span>
            </div>
          </div>
          
          <h1 className="text-6xl mb-8 leading-tight font-bold tracking-tight">
            부산시<br />
            스마트 차량<br />
            통합 관리 시스템
          </h1>
          
          <p className="text-2xl text-blue-100 mb-16 leading-relaxed font-light">
            안전한 도시를 만드는 지능형 교통 관제 플랫폼
          </p>
          
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div className="size-3 bg-blue-300 rounded-full shadow-lg"></div>
              <span className="text-xl text-blue-50 font-medium">실시간 안전운전 모니터링</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="size-3 bg-blue-300 rounded-full shadow-lg"></div>
              <span className="text-xl text-blue-50 font-medium">AI 기반 불법행위 탐지</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="size-3 bg-blue-300 rounded-full shadow-lg"></div>
              <span className="text-xl text-blue-50 font-medium">빅데이터 분석 및 인사이트</span>
            </div>
          </div>
        </div>
      </div>

      {/* 오른쪽 로그인 폼 */}
      <div className="flex-1 flex items-center justify-center p-12 bg-gray-100">
        <Card className="w-full max-w-2xl p-16 shadow-apple-xl border-0 bg-white">
          <div className="mb-12">
            <div className="flex items-center gap-3 mb-6 lg:hidden">
              <Car className="size-10 text-blue-600" />
              <span className="text-3xl text-blue-600 font-bold tracking-tight">SMART BUSAN</span>
            </div>
            <h2 className="text-5xl font-bold text-gray-950 mb-4 tracking-tight">로그인</h2>
            <p className="text-xl text-gray-700 leading-relaxed font-medium">시스템에 접속하려면 로그인하세요</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {successMessage && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm">
                {successMessage}
              </div>
            )}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-3">
              <Label htmlFor="email" className="text-base font-semibold text-gray-900">이메일</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="이메일을 입력하세요"
                required
                className="h-14 text-base rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            <div className="space-y-3">
              <Label htmlFor="password" className="text-base font-semibold text-gray-900">비밀번호</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="비밀번호를 입력하세요"
                required
                className="h-14 text-base rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            <div className="space-y-3">
              <Label htmlFor="userType" className="text-base font-semibold text-gray-900">사용자 유형</Label>
              <Select value={userType} onValueChange={setUserType}>
                <SelectTrigger id="userType" className="h-14 text-base rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20">
                  <SelectValue placeholder="사용자 유형 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="user">일반 사용자</SelectItem>
                  <SelectItem value="admin">관리자</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {userType === 'admin' && (
              <div className="space-y-3">
                <Label htmlFor="organization" className="text-base font-semibold text-gray-900">소속 기관</Label>
                <Select value={organization} onValueChange={setOrganization}>
                  <SelectTrigger id="organization" className="h-14 text-base rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20">
                    <SelectValue placeholder="기관 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="busan">부산시</SelectItem>
                    <SelectItem value="nts">국세청</SelectItem>
                    <SelectItem value="police">경찰청</SelectItem>
                    <SelectItem value="system">시스템 관리자</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            <Button type="submit" className="w-full h-14 text-lg font-semibold bg-blue-600 hover:bg-blue-700 shadow-apple-lg" disabled={loading}>
              {loading ? '로그인 중...' : '로그인'}
              <ArrowRight className="size-5 ml-2" />
            </Button>

            <div className="text-center text-sm text-gray-600">
              계정이 없으신가요?{' '}
              <Link to="/register" className="text-blue-600 hover:text-blue-700 font-semibold">
                회원가입
              </Link>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
