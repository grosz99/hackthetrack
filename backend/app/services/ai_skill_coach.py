"""
AI Skill Coaching Service - Factor-specific driver coaching.

Uses Claude to analyze driver performance metrics and generate personalized
coaching recommendations for each skill factor.
"""

import os
import logging
from typing import Dict, List
from anthropic import Anthropic
import anthropic
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


SKILL_COACH_SYSTEM_PROMPT = """You are an elite motorsports talent scout writing concise scouting reports.

TASK:
Write a 5-6 sentence scouting assessment that includes:
1. Overall evaluation of their performance in this skill area (mention rank and percentile)
2. Their strongest and weakest underlying metrics
3. Specific track evidence from their season results showing where these patterns appeared
4. One key development opportunity

CONSTRAINTS:
- EXACTLY 5-6 sentences total, no more
- Reference specific percentiles and rankings from the data
- Mention actual track names from their race results when discussing evidence
- Write in third person using the driver's name provided (not "Driver #X")
- Be direct and analytical
- NO headers, NO bullet points, NO formatting - just flowing sentences
"""


class AISkillCoach:
    """Service for AI-powered skill factor coaching."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5-20250929"

    def generate_factor_coaching(
        self,
        driver_number: int,
        factor_name: str,
        variables: List[Dict],
        overall_percentile: float,
        rank_among_drivers: int,
        total_drivers: int,
        race_results: List[Dict] = None,
        driver_name: str = None
    ) -> str:
        """
        Generate personalized coaching for a specific skill factor.

        Args:
            driver_number: Driver number
            factor_name: Name of the factor (speed, consistency, etc.)
            variables: List of variable dicts with name, percentile, description
            overall_percentile: Driver's overall percentile for this factor
            rank_among_drivers: Driver's rank for this factor
            total_drivers: Total number of drivers
            race_results: List of race result dicts with track-specific data
            driver_name: Driver's name (optional, defaults to "Driver #XX")

        Returns:
            Coaching text formatted for display
        """
        user_prompt = self._format_coaching_prompt(
            driver_number,
            factor_name,
            variables,
            overall_percentile,
            rank_among_drivers,
            total_drivers,
            race_results or [],
            driver_name
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=SKILL_COACH_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except anthropic.APIError as e:
            logger.exception(f"Anthropic API error in skill coaching: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI skill coaching service temporarily unavailable. Please try again in a moment."
            )
        except Exception as e:
            logger.exception(f"Unexpected error in skill coaching: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to generate skill coaching. Please try again."
            )

    def _format_coaching_prompt(
        self,
        driver_number: int,
        factor_name: str,
        variables: List[Dict],
        overall_percentile: float,
        rank_among_drivers: int,
        total_drivers: int,
        race_results: List[Dict],
        driver_name: str = None
    ) -> str:
        """Format the data into a coaching prompt for Claude."""
        factor_display = factor_name.replace("_", " ").title()
        display_name = driver_name or f"Driver #{driver_number}"

        prompt = f"""{display_name} - {factor_display} Assessment

OVERALL: Ranked {rank_among_drivers} of {total_drivers} drivers ({overall_percentile:.1f}th percentile)

METRICS:
"""
        sorted_vars = sorted(variables, key=lambda x: x["percentile"])

        for var in sorted_vars:
            prompt += f"- {var['display_name']}: {var['percentile']:.1f}th percentile\n"

        weakest_var = sorted_vars[0]
        strongest_var = sorted_vars[-1]

        prompt += f"""
STRONGEST: {strongest_var["display_name"]} ({strongest_var["percentile"]:.1f}th)
WEAKEST: {weakest_var["display_name"]} ({weakest_var["percentile"]:.1f}th)

SEASON RACE RESULTS:
"""
        for race in race_results[:8]:
            prompt += (
                f"- {race.get('track_name', 'Unknown')}: "
                f"Started P{race.get('start_position', '?')}, "
                f"Finished P{race.get('finish_position', '?')}, "
                f"Gained {race.get('positions_gained', 0)} pos, "
                f"Gap to fastest lap: {race.get('gap_to_fastest_lap', 'N/A')}\n"
            )

        prompt += f"""
