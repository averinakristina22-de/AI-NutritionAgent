"""
Session Data Tool - Unified retrieval of all session data

This tool consolidates multiple retrieval operations into one simple interface.
Instead of having separate tools for retrieving profile, KBJU, and meal plan,
the agent can get everything it needs with a single tool call.
"""

from typing import Optional
from google.adk.tools.tool_context import ToolContext


def get_session_data(
    tool_context: ToolContext,
    data_type: Optional[str] = None
) -> dict:
    """
    Retrieve data from the current session (profile, KBJU targets, or meal plan).

    This unified tool replaces separate retrieve_user_profile(),
    retrieve_kbju_calculation(), and retrieve_meal_plan() tools.

    Args:
        tool_context: Tool context with access to session state
        data_type: Optional filter - "profile", "kbju", "meal_plan", or None for all
                   If None, returns all available session data

    Returns:
        Dictionary with requested session data:
        Success: {
            "status": "success",
            "data": {
                "user_profile": {...} or None,
                "kbju_calculation": {...} or None,
                "meal_plan": {...} or None
            },
            "available": ["profile", "kbju", "meal_plan"],  # List of what exists
            "message": str
        }
        Error: {"status": "error", "error_message": str}

    Examples:
        # Get everything
        result = get_session_data()

        # Get just user profile
        result = get_session_data(data_type="profile")

        # Get KBJU targets
        result = get_session_data(data_type="kbju")

        # Get meal plan
        result = get_session_data(data_type="meal_plan")
    """
    try:
        # Check what data is available
        user_profile = tool_context.state.get("user_profile")
        kbju_calculation = tool_context.state.get("kbju_calculation")
        meal_plan = tool_context.state.get("meal_plan")

        available = []
        if user_profile:
            available.append("profile")
        if kbju_calculation:
            available.append("kbju")
        if meal_plan:
            available.append("meal_plan")

        # If specific data type requested
        if data_type:
            data_type = data_type.lower()

            if data_type == "profile":
                if not user_profile:
                    return {
                        "status": "error",
                        "error_message": "No user profile found in session. Complete the interview first."
                    }
                return {
                    "status": "success",
                    "data": {"user_profile": user_profile},
                    "available": available,
                    "message": "Retrieved user profile"
                }

            elif data_type == "kbju":
                if not kbju_calculation:
                    return {
                        "status": "error",
                        "error_message": "No KBJU calculation found. Calculate nutritional targets first."
                    }
                return {
                    "status": "success",
                    "data": {"kbju_calculation": kbju_calculation},
                    "available": available,
                    "message": "Retrieved KBJU targets"
                }

            elif data_type == "meal_plan":
                if not meal_plan:
                    return {
                        "status": "error",
                        "error_message": "No meal plan found. Generate a meal plan first."
                    }
                return {
                    "status": "success",
                    "data": {"meal_plan": meal_plan},
                    "available": available,
                    "message": "Retrieved meal plan"
                }

            else:
                return {
                    "status": "error",
                    "error_message": f"Invalid data_type '{data_type}'. Use 'profile', 'kbju', or 'meal_plan'."
                }

        # Return all available data
        if not available:
            return {
                "status": "error",
                "error_message": "No session data available. Start by completing the interview."
            }

        result_data = {}
        if user_profile:
            result_data["user_profile"] = user_profile
        if kbju_calculation:
            result_data["kbju_calculation"] = kbju_calculation
        if meal_plan:
            result_data["meal_plan"] = meal_plan

        return {
            "status": "success",
            "data": result_data,
            "available": available,
            "message": f"Retrieved all session data: {', '.join(available)}"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error retrieving session data: {str(e)}"
        }
