/**
 * Register Page
 * 사용자 회원가입 페이지
 */

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { User, Mail, Lock, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, loading, error, clearError } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // 아이디 검증
    if (!formData.username || formData.username.length < 4) {
      errors.username = '아이디는 4자 이상이어야 합니다.';
    }

    // 이메일 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
      errors.email = '올바른 이메일 주소를 입력해주세요.';
    }

    // 비밀번호 검증
    if (!formData.password || formData.password.length < 8) {
      errors.password = '비밀번호는 8자 이상이어야 합니다.';
    }

    // 비밀번호 확인
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = '비밀번호가 일치하지 않습니다.';
    }

    // 이름 검증
    if (!formData.first_name || formData.first_name.trim().length < 1) {
      errors.first_name = '이름을 입력해주세요.';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationErrors({});

    if (!validateForm()) {
      toast.error('입력 정보를 확인해주세요.');
      return;
    }

    const result = await register({
      username: formData.username,
      email: formData.email,
      password: formData.password,
      first_name: formData.first_name,
      last_name: formData.last_name,
    });

    if (result.success) {
      toast.success('회원가입이 완료되었습니다.');
      navigate('/');
    } else {
      toast.error(result.error || '회원가입에 실패했습니다.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // 해당 필드의 에러 메시지 초기화
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const passwordsMatch = formData.password && formData.confirmPassword && formData.password === formData.confirmPassword;
  const passwordLongEnough = formData.password && formData.password.length >= 8;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">회원가입</h1>
          <p className="text-gray-600">Smart SPC 시스템에 가입하세요</p>
        </div>

        {/* 회원가입 폼 */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-center">계정 생성</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 이름 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    이름 *
                  </label>
                  <Input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    placeholder="이름"
                    disabled={loading}
                    autoComplete="given-name"
                    required
                  />
                  {validationErrors.first_name && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.first_name}</p>
                  )}
                </div>

                {/* 성 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    성
                  </label>
                  <Input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    placeholder="성 (선택)"
                    disabled={loading}
                    autoComplete="family-name"
                  />
                </div>
              </div>

              {/* 아이디 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  아이디 *
                </label>
                <Input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="4자 이상의 아이디"
                  disabled={loading}
                  autoComplete="username"
                  required
                />
                {validationErrors.username && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.username}</p>
                )}
              </div>

              {/* 이메일 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  이메일 *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="example@email.com"
                    className="pl-10"
                    disabled={loading}
                    autoComplete="email"
                    required
                  />
                </div>
                {validationErrors.email && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.email}</p>
                )}
              </div>

              {/* 비밀번호 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  비밀번호 *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="8자 이상의 비밀번호"
                    className="pl-10"
                    disabled={loading}
                    autoComplete="new-password"
                    required
                  />
                </div>
                {validationErrors.password && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.password}</p>
                )}

                {/* 비밀번호 강도 표시 */}
                {formData.password && (
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center gap-2 text-sm">
                      {passwordLongEnough ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                      )}
                      <span className={passwordLongEnough ? 'text-green-600' : 'text-gray-500'}>
                        8자 이상
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* 비밀번호 확인 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  비밀번호 확인 *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="비밀번호를 다시 입력하세요"
                    className="pl-10"
                    disabled={loading}
                    autoComplete="new-password"
                    required
                  />
                </div>
                {validationErrors.confirmPassword && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.confirmPassword}</p>
                )}
                {formData.confirmPassword && (
                  <div className="mt-2 flex items-center gap-2 text-sm">
                    {passwordsMatch ? (
                    <>
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span className="text-green-600">비밀번호가 일치합니다</span>
                    </>
                  ) : (
                    <span className="text-red-600">비밀번호가 일치하지 않습니다</span>
                  )}
                </div>
              )}
              </div>

              {/* 에러 메시지 */}
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                  <span className="text-sm text-red-700">{error}</span>
                </div>
              )}

              {/* 약관 동의 */}
              <div className="space-y-2">
                <label className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    className="mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                    required
                  />
                  <span className="text-sm text-gray-600">
                    <a href="/terms" className="text-purple-600 hover:text-purple-700">이용약관</a>에 동의합니다
                  </span>
                </label>
                <label className="flex items-start gap-2">
                  <input
                    type="checkbox"
                    className="mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                    required
                  />
                  <span className="text-sm text-gray-600">
                    <a href="/privacy" className="text-purple-600 hover:text-purple-700">개인정보 처리방침</a>에 동의합니다
                  </span>
                </label>
              </div>

              {/* 제출 버튼 */}
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    가입 중...
                  </>
                ) : (
                  '회원가입'
                )}
              </Button>
            </form>

            {/* 로그인 링크 */}
            <div className="mt-6 text-center text-sm">
              <span className="text-gray-600">이미 계정이 있으신가요?</span>{' '}
              <Link
                to="/login"
                className="text-purple-600 hover:text-purple-700 font-medium"
              >
                로그인
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

export default RegisterPage;