Write a 5-6 sentence scouting assessment for {display_name}'s {factor_display}."""

        return prompt

    def generate_comparative_coaching(
        self,
        current_driver_number: int,
        comparable_driver_number: int,
        factor_name: str,
        improvement_delta: float,
        current_skills: Dict,
        comparable_skills: Dict,
        comparable_race_results: List[Dict] = None
    ) -> str:
        """
        Generate coaching insights comparing current driver to comparable driver.

        Args:
            current_driver_number: Current driver's number
            comparable_driver_number: Comparable driver's number
            factor_name: Skill factor being improved (speed, consistency, etc.)
            improvement_delta: How much the user wants to improve (e.g., 2%)
            current_skills: Dict of current driver's skill percentiles
            comparable_skills: Dict of comparable driver's skill percentiles
            comparable_race_results: Race results from comparable driver

        Returns:
            Actionable coaching insights text
        """
        system_prompt = """You are a performance coach for the Toyota Gazoo Racing Cup series. Your drivers are 18-25 year olds - speak to them in a relatable, conversational way while being data-driven.

You use the 4-factor performance model (Speed, Consistency, Racecraft, Tire Management) combined with race history to guide drivers.

TASK:
Write coaching guidance in 3 sections showing how to learn from a comparable driver.

FORMAT:
KEY FOCUS AREAS
2-3 sentences in conversational language on what to work on. Reference the data but explain it in simple terms.

BEST TRACK OPPORTUNITIES
List 2-3 tracks where Driver #{comparable_driver_number} used this skill to their advantage. For each track, use this exact format:
- Track Name: Brief explanation of why this track matters and what you can learn here (1 sentence max)

DEVELOPMENT PATH
2-3 sentences on concrete, relatable steps to improve using everyday language

CONSTRAINTS:
- Write like you're talking to a 20-year-old racer, not an engineer
- Use "you" and conversational language
- Cite specific race data but explain it simply
- This is IMSA GTP sports car racing
- Keep formatting clean and easy to scan
- No overly technical jargon
- DO NOT use asterisks or markdown formatting
- Use ALL CAPS for section headers only
- Use simple hyphens for bullet points, not em-dashes or special characters
"""

        factor_display = factor_name.replace("_", " ").title()

        user_prompt = f"""IMPROVEMENT TARGET:
Driver #{current_driver_number} wants to improve their {factor_display} by +{improvement_delta:.0f}%

CURRENT DRIVER 4-FACTOR PROFILE:
- Speed: {current_skills.get('speed', 0):.1f}th percentile
- Consistency: {current_skills.get('consistency', 0):.1f}th percentile
- Racecraft: {current_skills.get('racecraft', 0):.1f}th percentile
- Tire Management: {current_skills.get('tire_management', 0):.1f}th percentile

COMPARABLE DRIVER #{comparable_driver_number} 4-FACTOR PROFILE:
- Speed: {comparable_skills.get('speed', 0):.1f}th percentile (+{comparable_skills.get('speed', 0) - current_skills.get('speed', 0):.1f} advantage)
- Consistency: {comparable_skills.get('consistency', 0):.1f}th percentile (+{comparable_skills.get('consistency', 0) - current_skills.get('consistency', 0):.1f} advantage)
- Racecraft: {comparable_skills.get('racecraft', 0):.1f}th percentile (+{comparable_skills.get('racecraft', 0) - current_skills.get('racecraft', 0):.1f} advantage)
- Tire Management: {comparable_skills.get('tire_management', 0):.1f}th percentile (+{comparable_skills.get('tire_management', 0) - current_skills.get('tire_management', 0):.1f} advantage)

"""
        if comparable_race_results:
            user_prompt += f"DRIVER #{comparable_driver_number}'S SEASON RESULTS (showing where {factor_display} strength delivered results):\n"
            for race in comparable_race_results[:12]:
                user_prompt += (
                    f"- {race.get('track_name')}: "
                    f"P{race.get('start_position')} → P{race.get('finish_position')}"
                )
                if race.get('positions_gained'):
                    user_prompt += f" ({'+' if race.get('positions_gained') > 0 else ''}{race.get('positions_gained')} positions)"
                user_prompt += "\n"

        user_prompt += f"""
Using the 4-factor model and race data, write coaching for Driver #{current_driver_number} to achieve +{improvement_delta:.0f}% {factor_display} improvement.

Focus on: Which tracks Driver #{comparable_driver_number} performed best at using {factor_display} as a strength, and why those tracks will show the most benefit for this improvement.

Remember: Toyota Gazoo Racing Cup / IMSA GTP sports car racing. Use data and track analysis."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except anthropic.APIError as e:
            logger.exception(f"Anthropic API error in improvement coaching: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI improvement coaching service temporarily unavailable. Please try again in a moment."
            )
        except Exception as e:
            logger.exception(f"Unexpected error in improvement coaching: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to generate improvement coaching. Please try again."
            )

    def generate_top_driver_insights(
        self,
        driver_name: str,
        driver_number: int,
        target_factor: str,
        losses: List[Dict],
        current_skills: Dict
    ) -> str:
        """
        Generate AI coaching for top drivers who have no better comparables.

        Focuses on analyzing non-winning races to identify improvement opportunities.
        """
        system_prompt = """You are a performance coach for the Toyota Gazoo Racing Cup series. Your drivers are 18-25 year olds - speak to them in a relatable, conversational way while being data-driven.

