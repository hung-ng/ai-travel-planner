"""
Context formatting utilities

Formats extracted context into readable strings for AI prompts.
"""
from typing import Dict


class ContextFormatter:
    """Format context data for AI consumption"""

    def format_context(self, context: Dict) -> str:
        """
        Format context dict into readable string

        Args:
            context: Dictionary of extracted context

        Returns:
            Formatted string representation
        """
        parts = []

        if "destination" in context:
            parts.append(f"Destination: {context['destination']}")

        if "duration_days" in context:
            parts.append(f"Duration: {context['duration_days']} days")

        if "budget" in context:
            parts.append(f"Budget: ${context['budget']:,}")

        if "interests" in context:
            parts.append(f"Interests: {', '.join(context['interests'])}")

        if "travel_style" in context:
            parts.append(f"Travel style: {context['travel_style']}")

        return "; ".join(parts)


# Singleton instance
context_formatter = ContextFormatter()
