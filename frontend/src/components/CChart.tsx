/**
 * c-Chart 컴포넌트
 * 결점수 관리도
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

interface CChartProps {
  data: ControlChartDataPoint[];
  limits: {
    p?: { ucl: number; cl: number; lcl: number };
  };
  height?: number;
}

export const CChart: React.FC<CChartProps> = ({ data, limits, height = 400 }) => {
  const { p: cLimits } = limits;

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-2">c-Chart (결점수 관리도)</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="subgroup_number"
            label={{ value: '샘플 번호', position: 'insideBottom', offset: -5 }}
          />
          <YAxis label={{ value: '결점수 (c)', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const point = payload[0].payload;
                return (
                  <div className="bg-white p-3 border border-gray-300 rounded shadow">
                    <p className="font-semibold">샘플 #{point.subgroup_number}</p>
                    <p className="text-sm">결점수: {point.c}</p>
                    {cLimits && (
                      <>
                        <p className="text-xs text-gray-500">UCL: {cLimits.ucl.toFixed(2)}</p>
                        <p className="text-xs text-gray-500">CL: {cLimits.cl.toFixed(2)}</p>
                        <p className="text-xs text-gray-500">LCL: {cLimits.lcl.toFixed(2)}</p>
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
          {cLimits && (
            <>
              <ReferenceLine
                y={cLimits.ucl}
                stroke="red"
                strokeDasharray="3 3"
                label={{
                  value: `UCL (${cLimits.ucl.toFixed(1)})`,
                  position: 'right',
                  fill: 'red',
                }}
              />
              <ReferenceLine
                y={cLimits.cl}
                stroke="green"
                strokeDasharray="3 3"
                label={{
                  value: `CL (${cLimits.cl.toFixed(1)})`,
                  position: 'right',
                  fill: 'green',
                }}
              />
              {cLimits.lcl > 0 && (
                <ReferenceLine
                  y={cLimits.lcl}
                  stroke="red"
                  strokeDasharray="3 3"
                  label={{
                    value: `LCL (${cLimits.lcl.toFixed(1)})`,
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
            dataKey="c"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              if (!cLimits) return <circle cx={cx} cy={cy} r={4} fill="#8b5cf6" />;

              // 관리 한계 벗어남 체크
              const isOutOfControl = payload.c > cLimits.ucl || payload.c < cLimits.lcl;

              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={isOutOfControl ? 6 : 4}
                  fill={isOutOfControl ? '#ef4444' : '#8b5cf6'}
                  stroke={isOutOfControl ? '#dc2626' : 'none'}
                  strokeWidth={2}
                />
              );
            }}
            name="결점수 (c)"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* 해석 가이드 */}
      <div className="mt-4 p-4 bg-purple-50 rounded-lg text-sm">
        <p className="font-semibold text-purple-900 mb-2">💡 c-Chart 해석:</p>
        <ul className="text-purple-800 space-y-1">
          <li>• 결점수가 관리 한계를 벗어나면 공정 이상</li>
          <li>• 포아송 분포를 따르는 결점수 데이터에 적용</li>
          <li>• 단위 크기가 일정해야 함 (변동 시 u-Chart 사용)</li>
        </ul>
      </div>
    </div>
  );
};

export default CChart;