You use the 4-factor performance model (Speed, Consistency, Racecraft, Tire Management) combined with race history to guide drivers.

TASK:
Write coaching advice in 3 sections for an elite driver who wants to turn podiums into wins.

FORMAT:
CRITICAL PATTERN ACROSS TRACKS
2-3 sentences in conversational language identifying what's preventing wins. Reference specific race data but explain it in simple terms.

TRACK-BY-TRACK ANALYSIS
List 2-3 tracks where this improvement will make the biggest difference. For each track, use this exact format:
- Track Name: Brief explanation of why this track matters for this skill (1 sentence max)

DEVELOPMENT PATH
2-3 sentences on concrete, relatable steps to improve using everyday language

CONSTRAINTS:
- Write like you're talking to a 20-year-old racer, not an engineer
- Use "you" and conversational language
- Cite specific races but explain them simply
- This is IMSA GTP sports car racing
- Keep formatting clean and easy to scan
- No overly technical jargon
- DO NOT use asterisks or markdown formatting
- Use ALL CAPS for section headers only
- Use simple hyphens for bullet points, not em-dashes or special characters
"""

        factor_display = target_factor.replace("_", " ").title()

        user_prompt = f"""TOP DRIVER ANALYSIS: {driver_name}

This driver is already elite-level but needs to convert more podiums into wins.

4-FACTOR PERFORMANCE PROFILE:
- Speed: {current_skills.get('speed', 0):.1f}th percentile
- Consistency: {current_skills.get('consistency', 0):.1f}th percentile
- Racecraft: {current_skills.get('racecraft', 0):.1f}th percentile
- Tire Management: {current_skills.get('tire_management', 0):.1f}th percentile

PRIMARY IMPROVEMENT TARGET: {factor_display}

NON-WINNING FINISHES TO ANALYZE:
"""

        for loss in losses[:5]:  # Analyze more losses for pattern detection
            user_prompt += f"- {loss.get('track')}: Started P{loss.get('start')} → Finished P{loss.get('finish')}"
            positions = loss.get('positions_gained', 0)
            if positions != 0:
                user_prompt += f" ({'+' if positions > 0 else ''}{positions} positions)"
            user_prompt += "\n"

        user_prompt += f"""
Using the 4-factor model and race data, write coaching for {driver_name} to identify patterns preventing wins and prioritize which tracks to focus on for {factor_display} improvement.

Focus on: Which of these non-winning races show the clearest opportunity for improvement in {factor_display}, and why those tracks are priority targets.

Remember: Toyota Gazoo Racing Cup / IMSA GTP sports car racing. Use data to identify patterns."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except anthropic.APIError as e:
            logger.exception(f"Anthropic API error in top driver insights: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI top driver insights service temporarily unavailable. Please try again in a moment."
            )
        except Exception as e:
            logger.exception(f"Unexpected error in top driver insights: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to generate top driver insights. Please try again."
            )


ai_skill_coach = AISkillCoach()
