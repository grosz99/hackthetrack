import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { sendChatMessage, getDriver, getTrack, getDetailedTelemetry } from '../../services/api';
import SpeedTraceChart from '../../components/charts/SpeedTraceChart';
import './StrategyChat.css';

function StrategyChat() {
  const location = useLocation();
  const navigate = useNavigate();

  const [driverNumber, setDriverNumber] = useState(location.state?.driverNumber || null);
  const [trackId, setTrackId] = useState(location.state?.trackId || null);
  const [driver, setDriver] = useState(null);
  const [track, setTrack] = useState(null);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);

  const [telemetryData, setTelemetryData] = useState(null);
  const [telemetryLoading, setTelemetryLoading] = useState(false);
  const [showTelemetry, setShowTelemetry] = useState(false);
  const [highlightedCorners, setHighlightedCorners] = useState([]);

  const messagesEndRef = useRef(null);

  // Parse AI response for corner mentions
  const parseCornerMentions = (text) => {
    const cornerPatterns = [
      /turn\s+(\d+)/gi,
      /corner\s+(\d+)/gi,
      /T(\d+)/g,
      /sector\s+(\d+)/gi
    ];

    const corners = new Set();
    cornerPatterns.forEach(pattern => {
      const matches = text.matchAll(pattern);
      for (const match of matches) {
        corners.add(parseInt(match[1]));
      }
    });

    return Array.from(corners);
  };

  // Load driver and track data
  useEffect(() => {
    const loadData = async () => {
      if (driverNumber && trackId) {
        try {
          const [driverData, trackData] = await Promise.all([
            getDriver(driverNumber),
            getTrack(trackId)
          ]);
          setDriver(driverData);
          setTrack(trackData);

          // Add welcome message
          setMessages([{
            role: 'assistant',
            content: `Welcome! I'm your AI racing strategist. I've analyzed Driver #${driverNumber}'s performance profile for ${trackData.name}. How can I help you prepare for this race?`
          }]);

          setSuggestedQuestions([
            `What should I focus on to improve at ${trackData.name}?`,
            "How does my skill profile match this track?",
            "Which driver should I compare myself against in telemetry?"
          ]);

        } catch (error) {
          console.error('Error loading data:', error);
        }
      }
    };

    loadData();
  }, [driverNumber, trackId]);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (messageText = null) => {
    const textToSend = messageText || input.trim();

    if (!textToSend || loading || !driverNumber || !trackId) return;

    setInput('');
    setLoading(true);

    // Add user message
    const newMessages = [
      ...messages,
      { role: 'user', content: textToSend }
    ];
    setMessages(newMessages);

    try {
      // Send to API
      const response = await sendChatMessage(
        textToSend,
        driverNumber,
        trackId,
        messages
      );

      // Add AI response
      setMessages([
        ...newMessages,
        { role: 'assistant', content: response.message }
      ]);

      // Parse corner mentions from AI response
      const mentionedCorners = parseCornerMentions(response.message);
      if (mentionedCorners.length > 0) {
        setHighlightedCorners(mentionedCorners);
      }

      // Update suggested questions
      if (response.suggested_questions?.length > 0) {
        setSuggestedQuestions(response.suggested_questions);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please make sure the backend API is running.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestedQuestion = (question) => {
    handleSend(question);
  };

  const goToTelemetry = () => {
    navigate('/telemetry', {
      state: {
        driverNumber,
        trackId,
        trackName: track?.name
      }
    });
  };

  const loadTelemetryData = async () => {
    if (!driverNumber || !trackId) return;

    setTelemetryLoading(true);
    try {
      // Default to race 1 for now
      const data = await getDetailedTelemetry(trackId, 1, driverNumber);
      setTelemetryData(data);
      setShowTelemetry(true);
    } catch (error) {
      console.error('Error loading telemetry:', error);
    } finally {
      setTelemetryLoading(false);
    }
  };

  // If no driver/track selected, show selection UI
  if (!driverNumber || !trackId) {
    return (
      <div className="strategy-container">
        <div className="empty-state">
          <h2>No Driver or Track Selected</h2>
          <p>Please select a driver and track from the Track Intelligence page first.</p>
          <button
            className="primary-button"
            onClick={() => navigate('/track-intelligence')}
          >
            Go to Track Intelligence
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="strategy-container">
      {/* Header with context */}
      <div className="strategy-header">
        <div className="context-info">
          <h2>AI Strategy Coach</h2>
          {driver && track && (
            <div className="context-details">
              <div className="context-item">
                <span className="label">Driver:</span>
                <span className="value">#{driver.driver_number}</span>
              </div>
              <div className="context-item">
                <span className="label">Track:</span>
                <span className="value">{track.name}</span>
              </div>
              <div className="context-item">
                <span className="label">Overall Score:</span>
                <span className="value">{driver.overall_score.toFixed(0)}/100</span>
              </div>
            </div>
          )}
        </div>

        <div className="header-actions">
          <button className="secondary-button" onClick={() => navigate('/track-intelligence')}>
            Change Selection
          </button>
          <button className="primary-button" onClick={goToTelemetry}>
            View Telemetry →
          </button>
        </div>
      </div>

      {/* Skill breakdown */}
      {driver && (
        <div className="skills-summary">
          <div className="skill-card">
            <div className="skill-name">Speed</div>
            <div className="skill-score">{driver.speed.score.toFixed(0)}</div>
            <div className="skill-percentile">{driver.speed.percentile.toFixed(0)}th percentile</div>
          </div>
          <div className="skill-card">
            <div className="skill-name">Consistency</div>
            <div className="skill-score">{driver.consistency.score.toFixed(0)}</div>
            <div className="skill-percentile">{driver.consistency.percentile.toFixed(0)}th percentile</div>
          </div>
          <div className="skill-card">
            <div className="skill-name">Racecraft</div>
            <div className="skill-score">{driver.racecraft.score.toFixed(0)}</div>
            <div className="skill-percentile">{driver.racecraft.percentile.toFixed(0)}th percentile</div>
          </div>
          <div className="skill-card">
            <div className="skill-name">Tire Mgmt</div>
            <div className="skill-score">{driver.tire_management.score.toFixed(0)}</div>
            <div className="skill-percentile">{driver.tire_management.percentile.toFixed(0)}th percentile</div>
          </div>
        </div>
      )}

      {/* Chat messages */}
      <div className="chat-container">
        <div className="messages-area">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message assistant loading">
              <div className="message-content">
                <span className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested questions */}
        {suggestedQuestions.length > 0 && (
          <div className="suggested-questions">
            <div className="suggested-label">Suggested questions:</div>
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                className="suggested-question"
                onClick={() => handleSuggestedQuestion(question)}
                disabled={loading}
              >
                {question}
              </button>
            ))}
          </div>
        )}

        {/* Telemetry visualization button */}
        {messages.length > 1 && (
          <div className="telemetry-actions">
            <button
              className="telemetry-button"
              onClick={loadTelemetryData}
              disabled={telemetryLoading}
            >
              {telemetryLoading ? 'Loading...' : showTelemetry ? 'Refresh Speed Trace' : '📊 View Speed Trace Comparison'}
            </button>
          </div>
        )}

        {/* Input area */}
        <div className="input-area">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about race strategy, track approach, or driver comparison..."
            rows="2"
            disabled={loading}
          />
          <button
            className="send-button"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>

      {/* Two-column layout when telemetry is shown */}
      {showTelemetry && telemetryData && (
        <div className="telemetry-side-panel">
          <SpeedTraceChart
            telemetryData={telemetryData}
            comparisonDrivers={telemetryData.comparison_drivers}
            highlightedCorners={highlightedCorners}
          />
        </div>
      )}
    </div>
  );
}

export default StrategyChat;
