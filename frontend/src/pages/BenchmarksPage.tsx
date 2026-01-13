import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  TrendingUp,
  Award,
  Target,
  Globe,
  Factory,
  BookOpen,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from 'lucide-react';

interface BenchmarkMetric {
  id: string;
  name: string;
  current: number;
  industry: {
    average: number;
    top25: number;
    best: number;
  };
  unit: string;
  trend: 'up' | 'down' | 'stable';
}

interface BestPractice {
  id: string;
  title: string;
  company: string;
  category: string;
  summary: string;
  benefits: string[];
  implementation: string;
  rating: number;
}

interface CaseStudy {
  id: string;
  title: string;
  industry: string;
  challenge: string;
  solution: string;
  results: string[];
  applicable: boolean;
}

export const BenchmarksPage: React.FC = () => {
  const [metrics] = useState<BenchmarkMetric[]>([
    {
      id: '1',
      name: 'COPQ 비율',
      current: 49.6,
      industry: { average: 65, top25: 50, best: 35 },
      unit: '%',
      trend: 'down',
    },
    {
      id: '2',
      name: '공정 능력 지수 (Cpk)',
      current: 1.28,
      industry: { average: 1.0, top25: 1.33, best: 1.67 },
      unit: '',
      trend: 'up',
    },
    {
      id: '3',
      name: '고객 불만족률',
      current: 1.8,
      industry: { average: 3.5, top25: 2.0, best: 0.8 },
      unit: '%',
      trend: 'down',
    },
    {
      id: '4',
      name: '재작업률',
      current: 4.2,
      industry: { average: 8.0, top25: 5.0, best: 2.0 },
      unit: '%',
      trend: 'down',
    },
  ]);

  const [bestPractices] = useState<BestPractice[]>([
    {
      id: '1',
      title: '실시간 SPC 모니터링 시스템',
      company: 'Toyota 자동차',
      category: '공정관리',
      summary: '라인별 실시간 SPC 데이터 수집 및 자동 경보 시스템',
      benefits: [
        '불량률 60% 감소',
        '즉각적인 이상 대응',
        '데이터 기반 의사결정',
      ],
      implementation: '각 공정에 센서 설치, 중앙 모니터링 시스템 구축',
      rating: 5,
    },
    {
      id: '2',
      title: '품질 내재화(Quality by Design)',
      company: 'Samsung SDS',
      category: '설계 품질',
      summary: '설계 단계에서 품질 리스크를 사전에 식별하고 최적화',
      benefits: [
        '설계 변경 비용 70% 절감',
        '시장 출시 기간 단축',
        '고객 만족도 향상',
      ],
      implementation: 'DFMEA, PFMEA 도구 활용, 시뮬레이션 기반 검증',
      rating: 5,
    },
    {
      id: '3',
      title: 'AI 기반 검사 자동화',
      company: 'Foxconn',
      category: '검사 공정',
      summary: '딥러닝을 활용한 외관 검사 자동화',
      benefits: [
        '검사 정확도 99.5% 달성',
        '인건비 50% 절감',
        '24시간 연속 검사 가능',
      ],
      implementation: '카메라 설치, AI 모델 학습, 자동 분류 시스템',
      rating: 4,
    },
  ]);

  const [caseStudies] = useState<CaseStudy[]>([
    {
      id: '1',
      title: '치수불량률 80% 감소 사례',
      industry: '자동차 부품',
      challenge: 'CNC 가공 공정에서 지속적인 치수불량 발생, 월간 ₩5천만원 손실',
      solution: '공구 교체 주기 최적화, 온도 제어 시스템 개선, 작업자 교육 강화',
      results: [
        '치수불량률 12% → 2.4% 감소',
        '월간 ₩4천만원 절감',
        'Cpk 0.9 → 1.45 개선',
      ],
      applicable: true,
    },
    {
      id: '2',
      title: '외관 불량 Zero 달성',
      industry: '전자 부품',
      challenge: '스크래치, 이물 등 외관 불량으로 인한 클레임 지속 발생',
      solution: '자동화 세척 라인 도입, 무인 검사 시스템 구축',
      results: [
        '외관 불량률 5% → 0.2% 감소',
        '클레임 건수 90% 감소',
        '검사 인건비 60% 절감',
      ],
      applicable: true,
    },
    {
      id: '3',
      title: '공급자 품질 수준 향상',
      industry: '조립 산업',
      challenge: '공급사 납품물 품질 편차 심함, 수입 검사 불합격률 15%',
      solution: '공급사 평가 시스템 도입, 기술 지원 확대, 파트너십 강화',
      results: [
        '수입 검사 불합격률 15% → 3% 감소',
        '공급사 온타임 납품률 98% 달성',
        '협업 비용 30% 절감',
      ],
      applicable: false,
    },
  ]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <ArrowUpRight className="w-4 h-4 text-green-600" />;
      case 'down':
        return <ArrowDownRight className="w-4 h-4 text-red-600" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Globe className="w-8 h-8 text-purple-600" />
            벤치마킹 & 사례
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            업계 벤치마크 및 우수 사례 참고
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <BookOpen className="w-4 h-4 mr-2" />
            가이드라인
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Factory className="w-4 h-4 mr-2" />
            사례 등록
          </Button>
        </div>
      </div>

      {/* 업계 벤치마크 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-600" />
            업계 벤치마크 비교
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((metric) => (
              <div key={metric.id} className="p-4 bg-white rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">{metric.name}</h3>
                  {getTrendIcon(metric.trend)}
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">현재</span>
                    <span className="font-bold text-lg text-purple-600">
                      {metric.current}{metric.unit}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">업계 평균</span>
                    <span className="text-gray-700">
                      {metric.industry.average}{metric.unit}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">상위 25%</span>
                    <span className="text-blue-600 font-medium">
                      {metric.industry.top25}{metric.unit}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">최고 수준</span>
                    <span className="text-green-600 font-medium">
                      {metric.industry.best}{metric.unit}
                    </span>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t">
                  <div className="flex items-center gap-1 text-xs">
                    {metric.current <= metric.industry.top25 ? (
                      <Star className="w-4 h-4 text-yellow-500" />
                    ) : metric.current <= metric.industry.average ? (
                      <Target className="w-4 h-4 text-blue-500" />
                    ) : (
                      <TrendingUp className="w-4 h-4 text-orange-500" />
                    )}
                    <span className="text-gray-600">
                      {metric.current <= metric.industry.top25
                        ? '상위 25% 달성'
                        : metric.current <= metric.industry.average
                        ? '업계 평균 이상'
                        : '개선 필요'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 베스트 프랙티스 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5 text-purple-600" />
              베스트 프랙티스
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {bestPractices.map((practice) => (
                <div
                  key={practice.id}
                  className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="text-xs">
                          {practice.category}
                        </Badge>
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3 h-3 ${
                                i < practice.rating
                                  ? 'text-yellow-500 fill-yellow-500'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                      <h3 className="font-semibold text-gray-900">{practice.title}</h3>
                      <p className="text-xs text-gray-500 mt-1">{practice.company}</p>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">{practice.summary}</p>

                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-1">기대 효과</div>
                    <ul className="space-y-1">
                      {practice.benefits.map((benefit, idx) => (
                        <li key={idx} className="text-xs text-gray-700 flex items-start gap-1">
                          <Target className="w-3 h-3 text-green-600 mt-0.5 flex-shrink-0" />
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Button variant="outline" size="sm" className="w-full">
                    상세보기
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 성공 사례 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Factory className="w-5 h-5 text-purple-600" />
              성공 사례
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {caseStudies.map((study) => (
                <div
                  key={study.id}
                  className={`p-4 rounded-lg border transition-all ${
                    study.applicable
                      ? 'bg-green-50 border-green-200 hover:shadow-md'
                      : 'bg-white border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <Badge variant="outline" className="text-xs mb-2">
                        {study.industry}
                      </Badge>
                      <h3 className="font-semibold text-gray-900">{study.title}</h3>
                    </div>
                    {study.applicable && (
                      <Badge className="bg-green-100 text-green-700 text-xs">
                        적용 가능
                      </Badge>
                    )}
                  </div>

                  <div className="space-y-2 text-sm">
                    <div>
                      <div className="text-xs text-gray-500 mb-1">과제</div>
                      <div className="text-gray-700">{study.challenge}</div>
                    </div>

                    <div>
                      <div className="text-xs text-gray-500 mb-1">해결 방안</div>
                      <div className="text-gray-700">{study.solution}</div>
                    </div>

                    <div className="p-2 bg-white rounded border border-gray-200">
                      <div className="text-xs text-gray-500 mb-1">성과</div>
                      <ul className="space-y-1">
                        {study.results.map((result, idx) => (
                          <li key={idx} className="text-xs text-gray-700 flex items-start gap-1">
                            <Award className="w-3 h-3 text-purple-600 mt-0.5 flex-shrink-0" />
                            <span>{result}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
