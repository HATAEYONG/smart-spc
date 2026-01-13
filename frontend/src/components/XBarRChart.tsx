/**
 * X-bar & R Chart 컴포넌트
 * 평균-범위 관리도 시각화
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
  ComposedChart,
  Area,
} from 'recharts';
import type { ControlChartDataPoint } from '@/types/spc';

interface XBarRChartProps {
  data: ControlChartDataPoint[];
  limits: {
    xbar?: { ucl: number; cl: number; lcl: number };
    r?: { ucl: number; cl: number; lcl: number };
  };
  showR?: boolean;
  height?: number;
}

export const XBarRChart: React.FC<XBarRChartProps> = ({
  data,
  limits,
  showR = true,
  height = 300,
}) => {
  const { xbar: xbarLimits, r: rLimits } = limits;

  // X-bar Chart
  const XBarChart = () => (
    <div className="mb-6">
      <h3 className="text-lg font-semibold mb-2">X-bar Chart (평균 관리도)</h3>
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="subgroup_number"
            label={{ value: '부분군 번호', position: 'insideBottom', offset: -5 }}
          />
          <YAxis label={{ value: '평균', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const point = payload[0].payload;
                return (
                  <div className="bg-white p-3 border border-gray-300 rounded shadow">
                    <p className="font-semibold">부분군 #{point.subgroup_number}</p>
                    <p className="text-sm">평균: {point.xbar?.toFixed(3)}</p>
                    {xbarLimits && (
                      <>
                        <p className="text-xs text-gray-500">UCL: {xbarLimits.ucl.toFixed(3)}</p>
                        <p className="text-xs text-gray-500">CL: {xbarLimits.cl.toFixed(3)}</p>
                        <p className="text-xs text-gray-500">LCL: {xbarLimits.lcl.toFixed(3)}</p>
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
          {xbarLimits && (
            <>
              <ReferenceLine
                y={xbarLimits.ucl}
                stroke="red"
                strokeDasharray="3 3"
                label={{ value: 'UCL', position: 'right', fill: 'red' }}
              />
              <ReferenceLine
                y={xbarLimits.cl}
                stroke="green"
                strokeDasharray="3 3"
                label={{ value: 'CL', position: 'right', fill: 'green' }}
              />
              <ReferenceLine
                y={xbarLimits.lcl}
                stroke="red"
                strokeDasharray="3 3"
                label={{ value: 'LCL', position: 'right', fill: 'red' }}
              />

              {/* ±1σ 구간 (회색 영역) */}
              <Area
                dataKey={() => xbarLimits.cl + (xbarLimits.ucl - xbarLimits.cl) / 3}
                fill="rgba(255, 255, 0, 0.1)"
                stroke="none"
              />
              <Area
                dataKey={() => xbarLimits.cl - (xbarLimits.cl - xbarLimits.lcl) / 3}
                fill="rgba(255, 255, 0, 0.1)"
                stroke="none"
              />
            </>
          )}

          {/* 데이터 라인 */}
          <Line
            type="monotone"
            dataKey="xbar"
            stroke="#2563eb"
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              if (!xbarLimits) return <circle cx={cx} cy={cy} r={4} fill="#2563eb" />;

              // 관리 한계 벗어남 체크
              const isOutOfControl =
                payload.xbar > xbarLimits.ucl || payload.xbar < xbarLimits.lcl;

              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={isOutOfControl ? 6 : 4}
                  fill={isOutOfControl ? '#ef4444' : '#2563eb'}
                  stroke={isOutOfControl ? '#dc2626' : 'none'}
                  strokeWidth={2}
                />
              );
            }}
            name="X-bar"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );

  // R Chart
  const RChart = () => (
    <div>
      <h3 className="text-lg font-semibold mb-2">R Chart (범위 관리도)</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="subgroup_number"
            label={{ value: '부분군 번호', position: 'insideBottom', offset: -5 }}
          />
          <YAxis label={{ value: '범위', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const point = payload[0].payload;
                return (
                  <div className="bg-white p-3 border border-gray-300 rounded shadow">
                    <p className="font-semibold">부분군 #{point.subgroup_number}</p>
                    <p className="text-sm">범위: {point.r?.toFixed(3)}</p>
                    {rLimits && (
                      <>
                        <p className="text-xs text-gray-500">UCL: {rLimits.ucl.toFixed(3)}</p>
                        <p className="text-xs text-gray-500">CL: {rLimits.cl.toFixed(3)}</p>
                        <p className="text-xs text-gray-500">LCL: {rLimits.lcl.toFixed(3)}</p>
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
          {rLimits && (
            <>
              <ReferenceLine
                y={rLimits.ucl}
                stroke="red"
                strokeDasharray="3 3"
                label={{ value: 'UCL', position: 'right', fill: 'red' }}
              />
              <ReferenceLine
                y={rLimits.cl}
                stroke="green"
                strokeDasharray="3 3"
                label={{ value: 'CL', position: 'right', fill: 'green' }}
              />
              {rLimits.lcl > 0 && (
                <ReferenceLine
                  y={rLimits.lcl}
                  stroke="red"
                  strokeDasharray="3 3"
                  label={{ value: 'LCL', position: 'right', fill: 'red' }}
                />
              )}
            </>
          )}

          {/* 데이터 라인 */}
          <Line
            type="monotone"
            dataKey="r"
            stroke="#dc2626"
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              if (!rLimits) return <circle cx={cx} cy={cy} r={4} fill="#dc2626" />;

              // 관리 한계 벗어남 체크
              const isOutOfControl = payload.r > rLimits.ucl || payload.r < rLimits.lcl;

              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={isOutOfControl ? 6 : 4}
                  fill={isOutOfControl ? '#ef4444' : '#dc2626'}
                  stroke={isOutOfControl ? '#dc2626' : 'none'}
                  strokeWidth={2}
                />
              );
            }}
            name="Range"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <div className="w-full">
      <XBarChart />
      {showR && <RChart />}
    </div>
  );
};

export default XBarRChart;
