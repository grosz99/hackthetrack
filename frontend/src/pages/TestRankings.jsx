import { useState, useEffect } from 'react';

export default function TestRankings() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/drivers')
      .then(res => res.json())
      .then(data => {
        console.log('Raw API data:', data);
        setData(data);
      })
      .catch(err => {
        console.error('Error:', err);
        setError(err.message);
      });
  }, []);

  return (
    <div style={{ padding: '2rem', color: 'white', background: '#0a0a0a', minHeight: '100vh' }}>
      <h1>TEST PAGE - API Data Check</h1>

      {error && <div style={{ color: 'red' }}>Error: {error}</div>}

      {data && (
        <div>
          <p>Total drivers: {data.length}</p>
          <pre style={{ background: '#1a1a1a', padding: '1rem', overflow: 'auto', maxHeight: '600px' }}>
            {JSON.stringify(data.slice(0, 3), null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
