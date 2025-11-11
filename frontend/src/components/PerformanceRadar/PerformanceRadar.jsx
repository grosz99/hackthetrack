import { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import './PerformanceRadar.css';

export default function PerformanceRadar({ driver }) {
  if (!driver) return null;

  // Extract 4 factors
  const factors = [
    { name: 'Cornering', value: driver.racecraft || 0 },
    { name: 'Racecraft', value: driver.racecraft || 0 },
    { name: 'Tire Mgmt', value: driver.tire_management || 0 },
    { name: 'Raw Speed', value: driver.speed || 0 },
  ];

  // Calculate top 3 average (mock for now - would come from API)
  const top3Average = factors.map(f => ({ ...f, value: Math.max(0, f.value - 10) }));

  const data = [
    {
      type: 'scatterpolar',
      r: factors.map(f => f.value),
      theta: factors.map(f => f.name),
      fill: 'toself',
      name: 'You',
      marker: { color: '#E74C3C' },
      line: { color: '#E74C3C', width: 3 },
    },
    {
      type: 'scatterpolar',
      r: top3Average.map(f => f.value),
      theta: top3Average.map(f => f.name),
      fill: 'toself',
      name: 'Top 3 Average',
      marker: { color: 'rgba(255, 255, 255, 0.3)' },
      line: { color: 'rgba(255, 255, 255, 0.5)', width: 2, dash: 'dash' },
    },
  ];

  const layout = {
    polar: {
      radialaxis: {
        visible: true,
        range: [0, 100],
        gridcolor: 'rgba(255, 255, 255, 0.1)',
        tickfont: { color: 'rgba(255, 255, 255, 0.6)', size: 10 },
      },
      angularaxis: {
        gridcolor: 'rgba(255, 255, 255, 0.1)',
        tickfont: { color: '#ffffff', size: 12, weight: 600 },
      },
      bgcolor: '#1a1a1a',
    },
    showlegend: true,
    legend: {
      x: 0.5,
      xanchor: 'center',
      y: -0.1,
      yanchor: 'top',
      orientation: 'h',
      font: { color: '#ffffff', size: 12 },
      bgcolor: 'rgba(0, 0, 0, 0)',
    },
    paper_bgcolor: '#1a1a1a',
    plot_bgcolor: '#1a1a1a',
    margin: { t: 40, r: 40, b: 80, l: 40 },
  };

  const config = {
    responsive: true,
    displayModeBar: false,
  };

  return (
    <div className="performance-radar">
      <h3 className="radar-title">PERFORMANCE COMPARISON</h3>
      <p className="radar-subtitle">Your vs Top 3 Average</p>
      <Plot
        data={data}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '400px' }}
      />
    </div>
  );
}
