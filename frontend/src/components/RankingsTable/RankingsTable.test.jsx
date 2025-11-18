import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RankingsTable from './RankingsTable';

describe('RankingsTable Component', () => {
  const mockDrivers = [
    {
      driver_number: 7,
      name: 'Joe Doe',
      overall_score: 85.5,
      speed: 88.2,
      consistency: 82.1,
      racecraft: 85.0,
      tire_management: 87.3,
    },
    {
      driver_number: 13,
      name: 'Jane Smith',
      overall_score: 83.2,
      speed: 85.5,
      consistency: 80.2,
      racecraft: 83.8,
      tire_management: 84.1,
    },
  ];

  it('should render driver rankings', () => {
    render(
      <BrowserRouter>
        <RankingsTable drivers={mockDrivers} />
      </BrowserRouter>
    );

    expect(screen.getByText('Joe Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('should display overall scores', () => {
    render(
      <BrowserRouter>
        <RankingsTable drivers={mockDrivers} />
      </BrowserRouter>
    );

    expect(screen.getByText('85.5')).toBeInTheDocument();
    expect(screen.getByText('83.2')).toBeInTheDocument();
  });

  it('should display driver numbers', () => {
    render(
      <BrowserRouter>
        <RankingsTable drivers={mockDrivers} />
      </BrowserRouter>
    );

    expect(screen.getByText('#7')).toBeInTheDocument();
    expect(screen.getByText('#13')).toBeInTheDocument();
  });

  it('should render empty state when no drivers', () => {
    render(
      <BrowserRouter>
        <RankingsTable drivers={[]} />
      </BrowserRouter>
    );

    // Table should still render but be empty
    const table = screen.queryByRole('table');
    expect(table).toBeInTheDocument();
  });

  it('should handle missing factor scores gracefully', () => {
    const driversWithMissingData = [
      {
        driver_number: 99,
        name: 'Incomplete Driver',
        overall_score: 75.0,
        // Missing individual factor scores
      },
    ];

    render(
      <BrowserRouter>
        <RankingsTable drivers={driversWithMissingData} />
      </BrowserRouter>
    );

    expect(screen.getByText('Incomplete Driver')).toBeInTheDocument();
    expect(screen.getByText('75.0')).toBeInTheDocument();
  });

  it('should sort drivers by overall score (descending)', () => {
    const { container } = render(
      <BrowserRouter>
        <RankingsTable drivers={mockDrivers} />
      </BrowserRouter>
    );

    const rows = container.querySelectorAll('tbody tr');
    expect(rows.length).toBe(2);

    // First driver should be Joe Doe (85.5) before Jane Smith (83.2)
    expect(rows[0]).toHaveTextContent('Joe Doe');
    expect(rows[1]).toHaveTextContent('Jane Smith');
  });
});
