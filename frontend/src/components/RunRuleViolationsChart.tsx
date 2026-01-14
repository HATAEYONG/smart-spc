/**
 * Run Rule 위반 시각화 컴포넌트
 * Western Electric Rules 위반 표시
 */
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  ZAxis,
  Cell,
} from 'recharts';
import type { QualityMeasurement, RunRuleViolation } from '@/types/spc';

interface RunRuleViolationsChartProps {
  measurements: QualityMeasurement[];
  violations: RunRuleViolation[];
  limits: {
    ucl: number;
    cl: number;
    lcl: number;
  };
  height?: number;
}

// Run Rule 타입별 색상 매핑
const RULE_COLORS: Record<string, string> = {
  RULE_1: '#ef4444', // 빨강: 관리 한계 벗어남
  RULE_2: '#f97316', // 주황: 9개 연속 중심선 한쪽
  RULE_3: '#f59e0b', // 노랑: 6개 연속 증가/감소
  RULE_4: '#84cc16', // 연두: 14개 연속 교대
  RULE_5: '#06b6d4', // 청록: 2/3개 2시그마 벗어남
  RULE_6: '#3b82f6', // 파랑: 4/5개 1시그마 벗어남
  RULE_7: '#8b5cf6', // 보라: 15개 연속 1시그마 이내
  RULE_8: '#ec4899', // 분홍: 8개 연속 1시그마 벗어남
};

// Run Rule 설명
const RULE_DESCRIPTIONS: Record<string, string> = {
  RULE_1: '관리 한계선 벗어남',
  RULE_2: '9개 연속 점이 중심선 한쪽에 위치',
  RULE_3: '6개 연속 점이 증가 또는 감소 추세',
  RULE_4: '14개 연속 점이 교대로 증가/감소',
  RULE_5: '3개 중 2개가 2σ 이상 벗어남',
  RULE_6: '5개 중 4개가 1σ 이상 벗어남',
  RULE_7: '15개 연속 점이 1σ 이내',
  RULE_8: '8개 연속 점이 1σ 벗어남',
};

