/**
 * Driver Classification Utilities
 * Based on data analysis of 34-driver dataset
 */

// Classification tiers based on data analysis
export const CLASSIFICATIONS = {
  FRONTRUNNER: {
    id: 'FRONTRUNNER',
    label: 'Frontrunner',
    color: '#D4AF37', // Gold
    bgColor: '#FFF8DC',
    description: 'Proven race-winning capability',
    criteria: 'Overall 65+, 10+ races, avg finish <5'
  },
  CONTENDER: {
    id: 'CONTENDER',
    label: 'Contender',
    color: '#C0C0C0', // Silver
    bgColor: '#F5F5F5',
    description: 'Podium threats and high-potential prospects',
    criteria: 'Overall 60-65 OR Speed 70+ with <7 races'
  },
  MID_PACK: {
    id: 'MID_PACK',
    label: 'Mid-Pack',
    color: '#CD7F32', // Bronze
    bgColor: '#FFF5EE',
    description: 'Solid performers with development trajectory',
    criteria: 'Overall 50-60'
  },
  DEVELOPMENT: {
    id: 'DEVELOPMENT',
    label: 'Development Pool',
    color: '#6B7280', // Gray
    bgColor: '#F9FAFB',
    description: 'Long-term projects showing potential',
    criteria: 'Overall <50'
  }
};

/**
 * Classify a driver based on their stats
 * @param {Object} driver - Driver data from dashboardData.json
 * @returns {Object} Classification object
 */
export function classifyDriver(driver) {
  const overall = driver.overall_score || 0;
  const races = driver.races || 0;
  const avgFinish = driver.avg_finish || 999;
  const speed = driver.factors?.raw_speed?.percentile || 0;

  // FRONTRUNNER: 65+ overall, 10+ races, proven results
  if (overall >= 65 && races >= 10 && avgFinish < 5) {
    return {
      ...CLASSIFICATIONS.FRONTRUNNER,
      confidence: 95,
      reasoning: 'Elite performance with proven track record'
    };
  }

  // CONTENDER: 60-65 overall OR speed phenom
  if (overall >= 60 || (speed >= 70 && races <= 6)) {
    return {
      ...CLASSIFICATIONS.CONTENDER,
      confidence: 85,
      reasoning: speed >= 70 && races <= 6
        ? 'Elite raw speed with high upside potential'
        : 'Consistent podium-level performance'
    };
  }

  // MID-PACK: 50-60 overall
  if (overall >= 50) {
    return {
      ...CLASSIFICATIONS.MID_PACK,
      confidence: 80,
      reasoning: 'Solid points-scoring capability'
    };
  }

  // DEVELOPMENT: <50 overall
  return {
    ...CLASSIFICATIONS.DEVELOPMENT,
    confidence: 70,
    reasoning: 'Development case requiring structured program'
  };
}

/**
 * Get attribute tags for a driver
 * @param {Object} driver - Driver data
 * @returns {Array} Array of attribute tag objects
 */
export function getDriverTags(driver) {
  const tags = [];
  const speed = driver.factors?.raw_speed?.percentile || 0;
  const consistency = driver.factors?.consistency?.percentile || 0;
  const racecraft = driver.factors?.racecraft?.percentile || 0;
  const races = driver.races || 0;
  const overall = driver.overall_score || 0;

  // Performance tags
  if (speed >= 70) {
    tags.push({ type: 'SPEED', label: 'Speed Specialist', icon: '⚡' });
  }
  if (consistency >= 60) {
    tags.push({ type: 'CONSISTENT', label: 'Consistency Driver', icon: '🎯' });
  }
  if (racecraft >= 60) {
    tags.push({ type: 'WHEEL_TO_WHEEL', label: 'Wheel-to-Wheel', icon: '⚔️' });
  }

  // Experience tags
  if (races >= 10) {
    tags.push({ type: 'VETERAN', label: 'Veteran', icon: null });
  } else if (races >= 5) {
    tags.push({ type: 'DEVELOPING', label: 'Developing', icon: null });
  } else {
    tags.push({ type: 'ROOKIE', label: 'Rookie', icon: null });
  }

  // Potential tags
  if (speed > overall + 10) {
    tags.push({ type: 'HIGH_UPSIDE', label: 'High Upside', icon: '↗️' });
  }

  return tags;
}

