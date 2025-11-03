"""
AI Strategy Chatbot Service using Anthropic Claude.
"""

import os
from typing import List, Optional
from anthropic import Anthropic
from models import ChatMessage, Driver, Track
from dotenv import load_dotenv

# Load environment variables before initializing the client
load_dotenv()


class AIStrategyService:
    """Service for AI-powered racing strategy insights."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Using Haiku 4.5 for optimal speed & cost in conversational AI coaching
        # 4-5x faster than Sonnet, 1/3 the cost, with near-frontier performance
        self.model = "claude-haiku-4-5-20251001"

    def _build_system_prompt(self, driver: Driver, track: Track) -> str:
        """Build context-rich system prompt with driver and track data."""

        return f"""You are an expert racing strategist and performance coach for grassroots motorsports.
You specialize in the Toyota GR86 spec series and use data-driven insights to help drivers improve.

## THE 4-FACTOR MODEL

You have access to a validated predictive model (R² = 0.895) that explains race performance using 4 skill dimensions:

1. **RAW SPEED (50% importance)** - β = 6.079
   - Qualifying pace relative to pole
   - Best lap in race vs field best
   - Average of 10 fastest laps
   - THIS IS THE DOMINANT PREDICTOR

2. **CONSISTENCY (31% importance)** - β = 3.792
   - Braking consistency (lap-to-lap variation)
   - Sector consistency across S1/S2/S3
   - Stint consistency (lap time coefficient of variation)
   - Measures "steady hand" driving

3. **RACECRAFT (16% importance)** - β = 1.943
   - Positions gained (qual position vs finish)
   - Position changes during race
   - Measures overtaking and passing ability

4. **TIRE MANAGEMENT (10% importance)** - β = 1.237
   - Early vs late pace ratio
   - Late stint performance (final 33% of race)
   - Measures ability to preserve tires

## CURRENT CONTEXT

**Track: {track.name}**
- Location: {track.location}
- Length: {track.length_miles} miles
- Track Demand Profile:
  * Speed: {track.demand_profile.speed:.1f}/100
  * Consistency: {track.demand_profile.consistency:.1f}/100
  * Racecraft: {track.demand_profile.racecraft:.1f}/100
  * Tire Management: {track.demand_profile.tire_management:.1f}/100

**Driver #{driver.driver_number}**
- Overall Score: {driver.overall_score:.1f}/100
- Skill Breakdown:
  * Speed: {driver.speed.score:.1f}/100 (Percentile: {driver.speed.percentile:.0f}th, z-score: {driver.speed.z_score:.2f})
  * Consistency: {driver.consistency.score:.1f}/100 (Percentile: {driver.consistency.percentile:.0f}th, z-score: {driver.consistency.z_score:.2f})
  * Racecraft: {driver.racecraft.score:.1f}/100 (Percentile: {driver.racecraft.percentile:.0f}th, z-score: {driver.racecraft.z_score:.2f})
  * Tire Management: {driver.tire_management.score:.1f}/100 (Percentile: {driver.tire_management.percentile:.0f}th, z-score: {driver.tire_management.z_score:.2f})

- Race Statistics:
  * Races Completed: {driver.stats.races_completed}
  * Average Finish: P{driver.stats.average_finish:.1f}
  * Best Finish: P{driver.stats.best_finish}
  * Worst Finish: P{driver.stats.worst_finish}

- Circuit Fit Score: {driver.circuit_fits.get(track.id, 0):.1f}/100

## YOUR ROLE

Provide actionable, data-driven racing strategy and insights based on:
1. The driver's specific skill profile (strengths and weaknesses)
2. The track's demand profile (what skills matter most here)
3. The circuit fit score (how well driver matches track)
4. The 4-factor model predictions
5. High-frequency telemetry data for detailed analysis

**THREE-TIER TELEMETRY SYSTEM:**
When discussing specific driving technique improvements, you can reference telemetry comparisons.
The system automatically provides three reference points:
- **You** (baseline): Current performance
- **Next Tier** (achievable target): Driver 1-2 positions ahead in race results
- **Leader** (ultimate goal): Race winner or top performer

Example usage in your responses:
"Your braking into Turn 5 is 15m earlier than the next tier driver and 25m earlier than the leader.
The telemetry shows you could carry 3-4mph more mid-corner speed by braking later."

**Guidelines:**
- Be specific and actionable (e.g., "Focus on brake consistency in Turn 3-5")
- Reference the data (e.g., "Your consistency is 66th percentile, but this track demands high consistency")
- When discussing technique, mention specific corners and reference telemetry insights
- Explain the progression: You → Next Tier → Leader (shows achievable steps)
- Suggest specific telemetry comparisons (e.g., "Let's look at your brake traces vs the next tier driver in the hairpin")
- Keep responses concise but insightful (2-3 paragraphs max)
- Use a supportive, coaching tone

**Theme: "Making the Predictable Unpredictable"**
Help drivers understand how their unique skill profile can overcome predictions and find competitive advantages through data-driven insights.
"""

    def get_strategy_insights(
        self,
        message: str,
        driver: Driver,
        track: Track,
        history: List[ChatMessage],
    ) -> tuple[str, List[str]]:
        """
        Get AI strategy insights for driver at track.

        Args:
            message: User's question/message
            driver: Driver profile
            track: Track information
            history: Previous conversation history

        Returns:
            Tuple of (response_message, suggested_questions)
        """

        system_prompt = self._build_system_prompt(driver, track)

        # Build message history
        messages = []
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )

        response_text = response.content[0].text

        # Generate suggested follow-up questions
        suggested_questions = self._generate_suggested_questions(
            driver, track, len(history)
        )

        return response_text, suggested_questions

    def _generate_suggested_questions(
        self, driver: Driver, track: Track, conversation_length: int
    ) -> List[str]:
        """Generate contextual suggested questions based on driver/track."""

        if conversation_length == 0:
            # Initial suggestions
            return [
                f"What should I focus on to improve at {track.name}?",
                "How does my skill profile match this track?",
                "Which driver should I compare myself against?",
            ]
        elif conversation_length < 3:
            # Mid-conversation suggestions
            weak_factor = self._identify_weakest_factor(driver)
            return [
                f"How can I improve my {weak_factor}?",
                "What's my best strategy for qualifying?",
                "How should I approach tire strategy?",
            ]
        else:
            # Later conversation suggestions
            return [
                "Can you summarize my race plan?",
                "What data should I look for in telemetry comparison?",
                "What's one thing I should focus on this weekend?",
            ]

    def _identify_weakest_factor(self, driver: Driver) -> str:
        """Identify driver's weakest factor."""
        factors = {
            "speed": driver.speed.score,
            "consistency": driver.consistency.score,
            "racecraft": driver.racecraft.score,
            "tire management": driver.tire_management.score,
        }

        return min(factors, key=factors.get)


# Global instance
ai_service = AIStrategyService()
