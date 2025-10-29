// Mock data for Toyota Gazoo Racing Dashboard

// Driver data with 4-factor scores
export const drivers = [
  {
    number: 13,
    name: "Driver #13",
    overall_score: 95,
    grade: "Elite",
    percentile: 95,
    races: 12,
    factors: {
      raw_speed: { score: 98, z_score: -0.88, rank: "2/35", percentile: 94, trend: "up" },
      consistency: { score: 92, z_score: -0.82, rank: "8/35", percentile: 77, trend: "stable" },
      racecraft: { score: 68, z_score: -0.18, rank: "18/35", percentile: 49, trend: "stable" },
      tire_mgmt: { score: 75, z_score: -0.20, rank: "20/35", percentile: 43, trend: "down" }
    },
    best_tracks: ["sebring", "cota", "sonoma"],
    worst_tracks: ["roadamerica", "vir", "barber"]
  },
  {
    number: 2,
    name: "Driver #2",
    overall_score: 88,
    grade: "Strong",
    percentile: 85,
    races: 12,
    factors: {
      raw_speed: { score: 85, z_score: -0.40, rank: "8/35", percentile: 77, trend: "up" },
      consistency: { score: 82, z_score: -0.35, rank: "12/35", percentile: 66, trend: "up" },
      racecraft: { score: 95, z_score: -1.20, rank: "1/35", percentile: 97, trend: "stable" },
      tire_mgmt: { score: 78, z_score: -0.25, rank: "18/35", percentile: 49, trend: "stable" }
    },
    best_tracks: ["roadamerica", "barber", "vir"],
    worst_tracks: ["sebring", "cota", "sonoma"]
  },
  {
    number: 7,
    name: "Driver #7",
    overall_score: 84,
    grade: "Strong",
    percentile: 80,
    races: 12,
    factors: {
      raw_speed: { score: 88, z_score: -0.55, rank: "5/35", percentile: 86, trend: "stable" },
      consistency: { score: 90, z_score: -0.75, rank: "6/35", percentile: 83, trend: "up" },
      racecraft: { score: 65, z_score: -0.10, rank: "20/35", percentile: 43, trend: "stable" },
      tire_mgmt: { score: 72, z_score: -0.10, rank: "22/35", percentile: 37, trend: "down" }
    },
    best_tracks: ["vir", "barber", "cota"],
    worst_tracks: ["sebring", "roadamerica", "sonoma"]
  },
  {
    number: 21,
    name: "Driver #21",
    overall_score: 78,
    grade: "Average",
    percentile: 65,
    races: 12,
    factors: {
      raw_speed: { score: 75, z_score: 0.10, rank: "18/35", percentile: 49, trend: "up" },
      consistency: { score: 78, z_score: -0.15, rank: "15/35", percentile: 57, trend: "up" },
      racecraft: { score: 72, z_score: -0.25, rank: "16/35", percentile: 54, trend: "stable" },
      tire_mgmt: { score: 68, z_score: 0.05, rank: "24/35", percentile: 31, trend: "stable" }
    },
    best_tracks: ["barber", "vir", "cota"],
    worst_tracks: ["sebring", "roadamerica", "sonoma"]
  },
  {
    number: 22,
    name: "Driver #22",
    overall_score: 81,
    grade: "Strong",
    percentile: 75,
    races: 12,
    factors: {
      raw_speed: { score: 82, z_score: -0.30, rank: "10/35", percentile: 71, trend: "stable" },
      consistency: { score: 85, z_score: -0.45, rank: "10/35", percentile: 71, trend: "up" },
      racecraft: { score: 70, z_score: -0.20, rank: "17/35", percentile: 51, trend: "stable" },
      tire_mgmt: { score: 74, z_score: -0.15, rank: "21/35", percentile: 40, trend: "stable" }
    },
    best_tracks: ["cota", "barber", "vir"],
    worst_tracks: ["roadamerica", "sebring", "sonoma"]
  },
  {
    number: 31,
    name: "Driver #31",
    overall_score: 68,
    grade: "Average",
    percentile: 45,
    races: 12,
    factors: {
      raw_speed: { score: 65, z_score: 0.40, rank: "25/35", percentile: 29, trend: "stable" },
      consistency: { score: 70, z_score: 0.15, rank: "22/35", percentile: 37, trend: "stable" },
      racecraft: { score: 68, z_score: -0.05, rank: "19/35", percentile: 46, trend: "up" },
      tire_mgmt: { score: 55, z_score: 0.85, rank: "30/35", percentile: 14, trend: "down" }
    },
    best_tracks: ["barber", "vir", "roadamerica"],
    worst_tracks: ["sebring", "cota", "sonoma"]
  },
  {
    number: 42,
    name: "Driver #42",
    overall_score: 72,
    grade: "Average",
    percentile: 55,
    races: 12,
    factors: {
      raw_speed: { score: 70, z_score: 0.25, rank: "22/35", percentile: 37, trend: "stable" },
      consistency: { score: 75, z_score: 0.00, rank: "18/35", percentile: 49, trend: "up" },
      racecraft: { score: 74, z_score: -0.30, rank: "14/35", percentile: 60, trend: "up" },
      tire_mgmt: { score: 65, z_score: 0.20, rank: "26/35", percentile: 26, trend: "stable" }
    },
    best_tracks: ["vir", "roadamerica", "barber"],
    worst_tracks: ["sebring", "cota", "sonoma"]
  },
  {
    number: 52,
    name: "Driver #52",
    overall_score: 75,
    grade: "Average",
    percentile: 60,
    races: 12,
    factors: {
      raw_speed: { score: 78, z_score: 0.05, rank: "16/35", percentile: 54, trend: "up" },
      consistency: { score: 80, z_score: -0.20, rank: "14/35", percentile: 60, trend: "stable" },
      racecraft: { score: 62, z_score: 0.10, rank: "22/35", percentile: 37, trend: "stable" },
      tire_mgmt: { score: 70, z_score: 0.00, rank: "23/35", percentile: 34, trend: "up" }
    },
    best_tracks: ["barber", "vir", "cota"],
    worst_tracks: ["sebring", "roadamerica", "sonoma"]
  },
  {
    number: 57,
    name: "Driver #57",
    overall_score: 58,
    grade: "Developing",
    percentile: 30,
    races: 12,
    factors: {
      raw_speed: { score: 25, z_score: 2.05, rank: "33/35", percentile: 6, trend: "stable" },
      consistency: { score: 65, z_score: 0.30, rank: "26/35", percentile: 26, trend: "up" },
      racecraft: { score: 60, z_score: 0.20, rank: "24/35", percentile: 31, trend: "stable" },
      tire_mgmt: { score: 62, z_score: 0.30, rank: "27/35", percentile: 23, trend: "down" }
    },
    best_tracks: ["barber", "vir", "roadamerica"],
    worst_tracks: ["sebring", "cota", "sonoma"]
  },
  {
    number: 63,
    name: "Driver #63",
    overall_score: 70,
    grade: "Average",
    percentile: 50,
    races: 12,
    factors: {
      raw_speed: { score: 68, z_score: 0.30, rank: "24/35", percentile: 31, trend: "stable" },
      consistency: { score: 72, z_score: 0.10, rank: "20/35", percentile: 43, trend: "stable" },
      racecraft: { score: 75, z_score: -0.35, rank: "13/35", percentile: 63, trend: "up" },
      tire_mgmt: { score: 68, z_score: 0.05, rank: "25/35", percentile: 29, trend: "stable" }
    },
    best_tracks: ["roadamerica", "barber", "vir"],
    worst_tracks: ["sebring", "cota", "sonoma"]
  },
  {
    number: 80,
    name: "Driver #80",
    overall_score: 62,
    grade: "Average",
    percentile: 40,
    races: 12,
    factors: {
      raw_speed: { score: 60, z_score: 0.60, rank: "28/35", percentile: 20, trend: "stable" },
      consistency: { score: 45, z_score: 0.92, rank: "32/35", percentile: 9, trend: "down" },
      racecraft: { score: 65, z_score: -0.10, rank: "21/35", percentile: 40, trend: "stable" },
      tire_mgmt: { score: 58, z_score: 0.50, rank: "29/35", percentile: 17, trend: "stable" }
    },
    best_tracks: ["roadamerica", "vir", "barber"],
    worst_tracks: ["sebring", "cota", "sonoma"]
  }
];

