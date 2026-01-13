/**
 * Login Page
 * 사용자 로그인 페이지
 */

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Lock, Mail, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, loading, error, clearError } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    clearError();

    if (!formData.username || !formData.password) {
      toast.error('아이디와 비밀번호를 입력해주세요.');
      return;
    }

    const result = await login(formData.username, formData.password);

    if (result.success) {
      toast.success('로그인되었습니다.');
      navigate('/');
    } else {
      toast.error(result.error || '로그인에 실패했습니다.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* 로고 및 타이틀 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Smart SPC</h1>
          <p className="text-gray-600">품질관리 시스템에 로그인하세요</p>
        </div>

        {/* 로그인 폼 */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-center">로그인</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 아이디 입력 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  아이디
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="아이디를 입력하세요"
                    className="pl-10"
                    disabled={loading}
                    autoComplete="username"
                    required
                  />
                </div>
              </div>

              {/* 비밀번호 입력 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  비밀번호
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="비밀번호를 입력하세요"
                    className="pl-10"
                    disabled={loading}
                    autoComplete="current-password"
                    required
                  />
                </div>
              </div>

              {/* 에러 메시지 */}
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                  <span className="text-sm text-red-700">{error}</span>
                </div>
              )}

              {/* 제출 버튼 */}
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    로그인 중...
                  </>
                ) : (
                  '로그인'
                )}
              </Button>

              {/* 추가 옵션 */}
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="ml-2 text-gray-600">로그인 상태 유지</span>
                </label>
                <Link
                  to="/forgot-password"
                  className="text-purple-600 hover:text-purple-700 font-medium"
                >
                  비밀번호 찾기
                </Link>
              </div>
            </form>

            {/* 회원가입 링크 */}
            <div className="mt-6 text-center text-sm">
              <span className="text-gray-600">계정이 없으신가요?</span>{' '}
              <Link
                to="/register"
                className="text-purple-600 hover:text-purple-700 font-medium"
              >
                회원가입
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* 저작권 정보 */}
        <div className="mt-8 text-center text-sm text-gray-500">
          © 2026 Smart SPC System. All rights reserved.
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
