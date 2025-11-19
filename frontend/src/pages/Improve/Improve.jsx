/**
 * Driver Development Page - AI-Guided Skill Improvement
 * Streamlined flow: AI Recommendation → Skill Sliders → Best Match → Track-Specific Actions
 */

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import SkillSliders from './components/SkillSliders';
import './Improve.css';

export default function Improve() {
  const { selectedDriverNumber } = useDriver();

  const [driverData, setDriverData] = useState(null);
  const [coachingRecommendations, setCoachingRecommendations] = useState(null);
  const [recommendedAllocation, setRecommendedAllocation] = useState(null);
  const [targetSkills, setTargetSkills] = useState(null);
  const [bestMatch, setBestMatch] = useState(null);
  const [matchCoachingData, setMatchCoachingData] = useState(null);
  const [liveCoachingInsights, setLiveCoachingInsights] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [selectedTrack, setSelectedTrack] = useState('barber');
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [matchingData, setMatchingData] = useState(null);

  const tracks = [
    { id: 'barber', name: 'Barber Motorsports Park' },
    { id: 'cota', name: 'Circuit of the Americas' },
    { id: 'roadamerica', name: 'Road America' },
    { id: 'sebring', name: 'Sebring International' },
    { id: 'sonoma', name: 'Sonoma Raceway' },
    { id: 'vir', name: 'Virginia International Raceway' }
  ];

  // Generate AI-recommended budget allocation based on weaknesses
  const generateRecommendedAllocation = (driverFactors, coaching) => {
    const factors = ['speed', 'consistency', 'racecraft', 'tire_management'];
    const MAX_BUDGET = 5;

    // Get percentiles for each factor
    const weaknesses = factors.map(factor => ({
      factor,
      percentile: driverFactors[factor]?.percentile || 50,
      coaching: coaching?.[factor]?.coaching_analysis || ''
    })).sort((a, b) => a.percentile - b.percentile);

    // Allocate budget - weakest gets most
    const allocation = { speed: 0, consistency: 0, racecraft: 0, tire_management: 0 };
    let remaining = MAX_BUDGET;

    // Weakest area gets 3% if really weak, else 2%
    if (weaknesses[0].percentile < 40) {
      allocation[weaknesses[0].factor] = 3;
      remaining -= 3;
    } else {
      allocation[weaknesses[0].factor] = 2;
      remaining -= 2;
    }

    // Second weakest gets 1-2%
    allocation[weaknesses[1].factor] = Math.min(2, remaining);
    remaining -= allocation[weaknesses[1].factor];

    // Remaining to third if any
    if (remaining > 0) {
      allocation[weaknesses[2].factor] = remaining;
    }

    const factorDisplayNames = {
      speed: 'Speed',
      consistency: 'Consistency',
      racecraft: 'Racecraft',
      tire_management: 'Tire Management'
    };

    return {
      allocation,
      weakestFactor: factorDisplayNames[weaknesses[0].factor],
      weakestPercentile: weaknesses[0].percentile.toFixed(0),
      reasoning: `Your weakest area is ${factorDisplayNames[weaknesses[0].factor]} (${weaknesses[0].percentile.toFixed(0)}th percentile). Focus your budget here for maximum improvement impact.`
    };
  };

  // Load driver data and AI coaching recommendations
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        setBestMatch(null);

        // Get driver data
        const driverResponse = await api.get(`/api/drivers/${selectedDriverNumber}`);
        setDriverData(driverResponse.data);

        // Get AI coaching recommendations for all factors (handle missing data gracefully)
        const coachingPromises = ['speed', 'consistency', 'racecraft', 'tire_management'].map(
          factor => api.get(`/api/factors/${factor}/coaching/${selectedDriverNumber}`)
            .catch(() => ({ data: null })) // Handle 404s gracefully
        );
        const coachingResults = await Promise.all(coachingPromises);

        const coachingData = {
          speed: coachingResults[0].data,
          consistency: coachingResults[1].data,
          racecraft: coachingResults[2].data,
          tire_management: coachingResults[3].data
        };
        setCoachingRecommendations(coachingData);

        // Generate AI-recommended allocation and auto-apply it
        const recommendation = generateRecommendedAllocation(driverResponse.data, coachingData);
        setRecommendedAllocation(recommendation);

        // Auto-apply the recommendation to pre-fill sliders
        const autoTargets = {
          speed: (driverResponse.data.speed?.percentile || 0) + recommendation.allocation.speed,
          consistency: (driverResponse.data.consistency?.percentile || 0) + recommendation.allocation.consistency,
          racecraft: (driverResponse.data.racecraft?.percentile || 0) + recommendation.allocation.racecraft,
          tire_management: (driverResponse.data.tire_management?.percentile || 0) + recommendation.allocation.tire_management
        };
        setTargetSkills(autoTargets);

      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load performance data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedDriverNumber]);

  // Handle applying AI recommendation
  const handleApplyRecommendation = () => {
    if (!recommendedAllocation || !driverData) return;

    const newTargets = {
      speed: (driverData.speed?.percentile || 0) + recommendedAllocation.allocation.speed,
      consistency: (driverData.consistency?.percentile || 0) + recommendedAllocation.allocation.consistency,
      racecraft: (driverData.racecraft?.percentile || 0) + recommendedAllocation.allocation.racecraft,
      tire_management: (driverData.tire_management?.percentile || 0) + recommendedAllocation.allocation.tire_management
    };

    setTargetSkills(newTargets);
  };

  // Handle target skills change from sliders
  const handleTargetChange = (newTargets) => {
    setTargetSkills(newTargets);
  };

  // Find best matching driver based on target skills
  const handleFindBestMatch = async () => {
    if (!targetSkills) return;

    try {
      console.log('🔍 Finding best match for driver:', selectedDriverNumber);
      setSearching(true);
      setBestMatch(null);
      setMatchCoachingData(null);
      setLiveCoachingInsights(null);
      setMatchingData(null);

      // Call backend API to find similar drivers (returns top 1)
      const response = await api.post('/api/drivers/find-similar', {
        current_driver_number: selectedDriverNumber,
        target_skills: targetSkills
      });
      console.log('📡 API Response:', response.data);

      // Store matching algorithm data for transparency
      if (response.data.matching_algorithm) {
        setMatchingData(response.data.matching_algorithm);
      }

      // Handle both normal matches AND elite drivers with empty array + message
      // (Backend should return elite drivers in array, but handle legacy response too)
      if (response.data.similar_drivers?.length > 0) {
        // Regular match or elite self-match in array
        const match = response.data.similar_drivers[0];
        console.log('✅ Best match found:', match);
        setBestMatch(match);
        setSearching(false);

        // Fetch LIVE coaching insights via Claude API
        if (!match.is_elite_self_match) {
          // Regular match - comparative insights
          const primaryFactor = getPrimaryImprovementFactor();
          const improvement = getPrimaryImprovement();
          if (primaryFactor && improvement && improvement.delta > 0) {
            setLoadingInsights(true);
            try {
              const insightsResponse = await api.post('/api/coaching/comparative-insights', {
                current_driver_number: selectedDriverNumber,
                comparable_driver_number: match.driver_number,
                factor_name: primaryFactor,
                improvement_delta: improvement.delta,
                track_name: tracks.find(t => t.id === selectedTrack)?.name || selectedTrack
              });
              setLiveCoachingInsights(insightsResponse.data.insights);
            } catch (insightErr) {
              console.error('Error fetching live coaching insights:', insightErr);
              setLiveCoachingInsights(null);
            } finally {
              setLoadingInsights(false);
            }
          }
        } else {
          // Top driver - self-improvement insights
          const primaryFactor = getPrimaryImprovementFactor();
          if (primaryFactor && match.losses_to_analyze && match.losses_to_analyze.length > 0) {
            setLoadingInsights(true);
            try {
              const insightsResponse = await api.post('/api/coaching/top-driver-insights', {
                driver_number: selectedDriverNumber,
                target_factor: primaryFactor,
                track_name: tracks.find(t => t.id === selectedTrack)?.name || selectedTrack,
                losses: match.losses_to_analyze,
                current_skills: match.skills
              });
              setLiveCoachingInsights(insightsResponse.data.insights);
            } catch (insightErr) {
              console.error('Error fetching top driver insights:', insightErr);
              setLiveCoachingInsights(null);
            } finally {
              setLoadingInsights(false);
            }
          }
        }
      } else if (response.data.similar_drivers?.length === 0 && response.data.message && response.data.current_avg_finish) {
        // Legacy: Backend returned empty array for elite driver - create self-match manually
        console.log('🏆 Elite driver (legacy response) - creating self-match...');

        try {
          const raceResultsResponse = await api.get(`/api/drivers/${selectedDriverNumber}/results`);
          const raceResults = raceResultsResponse.data;

          const wins = raceResults.filter(r => r.finish_position === 1).length;
          const losses = raceResults
            .filter(r => r.finish_position && r.finish_position > 1)
            .map(r => ({
              track: r.track_name,
              finish: r.finish_position,
              start: r.start_position || 0,
              positions_gained: (r.start_position && r.finish_position)
                ? r.start_position - r.finish_position
                : 0
            }))
            .slice(0, 5);

          const skills = {
            speed: driverData.speed?.percentile || 0,
            consistency: driverData.consistency?.percentile || 0,
            racecraft: driverData.racecraft?.percentile || 0,
            tire_management: driverData.tire_management?.percentile || 0
          };

          const weakestSkill = Object.entries(skills).sort((a, b) => a[1] - b[1])[0];

          const eliteSelfMatch = {
            driver_number: selectedDriverNumber,
            driver_name: driverData.driver_name || `Driver #${selectedDriverNumber}`,
            match_score: 100,
            is_elite_self_match: true,
            skills: {
              speed: skills.speed,
              consistency: skills.consistency,
              racecraft: skills.racecraft,
              tire_management: skills.tire_management
            },
            avg_finish: response.data.current_avg_finish,
            target_avg_finish: 1.0,
            wins,
            total_races: raceResults.length,
            losses_to_analyze: losses,
            target_factor: weakestSkill[0]
          };

          console.log('✅ Created elite self-match:', eliteSelfMatch);
          setBestMatch(eliteSelfMatch);
          setSearching(false);
        } catch (err) {
          console.error('Error creating elite self-match:', err);
          setSearching(false);
        }
      } else {
        // No matches found at all
        setSearching(false);
      }
    } catch (err) {
      console.error('❌ Error finding best match:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        stack: err.stack
      });
      setError('Failed to find comparable driver. Please try again.');
      setSearching(false); // Error occurred, stop searching
    }
  };

  // Get the primary improvement factor key (for fetching coaching data)
  const getPrimaryImprovementFactor = () => {
    if (!targetSkills || !driverData) return null;

    const deltas = {
      speed: targetSkills.speed - (driverData.speed?.percentile || 0),
      consistency: targetSkills.consistency - (driverData.consistency?.percentile || 0),
      racecraft: targetSkills.racecraft - (driverData.racecraft?.percentile || 0),
      tire_management: targetSkills.tire_management - (driverData.tire_management?.percentile || 0)
    };

    const maxDelta = Math.max(...Object.values(deltas));
    return Object.keys(deltas).find(key => deltas[key] === maxDelta);
  };

  // Calculate which skill improved most
  const getPrimaryImprovement = () => {
    if (!targetSkills || !driverData) return null;

    const deltas = {
      speed: targetSkills.speed - (driverData.speed?.percentile || 0),
      consistency: targetSkills.consistency - (driverData.consistency?.percentile || 0),
      racecraft: targetSkills.racecraft - (driverData.racecraft?.percentile || 0),
      tire_management: targetSkills.tire_management - (driverData.tire_management?.percentile || 0)
    };

    const maxDelta = Math.max(...Object.values(deltas));
    const primaryFactor = Object.keys(deltas).find(key => deltas[key] === maxDelta);

    const displayNames = {
      speed: 'Speed',
      consistency: 'Consistency',
      racecraft: 'Racecraft',
      tire_management: 'Tire Management'
    };

    return {
      factor: primaryFactor,
      displayName: displayNames[primaryFactor],
      delta: maxDelta
    };
  };

  if (loading) {
    return (
      <div className="improve-page">
        <DashboardHeader driverData={driverData} pageName="Driver Development" />
        <DashboardTabs />
        <div className="loading-container">
          <div className="loading-text">Loading development data...</div>
        </div>
      </div>
    );
  }

  // Format coaching insights markdown into HTML
  const formatCoachingInsights = (text) => {
    if (!text) return '';

    // Split by lines and process markdown
    return text.split('\n').map((line, index) => {
      // Headers with ## or **
      if (line.trim().startsWith('##')) {
        const headerText = line.trim().replace(/^##\s*/, '');
        return <strong key={index}>{headerText}</strong>;
      }
      else if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
        const headerText = line.trim().replace(/\*\*/g, '');
        return <strong key={index}>{headerText}</strong>;
      }
      // Skip lines that start with # (main title)
      else if (line.trim().startsWith('#')) {
        return null;
      }
      // Regular paragraph
      else if (line.trim()) {
        return <p key={index}>{line.trim()}</p>;
      }
      return null;
    }).filter(Boolean);
  };

  const primaryImprovement = getPrimaryImprovement();

  return (
    <div className="improve-page">
      {/* Unified Header */}
      <DashboardHeader driverData={driverData} pageName="Driver Development" />

      {/* Unified Navigation Tabs */}
      <DashboardTabs />

      {/* Main Content */}
      <div className="improve-content">

        {/* AI RECOMMENDED ALLOCATION */}
        {recommendedAllocation && !targetSkills && (
          <div className="ai-recommendation-banner">
            <div className="recommendation-header">
              <span className="recommendation-icon">AI</span>
              <h3>Recommended Budget Allocation</h3>
            </div>
            <p className="recommendation-reasoning">{recommendedAllocation.reasoning}</p>
            <div className="recommendation-values">
              <span>Speed +{recommendedAllocation.allocation.speed}%</span>
              <span>Consistency +{recommendedAllocation.allocation.consistency}%</span>
              <span>Racecraft +{recommendedAllocation.allocation.racecraft}%</span>
              <span>Tire Mgmt +{recommendedAllocation.allocation.tire_management}%</span>
            </div>
            <div className="recommendation-actions">
              <button className="apply-btn" onClick={handleApplyRecommendation}>
                Apply Recommendation
              </button>
              <button className="skip-btn" onClick={() => setTargetSkills({
                speed: driverData.speed?.percentile || 0,
                consistency: driverData.consistency?.percentile || 0,
                racecraft: driverData.racecraft?.percentile || 0,
                tire_management: driverData.tire_management?.percentile || 0
              })}>
                Allocate Manually
              </button>
            </div>
          </div>
        )}

        {/* TWO COLUMN LAYOUT - Skills & Best Match */}
        <div className="improve-grid">
          {/* LEFT COLUMN - SKILL SLIDERS */}
          {driverData && targetSkills && (
            <section className="skill-sliders-section">
              <SkillSliders
                currentSkills={{
                  speed: driverData.speed?.percentile || 0,
                  consistency: driverData.consistency?.percentile || 0,
                  racecraft: driverData.racecraft?.percentile || 0,
                  tire_management: driverData.tire_management?.percentile || 0
                }}
                initialTargets={targetSkills}
                onTargetChange={handleTargetChange}
                onFindSimilar={handleFindBestMatch}
                tracks={tracks}
                selectedTrack={selectedTrack}
                onTrackChange={setSelectedTrack}
                aiRecommendation={recommendedAllocation}
              />
            </section>
          )}

          {/* RIGHT COLUMN - BEST MATCH RESULTS */}
          <section className="comparables-section">
            {!searching && !bestMatch && targetSkills && (
              <div className="comparables-empty">
                <div className="empty-icon" aria-hidden="true">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#999" strokeWidth="1.5">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <h3>Find Your Best Match</h3>
                <p>Adjust your skill targets and select a track, then click "Find Best Match" to see a comparable driver and track-specific improvement actions.</p>
              </div>
            )}

            {searching && (
              <div className="comparables-loading">
                <div className="loading-spinner"></div>
                <p>Finding best match...</p>
              </div>
            )}

            {bestMatch && driverData && (
              <div className="best-match-results">
                <div className="best-match-header">
                  <h3>Best Match at {tracks.find(t => t.id === selectedTrack)?.name}</h3>
                </div>

                {/* Matching Transparency Section */}
                {matchingData && (
                  <details className="matching-transparency">
                    <summary>How We Found This Match</summary>
                    <div className="transparency-content">
                      <p><strong>{matchingData.method}</strong></p>
                      <p className="algorithm-description">{matchingData.description}</p>

                      <div className="skill-deltas">
                        <h5>Your Skill Improvements:</h5>
                        <div className="deltas-grid">
                          <div className="delta-item">
                            <span>Speed</span>
                            <span className={matchingData.skill_deltas.speed >= 0 ? 'positive' : 'negative'}>
                              {matchingData.skill_deltas.speed >= 0 ? '+' : ''}{matchingData.skill_deltas.speed}
                            </span>
                          </div>
                          <div className="delta-item">
                            <span>Consistency</span>
                            <span className={matchingData.skill_deltas.consistency >= 0 ? 'positive' : 'negative'}>
                              {matchingData.skill_deltas.consistency >= 0 ? '+' : ''}{matchingData.skill_deltas.consistency}
                            </span>
                          </div>
                          <div className="delta-item">
                            <span>Racecraft</span>
                            <span className={matchingData.skill_deltas.racecraft >= 0 ? 'positive' : 'negative'}>
                              {matchingData.skill_deltas.racecraft >= 0 ? '+' : ''}{matchingData.skill_deltas.racecraft}
                            </span>
                          </div>
                          <div className="delta-item">
                            <span>Tire Mgmt</span>
                            <span className={matchingData.skill_deltas.tire_management >= 0 ? 'positive' : 'negative'}>
                              {matchingData.skill_deltas.tire_management >= 0 ? '+' : ''}{matchingData.skill_deltas.tire_management}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="filters-applied">
                        <h5>Filters Applied:</h5>
                        <ul>
                          {matchingData.filters_applied.map((filter, idx) => (
                            <li key={idx}>{filter}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </details>
                )}

                {/* Best Match Card */}
                {bestMatch.is_elite_self_match ? (
                  // No match found - Show analysis for top performer
                  <div className="no-match-analysis">
                    <h3>Performance Analysis</h3>
                    <p className="analysis-intro">No drivers with better performance than your P{driverData.stats?.average_finish?.toFixed(1)} average finish. Here's how to improve further:</p>

                    <div className="current-performance">
                      <div className="stat-item">
                        <span className="stat-label">Current Avg</span>
                        <span className="stat-value">P{driverData.stats?.average_finish?.toFixed(1)}</span>
                      </div>
                      {bestMatch.wins !== undefined && (
                        <div className="stat-item">
                          <span className="stat-label">Wins</span>
                          <span className="stat-value">{bestMatch.wins}</span>
                        </div>
                      )}
                      {bestMatch.total_races !== undefined && (
                        <div className="stat-item">
                          <span className="stat-label">Total Races</span>
                          <span className="stat-value">{bestMatch.total_races}</span>
                        </div>
                      )}
                    </div>

                    {bestMatch.losses_to_analyze && bestMatch.losses_to_analyze.length > 0 && (
                      <div className="races-to-analyze">
                        <h4>Races to Analyze</h4>
                        <p>Focus on these non-winning finishes:</p>
                        <div className="race-list">
                          {bestMatch.losses_to_analyze.map((loss, idx) => (
                            <div key={idx} className="race-item">
                              <span className="track-name">{loss.track}</span>
                              <span className="result">P{loss.start} → P{loss.finish}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  // Regular match found - Show comparison
                  <div className="best-match-card">
                    <div className="match-badge">{bestMatch.match_score}% Match</div>
                    <div className="driver-info">
                      <h4>Driver #{bestMatch.driver_number}</h4>
                      <p>{bestMatch.driver_name}</p>
                    </div>
                    {bestMatch.avg_finish && (
                      <div className="finish-comparison">
                        <div className="your-finish">
                          <span className="label">Your Avg</span>
                          <span className="value">P{driverData.stats?.average_finish?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div className="arrow">→</div>
                        <div className="their-finish">
                          <span className="label">Their Avg</span>
                          <span className="value">P{bestMatch.avg_finish.toFixed(1)}</span>
                        </div>
                      </div>
                    )}
                    <div className="skills-grid">
                      <div className="skill-item">
                        <span className="skill-label">Speed</span>
                        <span className="skill-value">{bestMatch.skills.speed}</span>
                      </div>
                      <div className="skill-item">
                        <span className="skill-label">Consistency</span>
                        <span className="skill-value">{bestMatch.skills.consistency}</span>
                      </div>
                      <div className="skill-item">
                        <span className="skill-label">Racecraft</span>
                        <span className="skill-value">{bestMatch.skills.racecraft}</span>
                      </div>
                      <div className="skill-item">
                        <span className="skill-label">Tire Mgmt</span>
                        <span className="skill-value">{bestMatch.skills.tire_management}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Track-Specific Improvement Actions */}
                {primaryImprovement && primaryImprovement.delta > 0 && (
                  <div className="track-improvement-section">
                    <h4>How to Improve at {tracks.find(t => t.id === selectedTrack)?.name}</h4>
                    <div className="improvement-insights">
                      {loadingInsights ? (
                        <div className="insights-loading">
                          <div className="insights-spinner"></div>
                          <p>Generating personalized coaching insights...</p>
                        </div>
                      ) : liveCoachingInsights ? (
                        <div className="coaching-analysis-box">
                          <div className="coaching-text live-insights">
                            {formatCoachingInsights(liveCoachingInsights)}
                          </div>
                        </div>
                      ) : (
                        <div className="insight-placeholder">
                          <p><strong>Unable to generate coaching insights</strong></p>
                          <p>Try adjusting your skill targets or selecting a different track.</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>

      </div>
    </div>
  );
}