// Track data with circuit characteristics
export const tracks = [
  {
    id: "barber",
    name: "Barber Motorsports Park",
    location: "Birmingham, AL",
    length: "2.38 miles",
    mapUrl: "/track_maps/barber.png",
    demands: {
      raw_speed: 6.37,
      consistency: 9.94,
      racecraft: -1.08,
      tire_mgmt: 5.59
    },
    description: "High tire degradation, hard to pass"
  },
  {
    id: "cota",
    name: "Circuit of The Americas",
    location: "Austin, TX",
    length: "3.41 miles",
    mapUrl: "/track_maps/cota.png",
    demands: {
      raw_speed: 6.85,
      consistency: 4.20,
      racecraft: 1.15,
      tire_mgmt: 2.30
    },
    description: "Balanced track, rewards speed and consistency"
  },
  {
    id: "roadamerica",
    name: "Road America",
    location: "Elkhart Lake, WI",
    length: "4.05 miles",
    mapUrl: "/track_maps/roadamerica.png",
    demands: {
      raw_speed: 5.85,
      consistency: 8.50,
      racecraft: 2.45,
      tire_mgmt: 3.80
    },
    description: "Fast, flowing, rewards racecraft"
  },
  {
    id: "sebring",
    name: "Sebring International",
    location: "Sebring, FL",
    length: "3.74 miles",
    mapUrl: "/track_maps/sebring.png",
    demands: {
      raw_speed: 7.08,
      consistency: 3.74,
      racecraft: 0.91,
      tire_mgmt: 1.51
    },
    description: "Power track, low degradation, rewards raw speed"
  },
  {
    id: "sonoma",
    name: "Sonoma Raceway",
    location: "Sonoma, CA",
    length: "2.52 miles",
    mapUrl: "/track_maps/sonoma.png",
    demands: {
      raw_speed: 6.50,
      consistency: 5.20,
      racecraft: 1.80,
      tire_mgmt: 2.10
    },
    description: "Technical, elevation changes"
  },
  {
    id: "vir",
    name: "Virginia International Raceway",
    location: "Alton, VA",
    length: "3.27 miles",
    mapUrl: "/track_maps/vir.png",
    demands: {
      raw_speed: 5.19,
      consistency: 9.07,
      racecraft: 1.35,
      tire_mgmt: -0.19
    },
    description: "Technical, balanced, tire mgmt doesn't matter"
  }
];

