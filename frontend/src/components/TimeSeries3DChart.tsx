import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import { Loader2 } from 'lucide-react';

interface TimeSeriesData {
  timestamp: string;
  value: number;
  upper_limit?: number;
  lower_limit?: number;
  target?: number;
}

interface TimeSeries3DChartProps {
  data: TimeSeriesData[];
  title?: string;
  height?: number;
}

export const TimeSeries3DChart: React.FC<TimeSeries3DChartProps> = ({
  data,
  title = '3D 시계열 분석',
  height = 600
}) => {
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!data || data.length === 0) {
      setLoading(false);
      return;
    }

    // 3D Surface Plot을 위한 데이터 변환
    const x = data.map((d, i) => i);
    const y = data.map((d, i) => new Date(d.timestamp).getTime());
    const z = data.map(d => d.value);

    // 시간에 따른 3D 표면 생성
    const size = Math.ceil(Math.sqrt(data.length));
    const zSurface = [];

    for (let i = 0; i < size; i++) {
      const row = [];
      for (let j = 0; j < size; j++) {
        const idx = i * size + j;
        row.push(idx < data.length ? data[idx].value : null);
      }
      zSurface.push(row);
    }

    const xSurface = Array.from({ length: size }, (_, i) => i);
    const ySurface = Array.from({ length: size }, (_, i) => i);

    setChartData([
      {
        type: 'surface',
        x: xSurface,
        y: ySurface,
        z: zSurface,
        colorscale: 'Viridis',
        colorbar: {
          title: '측정값',
          titlefont: { size: 14 }
        },
        contours: {
          z: {
            show: true,
            usecolormap: true,
            highlightcolor: "#42f462",
            project: { z: true }
          }
        },
        opacity: 0.9,
        name: '시계열 표면'
      },
      {
        type: 'scatter3d',
        mode: 'lines+markers',
        x: x,
        y: y.map((_, i) => i),
        z: z,
        marker: {
          size: 4,
          color: z,
          colorscale: 'RdYlBu',
          colorbar: {
            title: '값',
            titlefont: { size: 14 }
          }
        },
        line: {
          color: 'darkblue',
          width: 2
        },
        name: '측정 데이터'
      },
      // 상한선
      ...(data[0]?.upper_limit !== undefined ? [{
        type: 'scatter3d',
        mode: 'lines',
        x: x,
        y: y.map((_, i) => i),
        z: data.map(() => data[0].upper_limit!),
        line: { color: 'red', width: 3, dash: 'dash' },
        name: '상한선 (UCL)'
      }] : []),
      // 하한선
      ...(data[0]?.lower_limit !== undefined ? [{
        type: 'scatter3d',
        mode: 'lines',
        x: x,
        y: y.map((_, i) => i),
        z: data.map(() => data[0].lower_limit!),
        line: { color: 'orange', width: 3, dash: 'dash' },
        name: '하한선 (LCL)'
      }] : []),
      // 목표값
      ...(data[0]?.target !== undefined ? [{
        type: 'scatter3d',
        mode: 'lines',
        x: x,
        y: y.map((_, i) => i),
        z: data.map(() => data[0].target!),
        line: { color: 'green', width: 4 },
        name: '목표값'
      }] : [])
    ]);

    setLoading(false);
  }, [data]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin h-8 w-8 text-blue-600" />
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
    margin: { l: 0, r: 0, b: 0, t: 50 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    scene: {
      xaxis: {
        title: '시간 인덱스',
        titlefont: { size: 14 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true
      },
      yaxis: {
        title: '데이터 포인트',
        titlefont: { size: 14 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true
      },
      zaxis: {
        title: '측정값',
        titlefont: { size: 14 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true
      },
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.5 }
      },
      aspectmode: 'cube'
    },
    showlegend: true,
    legend: {
      x: 0.02,
      y: 0.98,
      bgcolor: 'rgba(255, 255, 255, 0.8)',
      bordercolor: '#DDD',
      borderwidth: 1
    }
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d']
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