export const RunRuleViolationsChart: React.FC<RunRuleViolationsChartProps> = ({
  measurements,
  violations,
  limits,
  height = 500,
}) => {
  // 부분군별 평균 계산
  const subgroupData = React.useMemo(() => {
    const subgroups = new Map<number, number[]>();
    measurements.forEach((m) => {
      if (!subgroups.has(m.subgroup_number)) {
        subgroups.set(m.subgroup_number, []);
      }
      subgroups.get(m.subgroup_number)!.push(m.measurement_value);
    });

    return Array.from(subgroups.entries()).map(([subgroup_number, values]) => ({
      subgroup_number,
      xbar: values.reduce((a, b) => a + b, 0) / values.length,
    }));
  }, [measurements]);

  // 위반 점 매핑
  const violationsBySubgroup = React.useMemo(() => {
    const map = new Map<number, RunRuleViolation[]>();
    violations.forEach((v) => {
      const subgroup = v.point_index || v.subgroup_number;
      if (!map.has(subgroup)) {
        map.set(subgroup, []);
      }
      map.get(subgroup)!.push(v);
    });
    return map;
  }, [violations]);

  // 1σ, 2σ 라인 계산
  const sigma = (limits.ucl - limits.cl) / 3;
  const oneSigmaUpper = limits.cl + sigma;
  const oneSigmaLower = limits.cl - sigma;
  const twoSigmaUpper = limits.cl + 2 * sigma;
  const twoSigmaLower = limits.cl - 2 * sigma;

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-2">Run Rule 위반 분석</h3>

      {/* 차트 */}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={subgroupData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="subgroup_number"
            label={{ value: '부분군 번호', position: 'insideBottom', offset: -5 }}
          />
          <YAxis label={{ value: '평균 (X-bar)', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const point = payload[0].payload;
                const subgroupViolations = violationsBySubgroup.get(point.subgroup_number) || [];

                return (
                  <div className="bg-white p-3 border border-gray-300 rounded shadow max-w-md">
                    <p className="font-semibold">부분군 #{point.subgroup_number}</p>
                    <p className="text-sm">평균: {point.xbar.toFixed(4)}</p>
                    {subgroupViolations.length > 0 && (
                      <>
                        <hr className="my-2" />
                        <p className="font-semibold text-red-600 text-sm">위반 사항:</p>
                        {subgroupViolations.map((v, idx) => (
                          <div key={idx} className="text-xs mt-1">
                            <span
                              className="inline-block w-3 h-3 rounded-full mr-1"
                              style={{ backgroundColor: RULE_COLORS[v.rule_type] }}
                            />
                            {RULE_DESCRIPTIONS[v.rule_type]}
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />

          {/* 관리 한계선 */}
          <ReferenceLine
            y={limits.ucl}
            stroke="#ef4444"
            strokeWidth={2}
            label={{ value: 'UCL', position: 'right', fill: '#ef4444' }}
          />
          <ReferenceLine
            y={limits.cl}
            stroke="#10b981"
            strokeWidth={2}
            label={{ value: 'CL', position: 'right', fill: '#10b981' }}
          />
          <ReferenceLine
            y={limits.lcl}
            stroke="#ef4444"
            strokeWidth={2}
            label={{ value: 'LCL', position: 'right', fill: '#ef4444' }}
          />

          {/* 1σ, 2σ 라인 */}
          <ReferenceLine
            y={twoSigmaUpper}
            stroke="#f97316"
            strokeDasharray="5 5"
            strokeOpacity={0.5}
            label={{ value: '+2σ', position: 'right', fill: '#f97316', fontSize: 10 }}
          />
          <ReferenceLine
            y={oneSigmaUpper}
            stroke="#f59e0b"
            strokeDasharray="5 5"
            strokeOpacity={0.5}
            label={{ value: '+1σ', position: 'right', fill: '#f59e0b', fontSize: 10 }}
          />
          <ReferenceLine
            y={oneSigmaLower}
            stroke="#f59e0b"
            strokeDasharray="5 5"
            strokeOpacity={0.5}
            label={{ value: '-1σ', position: 'right', fill: '#f59e0b', fontSize: 10 }}
          />
          <ReferenceLine
            y={twoSigmaLower}
            stroke="#f97316"
            strokeDasharray="5 5"
            strokeOpacity={0.5}
            label={{ value: '-2σ', position: 'right', fill: '#f97316', fontSize: 10 }}
          />

          {/* 데이터 라인 */}
          <Line
            type="monotone"
            dataKey="xbar"
            stroke="#2563eb"
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              const subgroupViolations = violationsBySubgroup.get(payload.subgroup_number) || [];

              // 위반이 있으면 강조
              if (subgroupViolations.length > 0) {
                const primaryViolation = subgroupViolations[0];
                return (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={8}
                    fill={RULE_COLORS[primaryViolation.rule_type]}
                    stroke="#ffffff"
                    strokeWidth={2}
                  />
                );
              }

              return <circle cx={cx} cy={cy} r={4} fill="#2563eb" />;
            }}
            name="평균 (X-bar)"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* 위반 요약 */}
      <div className="mt-4">
        <h4 className="font-semibold text-gray-700 mb-2">위반 요약 ({violations.length}건)</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {Object.entries(RULE_DESCRIPTIONS).map(([ruleType, description]) => {
            const count = violations.filter((v) => v.rule_type === ruleType).length;
            if (count === 0) return null;

            return (
              <div
                key={ruleType}
                className="p-2 border rounded-lg flex items-center space-x-2"
                style={{ borderColor: RULE_COLORS[ruleType] }}
              >
                <div
                  className="w-4 h-4 rounded-full flex-shrink-0"
                  style={{ backgroundColor: RULE_COLORS[ruleType] }}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-600 truncate">{description}</p>
                  <p className="text-sm font-semibold">{count}건</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 위반 상세 목록 */}
      {violations.length > 0 && (
        <div className="mt-4">
          <h4 className="font-semibold text-gray-700 mb-2">상세 위반 목록</h4>
          <div className="max-h-64 overflow-y-auto border rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    부분군
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Rule
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    설명
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    심각도
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {violations.map((violation, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-2 whitespace-nowrap text-sm">
                      #{violation.subgroup_number}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm">
                      <span
                        className="inline-block w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: RULE_COLORS[violation.rule_type] }}
                      />
                      {violation.rule_type.replace('_', ' ')}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {RULE_DESCRIPTIONS[violation.rule_type]}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          violation.severity === 4
                            ? 'bg-red-100 text-red-800'
                            : violation.severity === 3
                            ? 'bg-orange-100 text-orange-800'
                            : violation.severity === 2
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {violation.severity === 4 ? '매우 높음' : violation.severity === 3 ? '높음' : violation.severity === 2 ? '중간' : '낮음'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 해석 가이드 */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg text-sm">
        <p className="font-semibold text-blue-900 mb-2">💡 Run Rule 해석:</p>
        <ul className="text-blue-800 space-y-1 text-xs">
          <li>• Rule 1 (빨강): 관리 한계 벗어남 - 즉시 조치 필요</li>
          <li>• Rule 2 (주황): 공정 평균 이동 가능성</li>
          <li>• Rule 3 (노랑): 공정 추세 발생</li>
          <li>• Rule 4 (연두): 공정 불안정 (과도한 변동)</li>
          <li>• Rule 5-6 (청록/파랑): 공정 분산 증가 경고</li>
          <li>• Rule 7 (보라): 공정 분산 감소 (과도한 안정)</li>
          <li>• Rule 8 (분홍): 공정 혼합 또는 층화</li>
        </ul>
      </div>
    </div>
  );
};

export default RunRuleViolationsChart;
