"""
AI Skill Coaching Service - Factor-specific driver coaching.

Uses Claude to analyze driver performance metrics and generate personalized
coaching recommendations for each skill factor.
"""

import os
from typing import Dict, List
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


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

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=SKILL_COACH_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        return response.content[0].text

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
        track_name: str,
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
            track_name: Selected track for insights
            current_skills: Dict of current driver's skill percentiles
            comparable_skills: Dict of comparable driver's skill percentiles
            comparable_race_results: Race results from comparable driver

        Returns:
            Actionable coaching insights text
        """
        system_prompt = """You are a sports car racing coach for IMSA GTP series providing concise driver development advice.

TASK:
Write brief coaching guidance in 3 sections.

FORMAT:
**Key Focus Areas**
1-2 sentences on what to work on

**Track-Specific Techniques**
1-2 sentences with specific techniques for this track

**Development Path**
1-2 sentences on how to practice this

CONSTRAINTS:
- Keep it SHORT - maximum 1-2 sentences per section
- Sports car racing (GTP), NOT Formula 1
- Use simple, direct language
- Second person ("focus on...")
- Reference specific turns/sections when possible
- Be encouraging but concise
"""

        factor_display = factor_name.replace("_", " ").title()

        user_prompt = f"""IMPROVEMENT TARGET:
Driver #{current_driver_number} wants to improve their {factor_display} by +{improvement_delta:.0f}%

CURRENT DRIVER SKILLS:
- Speed: {current_skills.get('speed', 0):.1f}th percentile
- Consistency: {current_skills.get('consistency', 0):.1f}th percentile
- Racecraft: {current_skills.get('racecraft', 0):.1f}th percentile
- Tire Management: {current_skills.get('tire_management', 0):.1f}th percentile

COMPARABLE DRIVER #{comparable_driver_number} SKILLS:
- Speed: {comparable_skills.get('speed', 0):.1f}th percentile
- Consistency: {comparable_skills.get('consistency', 0):.1f}th percentile
- Racecraft: {comparable_skills.get('racecraft', 0):.1f}th percentile
- Tire Management: {comparable_skills.get('tire_management', 0):.1f}th percentile

TRACK: {track_name}

"""
        if comparable_race_results:
            user_prompt += "COMPARABLE DRIVER'S TRACK PERFORMANCE:\n"
            for race in comparable_race_results[:6]:
                if track_name.lower() in race.get('track_name', '').lower():
                    user_prompt += (
                        f"- {race.get('track_name')}: "
                        f"P{race.get('start_position')} → P{race.get('finish_position')}, "
                        f"Fastest lap gap: {race.get('gap_to_fastest_lap', 'N/A')}\n"
                    )

        user_prompt += f"""
Write 3-section coaching guidance for Driver #{current_driver_number} to achieve their +{improvement_delta:.0f}% {factor_display} improvement by learning from Driver #{comparable_driver_number}'s approach at {track_name}.

Remember: This is sports car racing (IMSA GTP/Gazoo Racing), not Formula 1. Focus on sports car-specific techniques."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        return response.content[0].text

    def generate_top_driver_insights(
        self,
        driver_name: str,
        driver_number: int,
        target_factor: str,
        track_name: str,
        losses: List[Dict],
        current_skills: Dict
    ) -> str:
        """
        Generate AI coaching for top drivers who have no better comparables.

        Focuses on analyzing non-winning races to identify improvement opportunities.
        """
        system_prompt = """You are an elite motorsports performance coach analyzing a top-tier driver's races.

TASK:
Write concise coaching advice in 3 sections focused on converting P2-P3 finishes into wins.

FORMAT:
**Critical Pattern**
1-2 sentences identifying what's preventing wins

**Track-Specific Focus**
1-2 sentences on this specific track's challenges

**Path to P1**
1-2 sentences on concrete steps to secure more wins

CONSTRAINTS:
- Keep it SHORT - maximum 1-2 sentences per section
- This is IMSA GTP/sports car racing, not Formula 1
- Focus on the margin between P2/P3 and P1
- Be specific and actionable
- Second person ("you need to...")
"""

        factor_display = target_factor.replace("_", " ").title()

        user_prompt = f"""TOP DRIVER ANALYSIS: {driver_name}

This driver is already elite-level but needs to convert more podiums into wins.

CURRENT SKILLS:
- Speed: {current_skills.get('speed', 0):.1f}th percentile
- Consistency: {current_skills.get('consistency', 0):.1f}th percentile
- Racecraft: {current_skills.get('racecraft', 0):.1f}th percentile
- Tire Management: {current_skills.get('tire_management', 0):.1f}th percentile

IMPROVEMENT FOCUS: {factor_display}
TRACK: {track_name}

NON-WINNING FINISHES TO ANALYZE:
"""

        for loss in losses[:3]:  # Top 3 losses
            user_prompt += f"- {loss.get('track')}: Started P{loss.get('start')} → Finished P{loss.get('finish')}"
            positions = loss.get('positions_gained', 0)
            if positions != 0:
                user_prompt += f" ({'+' if positions > 0 else ''}{positions} positions)"
            user_prompt += "\n"

        user_prompt += f"""
Write 3-section coaching for {driver_name} to identify what's preventing wins and how to improve {factor_display} at {track_name}.

Remember: This is sports car racing (IMSA GTP). Focus on the final details that separate P2 from P1."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        return response.content[0].text


ai_skill_coach = AISkillCoach()