/**
 * Apply filters to driver list
 * @param {Array} drivers - Array of driver objects
 * @param {Object} filters - Filter state from ScoutContext
 * @returns {Array} Filtered driver array
 */
export function applyFilters(drivers, filters) {
  return drivers.filter(driver => {
    // Search filter
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      const matchesNumber = driver.number.toString().includes(query);
      const matchesName = driver.name.toLowerCase().includes(query);
      if (!matchesNumber && !matchesName) return false;
    }

    // Classification filter
    if (filters.classification.length > 0) {
      const driverClass = classifyDriver(driver);
      if (!filters.classification.includes(driverClass.id)) return false;
    }

    // Experience filter
    if (filters.experience.length > 0) {
      const races = driver.races || 0;
      const hasVeteran = filters.experience.includes('VETERAN') && races >= 10;
      const hasDeveloping = filters.experience.includes('DEVELOPING') && races >= 5 && races < 10;
      const hasRookie = filters.experience.includes('ROOKIE') && races < 5;
      if (!hasVeteran && !hasDeveloping && !hasRookie) return false;
    }

    // Attribute filters
    if (filters.attributes.length > 0) {
      const tags = getDriverTags(driver);
      const tagTypes = tags.map(t => t.type);
      const hasMatchingAttribute = filters.attributes.some(attr => tagTypes.includes(attr));
      if (!hasMatchingAttribute) return false;
    }

    // Range filters
    const overall = driver.overall_score || 0;
    const speed = driver.factors?.raw_speed?.percentile || 0;
    const races = driver.races || 0;
    const avgFinish = driver.avg_finish || 0;

    if (overall < filters.overallRange[0] || overall > filters.overallRange[1]) return false;
    if (speed < filters.speedRange[0] || speed > filters.speedRange[1]) return false;
    if (races < filters.racesRange[0] || races > filters.racesRange[1]) return false;
    if (avgFinish < filters.avgFinishRange[0] || avgFinish > filters.avgFinishRange[1]) return false;

    return true;
  });
}

/**
 * Sort drivers based on criteria
 * @param {Array} drivers - Array of driver objects
 * @param {String} sortBy - Sort field
 * @param {String} sortOrder - 'asc' or 'desc'
 * @returns {Array} Sorted driver array
 */
export function sortDrivers(drivers, sortBy, sortOrder) {
  const sorted = [...drivers].sort((a, b) => {
    let aVal, bVal;

    switch (sortBy) {
      case 'overall_score':
        aVal = a.overall_score || 0;
        bVal = b.overall_score || 0;
        break;
      case 'speed':
        aVal = a.factors?.raw_speed?.percentile || 0;
        bVal = b.factors?.raw_speed?.percentile || 0;
        break;
      case 'consistency':
        aVal = a.factors?.consistency?.percentile || 0;
        bVal = b.factors?.consistency?.percentile || 0;
        break;
      case 'avg_finish':
        aVal = a.avg_finish || 999;
        bVal = b.avg_finish || 999;
        break;
      case 'races':
        aVal = a.races || 0;
        bVal = b.races || 0;
        break;
      case 'number':
        aVal = a.number;
        bVal = b.number;
        break;
      default:
        aVal = a.overall_score || 0;
        bVal = b.overall_score || 0;
    }

    if (sortOrder === 'asc') {
      return aVal - bVal;
    } else {
      return bVal - aVal;
    }
  });

  return sorted;
}

/**
 * Get data confidence level based on race count
 * @param {Number} races - Number of races
 * @returns {Object} Confidence object
 */
export function getDataConfidence(races) {
  if (races >= 10) {
    return {
      level: 'HIGH',
      label: 'Established profile',
      color: '#10B981',
      showWarning: false
    };
  } else if (races >= 5) {
    return {
      level: 'MODERATE',
      label: 'Developing profile',
      color: '#F59E0B',
      showWarning: true,
      message: 'Metrics stabilizing with more race data'
    };
  } else {
    return {
      level: 'LOW',
      label: 'Limited sample size',
      color: '#EF4444',
      showWarning: true,
      message: 'Metrics subject to significant change'
    };
  }
}
