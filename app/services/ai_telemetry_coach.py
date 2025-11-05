"""
AI Telemetry Coaching Service - Expert race engineer analysis.

Uses Claude to analyze telemetry data and provide specific, actionable coaching
in the style of a professional race engineer.
"""

import os
import pandas as pd
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


RACE_ENGINEER_SYSTEM_PROMPT = """You are an expert motorsports race engineer and driver coach with 20+ years of experience analyzing telemetry data and coaching professional drivers. Your goal is to provide specific, actionable coaching advice that helps drivers improve lap times.

ROLE & EXPERTISE:
- You understand racing physics, vehicle dynamics, and optimal racing techniques
- You can interpret telemetry data (throttle, brake, steering, speed, GPS)
- You identify patterns that indicate technique issues
- You provide coaching in the style of a professional race engineer

COACHING PHILOSOPHY:
- Focus on the 3-5 most impactful improvements (not everything at once)
- Be specific with numbers and measurements from telemetry
- Explain the "why" behind each recommendation (physics/technique)
- Prioritize by potential time gain (biggest opportunities first)
- Be direct but encouraging - drivers respond well to clear guidance

OUTPUT FORMAT:
For each priority area, provide:

**Priority #[N]: [Corner Name] - Losing [X.X]s**

**What the data shows:**
[Specific telemetry observations with numbers - e.g., "You're braking at 250m while the reference brakes at 280m. Your minimum apex speed is 92 km/h vs their 98 km/h."]

**What to do:**
[Specific, actionable coaching - e.g., "Brake 30 meters later using the 280m board as your reference point. Trust the car and carry more speed through the apex - target 97-98 km/h instead of 92 km/h."]

**Why it matters:**
[Brief physics/technique explanation - e.g., "This is a momentum corner where exit speed is critical. Each extra km/h at apex translates to 2+ km/h advantage at corner exit."]

---

CONSTRAINTS:
- Limit output to top 3-5 priority areas maximum
- Always include specific numbers from telemetry
- Use conversational language (not overly technical jargon)
- Focus on driver inputs (what they can control)
- Avoid vague advice like "go faster" - be precise
- Keep each priority section to 3-4 sentences maximum

TONE:
- Direct and clear (like a race engineer on team radio)
- Encouraging but honest about performance gaps
- Confident in recommendations
- Use racing terminology appropriately but explain when needed
"""


class AITelemetryCoach:
    """Service for AI-powered telemetry coaching."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Use Sonnet for deep analysis
        self.model = "claude-sonnet-4-5-20250929"

    def generate_coaching(
        self,
        driver_number: int,
        reference_driver_number: int,
        track_name: str,
        telemetry_insights: Dict,
        corner_analysis: List[Dict]
    ) -> str:
        """
        Generate AI coaching from telemetry analysis.

        Args:
            driver_number: User's driver number
            reference_driver_number: Comparison driver number
            track_name: Track name
            telemetry_insights: Dict with overall telemetry patterns
            corner_analysis: List of corner-by-corner breakdowns

        Returns:
            Coaching text formatted for display
        """

        # Format the data into a coaching prompt
        user_prompt = self._format_coaching_prompt(
            driver_number,
            reference_driver_number,
            track_name,
            telemetry_insights,
            corner_analysis
        )

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=RACE_ENGINEER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        return response.content[0].text

    def _format_coaching_prompt(
        self,
        driver_number: int,
        reference_driver_number: int,
        track_name: str,
        telemetry_insights: Dict,
        corner_analysis: List[Dict]
    ) -> str:
        """Format telemetry data into a Claude-friendly prompt."""

        prompt = f"""Analyze this telemetry data and provide coaching for Driver #{driver_number} at {track_name}.

## OVERALL CONTEXT
- Driver: #{driver_number}
- Reference Driver (faster): #{reference_driver_number}
- Track: {track_name}
- Total Time Delta: {telemetry_insights.get('total_delta', '0.000')}s per lap
- Potential Gain: {telemetry_insights.get('potential_gain', '0.000')}s

## TELEMETRY PATTERNS

**Braking:**
{telemetry_insights.get('braking_pattern', 'Data not available')}

**Throttle Application:**
{telemetry_insights.get('throttle_pattern', 'Data not available')}

**Speed Profile:**
{telemetry_insights.get('speed_pattern', 'Data not available')}

**Steering Smoothness:**
{telemetry_insights.get('steering_pattern', 'Data not available')}

## CORNER-BY-CORNER BREAKDOWN
(Top opportunities for time gain)

"""

        # Add top 5 corners with biggest time loss
        sorted_corners = sorted(corner_analysis, key=lambda x: x.get('time_loss', 0), reverse=True)
        for i, corner in enumerate(sorted_corners[:5], 1):
            prompt += f"""
**Corner {corner.get('corner_number', 'Unknown')} - {corner.get('corner_name', 'Unknown')}**
- Time Loss: {corner.get('time_loss', 0):.3f}s
- Your Apex Speed: {corner.get('driver_apex_speed', 0):.1f} km/h
- Reference Apex Speed: {corner.get('reference_apex_speed', 0):.1f} km/h
- Delta: {corner.get('apex_speed_delta', 0):.1f} km/h
- Primary Issue: {corner.get('focus_area', 'Unknown')}
"""

        prompt += """

## YOUR TASK
Provide 3-5 specific, actionable coaching recommendations using the format specified in your system prompt.
Focus on the biggest time gain opportunities first. Be specific with numbers and clear about what the driver should do differently.
"""

        return prompt


# Global instance
ai_telemetry_coach = AITelemetryCoach()