// Calculate circuit fit score for a driver at a track
export const calculateCircuitFit = (driver, track) => {
  const driverFactors = driver.factors;
  const trackDemands = track.demands;

  // Dot product of driver skill z-scores and track demands
  const fitScore =
    (driverFactors.raw_speed.z_score * trackDemands.raw_speed) +
    (driverFactors.consistency.z_score * trackDemands.consistency) +
    (driverFactors.racecraft.z_score * trackDemands.racecraft) +
    (driverFactors.tire_mgmt.z_score * trackDemands.tire_mgmt);

  // Convert to 0-100 scale (higher is better)
  // Negative fitScore is good (negative z-scores * positive coefficients)
  const normalized = 50 - (fitScore * 5);
  return Math.max(0, Math.min(100, Math.round(normalized)));
};

// Generate telemetry data for comparison charts
export const generateTelemetryData = (track, driver) => {
  const numPoints = 100;
  const data = {
    distance: [],
    driverSpeed: [],
    winnerSpeed: [],
    driverGForce: [],
    winnerGForce: [],
    driverThrottle: [],
    winnerThrottle: [],
    driverBrake: [],
    winnerBrake: []
  };

  for (let i = 0; i < numPoints; i++) {
    const distance = (i / numPoints) * 100; // 0-100% of lap
    data.distance.push(distance);

    // Speed varies with track sections (straights vs corners)
    const baseSpeed = 120 + 40 * Math.sin(distance * 0.15);
    const driverSkillFactor = (driver.factors.raw_speed.score - 50) / 50; // -1 to 1

    data.driverSpeed.push(baseSpeed + driverSkillFactor * 10 + Math.random() * 3);
    data.winnerSpeed.push(baseSpeed + 8 + Math.random() * 3);

    // G-forces in corners
    const cornerFactor = Math.abs(Math.sin(distance * 0.2));
    data.driverGForce.push(cornerFactor * 2.5 + Math.random() * 0.2);
    data.winnerGForce.push(cornerFactor * 2.6 + Math.random() * 0.2);

    // Throttle and brake (inverse relationship)
    const throttleFactor = (Math.sin(distance * 0.15) + 1) / 2;
    data.driverThrottle.push(throttleFactor * 100);
    data.winnerThrottle.push(throttleFactor * 100);
    data.driverBrake.push((1 - throttleFactor) * 100);
    data.winnerBrake.push((1 - throttleFactor) * 100);
  }

  return data;
};

// Model statistics
export const modelStats = {
  r_squared: 0.895,
  cross_val_r_squared: 0.877,
  mae: 1.78,
  races_analyzed: 291
};

// Factor explanations
export const factorInfo = {
  raw_speed: {
    name: "Raw Speed",
    weight: "50%",
    color: "#FF4444",
    description: "Outright car pace - qualifying, best lap, sustained speed",
    icon: "⚡"
  },
  consistency: {
    name: "Consistency",
    weight: "31%",
    color: "#4444FF",
    description: "Lap-to-lap consistency, braking repeatability, smoothness",
    icon: "🎯"
  },
  racecraft: {
    name: "Racecraft",
    weight: "16%",
    color: "#FF9900",
    description: "Ability to pass cars, gain positions during race",
    icon: "⚔️"
  },
  tire_mgmt: {
    name: "Tire Management",
    weight: "10%",
    color: "#00CC66",
    description: "Ability to maintain pace over long stints, preserve tires",
    icon: "🏁"
  }
};
