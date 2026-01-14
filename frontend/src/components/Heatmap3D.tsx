import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import { Loader2 } from 'lucide-react';

interface MultivariateData {
  timestamp: string;
  variables: {
    [key: string]: number;
  };
}

interface Heatmap3DProps {
  data: MultivariateData[];
  title?: string;
  height?: number;
}

export const Heatmap3D: React.FC<Heatmap3DProps> = ({
  data,
  title = '3D 다변량 히트맵',
  height = 600
}) => {
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!data || data.length === 0) {
      setLoading(false);
      return;
    }

    // 변수 이름 추출
    const variableNames = Object.keys(data[0].variables);

    // 히트맵 데이터 생성
    const zValues = variableNames.map(varName =>
      data.map(d => d.variables[varName])
    );

    const xValues = data.map(d => new Date(d.timestamp).toLocaleDateString('ko-KR'));
    const yValues = variableNames;

    setChartData([
      {
        type: 'surface',
        x: xValues,
        y: yValues,
        z: zValues,
        colorscale: 'RdYlGn',
        reversescale: false,
        colorbar: {
          title: '측정값',
          titlefont: { size: 14 },
          thickness: 20,
          len: 0.8
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
        hovertemplate:
          '<b>%{y}</b><br>' +
          '날짜: %{x}<br>' +
          '값: %{z:.2f}<extra></extra>',
        name: '다변량 데이터'
      }
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
    margin: { l: 80, r: 50, b: 80, t: 50 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    scene: {
      xaxis: {
        title: '날짜',
        titlefont: { size: 14 },
        tickfont: { size: 10 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true
      },
      yaxis: {
        title: '변수',
        titlefont: { size: 14 },
        tickfont: { size: 10 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true
      },
      zaxis: {
        title: '값',
        titlefont: { size: 14 },
        gridcolor: 'rgb(200, 200, 200)',
        showgrid: true
      },
      camera: {
        eye: { x: 1.8, y: 1.8, z: 1.2 }
      },
      aspectmode: 'manual',
      aspectratio: { x: 2, y: 1, z: 1 }
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
