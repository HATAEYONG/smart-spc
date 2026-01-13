/**
 * p-Chart 컴포넌트
 * 불량률 관리도
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
} from 'recharts';
import type { ControlChartDataPoint } from '@/types/spc';

interface PChartProps {
  data: ControlChartDataPoint[];
  limits: {
    p?: { ucl: number; cl: number; lcl: number };
  };
  height?: number;
}

export const PChart: React.FC<PChartProps> = ({ data, limits, height = 400 }) => {
  const { p: pLimits } = limits;

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-2">p-Chart (불량률 관리도)</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="subgroup_number"
            label={{ value: '샘플 번호', position: 'insideBottom', offset: -5 }}
          />
          <YAxis
            label={{ value: '불량률 (p)', angle: -90, position: 'insideLeft' }}
            tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const point = payload[0].payload;
                return (
                  <div className="bg-white p-3 border border-gray-300 rounded shadow">
                    <p className="font-semibold">샘플 #{point.subgroup_number}</p>
                    <p className="text-sm">불량률: {(point.p * 100).toFixed(2)}%</p>
                    {pLimits && (
                      <>
                        <p className="text-xs text-gray-500">
                          UCL: {(pLimits.ucl * 100).toFixed(2)}%
                        </p>
                        <p className="text-xs text-gray-500">
                          CL: {(pLimits.cl * 100).toFixed(2)}%
                        </p>
                        <p className="text-xs text-gray-500">
                          LCL: {(pLimits.lcl * 100).toFixed(2)}%
                        </p>
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
          {pLimits && (
            <>
              <ReferenceLine
                y={pLimits.ucl}
                stroke="red"
                strokeDasharray="3 3"
                label={{
                  value: `UCL (${(pLimits.ucl * 100).toFixed(1)}%)`,
                  position: 'right',
                  fill: 'red',
                }}
              />
              <ReferenceLine
                y={pLimits.cl}
                stroke="green"
                strokeDasharray="3 3"
                label={{
                  value: `CL (${(pLimits.cl * 100).toFixed(1)}%)`,
                  position: 'right',
                  fill: 'green',
                }}
              />
              {pLimits.lcl > 0 && (
                <ReferenceLine
                  y={pLimits.lcl}
                  stroke="red"
                  strokeDasharray="3 3"
                  label={{
                    value: `LCL (${(pLimits.lcl * 100).toFixed(1)}%)`,
                    position: 'right',
                    fill: 'red',
                  }}
                />
              )}
            </>
          )}

          {/* 데이터 라인 */}
          <Line
            type="monotone"
            dataKey="p"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              if (!pLimits) return <circle cx={cx} cy={cy} r={4} fill="#f59e0b" />;

              // 관리 한계 벗어남 체크
              const isOutOfControl = payload.p > pLimits.ucl || payload.p < pLimits.lcl;

              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={isOutOfControl ? 6 : 4}
                  fill={isOutOfControl ? '#ef4444' : '#f59e0b'}
                  stroke={isOutOfControl ? '#dc2626' : 'none'}
                  strokeWidth={2}
                />
              );
            }}
            name="불량률 (p)"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* 해석 가이드 */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg text-sm">
        <p className="font-semibold text-blue-900 mb-2">💡 p-Chart 해석:</p>
        <ul className="text-blue-800 space-y-1">
          <li>• 불량률이 관리 한계(UCL, LCL)를 벗어나면 공정 이상</li>
          <li>• 중심선(CL) 주변에 안정적으로 분포하면 공정 안정</li>
          <li>• 연속적인 상승/하강 추세는 공정 변화 신호</li>
        </ul>
      </div>
    </div>
  );
};

export default PChart;
