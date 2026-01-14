import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import { Loader2 } from 'lucide-react';

interface Scatter3DDataPoint {
  x: number;
  y: number;
  z: number;
  label?: string;
  color?: string;
  size?: number;
}

interface Scatter3DProps {
  data: Scatter3DDataPoint[];
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  zAxisLabel?: string;
  height?: number;
  colorScale?: string;
}

export const Scatter3D: React.FC<Scatter3DProps> = ({
  data,
  title = '3D 산점도',
  xAxisLabel = 'X축',
  yAxisLabel = 'Y축',
  zAxisLabel = 'Z축',
  height = 600,
  colorScale = 'Viridis'
}) => {
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!data || data.length === 0) {
      setLoading(false);
      return;
    }

    const x = data.map(d => d.x);
    const y = data.map(d => d.y);
    const z = data.map(d => d.z);
    const colors = data.map(d => d.color || z);
    const sizes = data.map(d => d.size || 8);
    const labels = data.map(d => d.label || '');

    setChartData([
      {
        type: 'scatter3d',
        mode: 'markers',
        x: x,
        y: y,
        z: z,
        marker: {
          size: sizes,
          color: colors,
          colorscale: colorScale,
          colorbar: {
            title: zAxisLabel,
            titlefont: { size: 14 },
            thickness: 20,
            len: 0.8
          },
          line: {
            color: 'rgba(217, 217, 217, 0.14)',
            width: 0.5
          },
          opacity: 0.8
        },
        text: labels,
        hovertemplate:
          '<b>%{text}</b><br>' +
          `${xAxisLabel}: %{x:.2f}<br>` +
          `${yAxisLabel}: %{y:.2f}<br>` +
          `${zAxisLabel}: %{z:.2f}<extra></extra>`,
        name: '데이터 포인트'
      }
    ]);

    setLoading(false);
  }, [data, xAxisLabel, yAxisLabel, zAxisLabel, colorScale]);

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
        title: xAxisLabel,
        titlefont: { size: 14 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true,
        zeroline: false
      },
      yaxis: {
        title: yAxisLabel,
        titlefont: { size: 14 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true,
        zeroline: false
      },
      zaxis: {
        title: zAxisLabel,
        titlefont: { size: 14 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true,
        zeroline: false
      },
      camera: {
        eye: { x: 1.6, y: 1.6, z: 1.2 }
      },
      aspectmode: 'cube'
    },
    showlegend: false
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
