import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import { Spinner } from 'lucide-react';

interface ForecastDataPoint {
  timestamp: string;
  value: number;
  is_forecast?: boolean;
  upper_bound?: number;
  lower_bound?: number;
}

interface ForecastChartProps {
  data: ForecastDataPoint[];
  title?: string;
  height?: number;
  showConfidenceInterval?: boolean;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({
  data,
  title = '시계열 예측',
  height = 500,
  showConfidenceInterval = true
}) => {
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!data || data.length === 0) {
      setLoading(false);
      return;
    }

    const timestamps = data.map(d => new Date(d.timestamp));
    const values = data.map(d => d.value);
    const isForecast = data.map(d => d.is_forecast || false);

    // 실제 데이터
    const actualData = {
      x: timestamps.filter((_, i) => !isForecast[i]),
      y: values.filter((_, i) => !isForecast[i]),
      type: 'scatter',
      mode: 'lines+markers',
      name: '실제 데이터',
      line: { color: '#3b82f6', width: 2 },
      marker: { size: 6 }
    };

    // 예측 데이터
    const forecastData = {
      x: timestamps.filter((_, i) => isForecast[i]),
      y: values.filter((_, i) => isForecast[i]),
      type: 'scatter',
      mode: 'lines+markers',
      name: '예측 데이터',
      line: { color: '#10b981', width: 2, dash: 'dash' },
      marker: { size: 6, symbol: 'diamond' }
    };

    const traces = [actualData, forecastData];

    // 신뢰 구간
    if (showConfidenceInterval && data.some(d => d.upper_bound !== undefined)) {
      const upperBound = data.map(d => d.upper_bound);
      const lowerBound = data.map(d => d.lower_bound);

      traces.push({
        x: timestamps,
        y: upperBound,
        type: 'scatter',
        mode: 'lines',
        line: { width: 0 },
        showlegend: false,
        hoverinfo: 'skip'
      });

      traces.push({
        x: timestamps,
        y: lowerBound,
        type: 'scatter',
        mode: 'lines',
        fill: 'tonexty',
        fillcolor: 'rgba(16, 185, 129, 0.2)',
        line: { width: 0 },
        name: '신뢰 구간',
        hoverinfo: 'skip'
      });
    }

    setChartData(traces);
    setLoading(false);
  }, [data, showConfidenceInterval]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner className="animate-spin h-8 w-8 text-blue-600" />
        <span className="ml-2">차트 로딩 중...</span>
      </div>
    );
  }

  const layout = {
    title: {
      text: title,
      font: { size: 20, color: '#2c3e50' }
    },
    autosize: true,
    height: height,
    margin: { l: 60, r: 40, b: 60, t: 50 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: {
      title: '날짜',
      titlefont: { size: 14 },
      tickfont: { size: 12 },
      gridcolor: 'rgb(200, 200, 200)',
      showgrid: true,
      zeroline: true,
      zerolinecolor: '#666'
    },
    yaxis: {
      title: '측정값',
      titlefont: { size: 14 },
      tickfont: { size: 12 },
      gridcolor: 'rgb(200, 200, 200)',
      showgrid: true,
      zeroline: true,
      zerolinecolor: '#666'
    },
    hovermode: 'x unified',
    showlegend: true,
    legend: {
      x: 0.02,
      y: 0.98,
      bgcolor: 'rgba(255, 255, 255, 0.8)',
      bordercolor: '#DDD',
      borderwidth: 1
    },
    shapes: (() => {
      // 실제/예측 구분선
      if (data.some(d => d.is_forecast)) {
        const firstForecastIdx = data.findIndex(d => d.is_forecast);
        if (firstForecastIdx > 0) {
          return [{
            type: 'line',
            x0: new Date(data[firstForecastIdx].timestamp),
            y0: 0,
            x1: new Date(data[firstForecastIdx].timestamp),
            y1: 1,
            yref: 'paper',
            line: {
              color: '#666',
              width: 2,
              dash: 'dot'
            }
          }];
        }
      }
      return [];
    })()
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    toImageButtonOptions: {
      format: 'png',
      filename: 'forecast_chart',
      height: height,
      width: 1200,
      scale: 1
    }
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-lg p-6">
      <Plot
        data={chartData}
        layout={layout}
        config={config}
        useResizeHandler={true}
        style={{ width: '100%', height: `${height}px` }}
      />
    </div>
  );
};
