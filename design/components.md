# Component Patterns

React component examples and code patterns for building consistent dashboard UI elements.

## Base Card Component

All dashboard content should be wrapped in cards with the signature red border.

```jsx
const Card = ({ children, className = '' }) => (
  <div className={`
    bg-white
    border-[3px] border-[#E74C3C]
    rounded-xl
    p-8
    ${className}
  `}>
    {children}
  </div>
);
```

## Metric Card

Small cards showing a single metric with large number, label, progress bar, and description.

```jsx
const MetricCard = ({ 
  title, 
  value, 
  percentile, 
  percentileValue,
  description,
  valueColor = '#E74C3C' 
}) => (
  <Card>
    <div className="flex flex-col h-full">
      {/* Header with title and value */}
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wide text-black">
          {title}
        </h3>
        <div className="text-5xl font-extrabold" style={{ color: valueColor }}>
          {value}
        </div>
      </div>
      
      {/* Percentile label */}
      <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">
        {percentile}
      </div>
      
      {/* Progress bar */}
      <div className="w-full h-2 bg-gray-200 rounded-full mb-4">
        <div 
          className="h-full bg-[#E74C3C] rounded-full"
          style={{ width: `${percentileValue}%` }}
        />
      </div>
      
      {/* Description */}
      <p className="text-sm text-gray-600 leading-relaxed">
        {description}
      </p>
    </div>
  </Card>
);

// Usage
<MetricCard
  title="CONSISTENCY"
  value="66"
  percentile="66TH PERCENTILE"
  percentileValue={66}
  description="Measures lap-to-lap consistency and predictability of performance"
/>
```

## Large Stat Card

Cards showing large metrics with labels underneath (like Season Averages).

```jsx
const StatCard = ({ value, label, valueColor = '#000000', prefix = '' }) => (
  <Card>
    <div className="flex flex-col items-center justify-center py-6">
      <div 
        className="text-6xl font-extrabold mb-2"
        style={{ color: valueColor }}
      >
        {prefix}{value}
      </div>
      <div className="text-xs uppercase tracking-wider text-gray-500">
        {label}
      </div>
    </div>
  </Card>
);

// Usage - Three stats in a row
<div className="grid grid-cols-3 gap-4">
  <StatCard value="5.0" label="AVG START POSITION" />
  <StatCard value="2.8" label="AVG FINISH POSITION" />
  <StatCard 
    value="2.3" 
    label="AVG POSITION GAIN" 
    valueColor="#2ECC71"
    prefix="+"
  />
</div>
```

## Chart Card

Card containing data visualizations.

```jsx
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Legend } from 'recharts';

const ChartCard = ({ title, subtitle, data, children }) => (
  <Card>
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-black mb-1">
        {title}
      </h2>
      {subtitle && (
        <p className="text-sm text-gray-600">
          {subtitle}
        </p>
      )}
    </div>
    {children}
  </Card>
);

// Usage with line chart
<ChartCard 
  title="Race by Race Performance"
  subtitle="Starting vs Finishing Position"
>
  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={raceData}>
      <XAxis 
        dataKey="race" 
        stroke="#95A5A6"
        style={{ fontSize: '12px' }}
      />
      <YAxis 
        reversed
        stroke="#95A5A6"
        style={{ fontSize: '12px' }}
      />
      <Line 
        type="monotone" 
        dataKey="startPosition" 
        stroke="#95A5A6" 
        strokeWidth={2}
        dot={{ fill: '#95A5A6', r: 5 }}
      />
      <Line 
        type="monotone" 
        dataKey="finishPosition" 
        stroke="#E74C3C" 
        strokeWidth={2}
        dot={{ fill: '#E74C3C', r: 5 }}
      />
      <Legend 
        verticalAlign="bottom"
        height={36}
        iconType="circle"
      />
    </LineChart>
  </ResponsiveContainer>
</ChartCard>
```

## Radar Chart Component

For multi-dimensional performance comparisons.

```jsx
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, Legend } from 'recharts';

const PerformanceRadar = ({ data, series }) => (
  <ChartCard 
    title="PERFORMANCE COMPARISON"
    subtitle="You vs Top 3 Drivers"
  >
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart data={data}>
        <PolarGrid stroke="#E0E0E0" />
        <PolarAngleAxis 
          dataKey="metric" 
          tick={{ fontSize: 12, fill: '#666' }}
        />
        
        {/* Your performance - primary red */}
        <Radar 
          name="You (#13)" 
          dataKey="you" 
          stroke="#E74C3C" 
          fill="rgba(231, 76, 60, 0.25)" 
          strokeWidth={2}
        />
        
        {/* Comparison drivers - grays */}
        <Radar 
          name="Top Driver #22" 
          dataKey="top1" 
          stroke="#7F8C8D" 
          fill="rgba(127, 140, 141, 0.1)" 
          strokeWidth={1}
        />
        
        <Legend 
          verticalAlign="bottom"
          height={36}
        />
      </RadarChart>
    </ResponsiveContainer>
  </ChartCard>
);
```

## Data Table

Clean table with uppercase headers and minimal styling.

```jsx
const DataTable = ({ columns, data, onRowClick }) => (
  <Card>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            {columns.map((col, idx) => (
              <th 
                key={idx}
                className="text-left text-xs uppercase tracking-wider text-gray-500 pb-3 font-semibold"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr 
              key={rowIdx}
              onClick={() => onRowClick?.(row)}
              className={`
                border-b border-gray-100 last:border-0
                ${onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}
              `}
            >
              {columns.map((col, colIdx) => (
                <td 
                  key={colIdx}
                  className="py-4 text-sm text-black"
                >
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </Card>
);

// Usage
const columns = [
  { header: 'Round', key: 'round' },
  { header: 'Track', key: 'track' },
  { header: 'Qualifying Time', key: 'qualTime' },
  { header: 'Start', key: 'start' },
  { header: 'Finish', key: 'finish' },
  { 
    header: 'Change', 
    key: 'change',
    render: (value) => (
      <span className={value > 0 ? 'text-green-600' : 'text-red-600'}>
        {value > 0 ? '↑' : '↓'} {Math.abs(value)}
      </span>
    )
  },
];

<DataTable columns={columns} data={raceResults} onRowClick={handleRowClick} />
```

## Progress Bar

Horizontal progress indicator used in metric cards.

```jsx
const ProgressBar = ({ value, max = 100, color = '#E74C3C' }) => (
  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
    <div 
      className="h-full rounded-full transition-all duration-300"
      style={{ 
        width: `${(value / max) * 100}%`,
        backgroundColor: color 
      }}
    />
  </div>
);

// With label
const ProgressBarWithLabel = ({ label, value, max = 100 }) => (
  <div className="space-y-2">
    <div className="flex justify-between text-xs">
      <span className="uppercase tracking-wider text-gray-500">{label}</span>
      <span className="font-bold text-black">{value}%</span>
    </div>
    <ProgressBar value={value} max={max} />
  </div>
);
```

## Circular Button

Red circular button typically used for navigation or actions.

```jsx
const CircularButton = ({ onClick, icon, label }) => (
  <button
    onClick={onClick}
    className="
      bg-[#E74C3C] hover:bg-[#C0392B]
      text-white
      rounded-full
      w-16 h-16
      flex flex-col items-center justify-center
      shadow-lg hover:shadow-xl
      transition-all duration-200
      hover:scale-105
    "
    aria-label={label}
  >
    <div className="text-2xl mb-1">{icon}</div>
    {label && (
      <div className="text-[8px] uppercase font-semibold tracking-wider">
        {label}
      </div>
    )}
  </button>
);

// Usage
<CircularButton 
  icon="→" 
  label="See Race Logs"
  onClick={() => navigate('/race-logs')}
/>
```

## Section Header

Headers for different sections on dark backgrounds.

```jsx
const SectionHeader = ({ children, subtitle }) => (
  <div className="mb-6">
    <h2 className="text-3xl font-bold text-white mb-2">
      {children}
    </h2>
    {subtitle && (
      <p className="text-gray-400 text-sm italic">
        {subtitle}
      </p>
    )}
  </div>
);

// Usage on dark background
<SectionHeader subtitle="Click rows for race lap time analysis">
  2025 Season Results
</SectionHeader>
```

## Grid Layouts

Common grid patterns for cards.

```jsx
// Two-column layout
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  <MetricCard {...props} />
  <MetricCard {...props} />
</div>

// Three-column layout
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <StatCard {...props} />
  <StatCard {...props} />
  <StatCard {...props} />
</div>

// Mixed layout - large left, small right
<div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
  <div className="lg:col-span-2">
    <ChartCard {...props} />
  </div>
  <div className="grid grid-cols-1 gap-4">
    <MetricCard {...props} />
    <MetricCard {...props} />
  </div>
</div>

// Four-column metric grid (2x2)
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
  <MetricCard {...props} />
  <MetricCard {...props} />
  <MetricCard {...props} />
  <MetricCard {...props} />
</div>
```

## Page Layout Template

Complete page structure with dark background and cards.

```jsx
const DashboardPage = ({ children }) => (
  <div className="min-h-screen bg-[#1A1A1A] text-white">
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {children}
    </div>
  </div>
);

// Usage
<DashboardPage>
  <SectionHeader subtitle="Your performance breakdown">
    Driver Performance
  </SectionHeader>
  
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <div className="lg:col-span-2">
      <ChartCard {...radarProps} />
    </div>
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
      <MetricCard {...consistencyProps} />
      <MetricCard {...racecraftProps} />
    </div>
  </div>
  
  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
    <StatCard {...avgStartProps} />
    <StatCard {...avgFinishProps} />
    <StatCard {...avgGainProps} />
  </div>
  
  <DataTable {...resultsTableProps} />
</DashboardPage>
```

## Styling Tips

### Tailwind Classes
If using Tailwind, configure custom colors:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'racing-red': '#E74C3C',
        'racing-bg': '#1A1A1A',
        'racing-success': '#2ECC71',
      },
    },
  },
};
```

### Inline Styles
For dynamic values or precise colors:

```jsx
<div style={{ 
  color: '#E74C3C',
  borderColor: '#E74C3C',
  width: `${percentage}%` 
}} />
```

### CSS Modules
For component-specific styles:

```css
/* MetricCard.module.css */
.card {
  background: white;
  border: 3px solid #E74C3C;
  border-radius: 12px;
  padding: 32px;
}

.metricValue {
  font-size: 48px;
  font-weight: 800;
  color: #E74C3C;
}
```

## Accessibility Considerations

- Ensure contrast ratios meet WCAG AA standards (white text on dark backgrounds is good)
- Add `aria-label` to icon-only buttons
- Include proper heading hierarchy (h1 → h2 → h3)
- Make interactive elements keyboard accessible
- Provide text alternatives for charts/visualizations
- Use semantic HTML elements (`<table>`, `<button>`, etc.)

## Responsive Design

```jsx
// Stack on mobile, side-by-side on desktop
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">

// Hide on mobile, show on desktop
<div className="hidden lg:block">

// Adjust font sizes
<h1 className="text-2xl md:text-3xl lg:text-4xl">

// Adjust padding
<div className="p-4 md:p-6 lg:p-8">
```
