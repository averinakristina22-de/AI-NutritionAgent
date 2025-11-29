"""
Data Collection Tool - Structures and validates user profile data

This tool provides:
- save_user_profile_data(): Collects and validates all user information
  Returns completeness percentage and missing fields automatically
"""

from typing import Dict, List, Optional, Literal
from google.adk.tools.tool_context import ToolContext


def save_user_profile_data(
    tool_context: ToolContext,
    age: int,
    gender: Literal["male", "female"],
    height_cm: float,
    weight_kg: float,
    activity_level: Literal[
        "sedentary",
        "lightly_active",
        "moderately_active",
        "very_active",
        "extremely_active"
    ],
    goal: Literal["weight_loss", "maintenance", "muscle_gain", "recomp"],
    dietary_restrictions: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
    favorite_foods: Optional[List[str]] = None,
    foods_to_avoid: Optional[List[str]] = None,
    health_conditions: Optional[List[str]] = None,
    meal_frequency: Optional[int] = None,
    cooking_skill: Optional[str] = None,
    budget_level: Optional[str] = None
) -> Dict:
    """
    Structure and validate user profile data collected during interview.

    This tool helps organize all the information gathered from the user
    into a structured format that can be accessed by downstream agents.
    The data is automatically saved to session.state for other agents.

    Args:
        tool_context: Tool context with access to session state
        age: User's age in years
        gender: Biological sex ("male" or "female")
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        activity_level: Daily activity level
        goal: Primary fitness/health goal
        dietary_restrictions: List of dietary restrictions (e.g., ["vegetarian", "gluten_free"])
        allergies: List of food allergies (e.g., ["tree_nuts", "shellfish"])
        favorite_foods: List of favorite foods or cuisines
        foods_to_avoid: List of foods to avoid for any reason
        health_conditions: List of existing health conditions
        meal_frequency: Preferred number of meals per day
        cooking_skill: Cooking skill level ("beginner", "intermediate", "advanced")
        budget_level: Budget consideration ("low", "medium", "high")

    Returns:
        Dictionary with status and structured user data:
        Success: {
            "status": "success",
            "user_profile": {
                "basic_info": {...},
                "health_goals": {...},
                "dietary_info": {...},
                "lifestyle": {...}
            },
            "completeness": float (0-100),
            "missing_fields": [...]
        }
        Error: {"status": "error", "error_message": str}
    """
    try:
        # Validate required fields
        required_fields = {
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "activity_level": activity_level,
            "goal": goal
        }

        missing_required = [k for k, v in required_fields.items() if v is None]

        if missing_required:
            return {
                "status": "error",
                "error_message": f"Missing required fields: {', '.join(missing_required)}"
            }

        # Basic validation
        if age < 18 or age > 120:
            return {
                "status": "error",
                "error_message": "Age must be between 18 and 120 years"
            }

        if height_cm < 100 or height_cm > 250:
            return {
                "status": "error",
                "error_message": "Height must be between 100 and 250 cm"
            }

        if weight_kg < 30 or weight_kg > 300:
            return {
                "status": "error",
                "error_message": "Weight must be between 30 and 300 kg"
            }

        # Structure the data
        user_profile = {
            "basic_info": {
                "age": age,
                "gender": gender,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "activity_level": activity_level
            },
            "health_goals": {
                "primary_goal": goal,
                "health_conditions": health_conditions or [],
            },
            "dietary_info": {
                "dietary_restrictions": dietary_restrictions or [],
                "allergies": allergies or [],
                "favorite_foods": favorite_foods or [],
                "foods_to_avoid": foods_to_avoid or []
            },
            "lifestyle": {
                "meal_frequency": meal_frequency or 3,
                "cooking_skill": cooking_skill or "intermediate",
                "budget_level": budget_level or "medium"
            }
        }

        # Calculate completeness
        # Empty lists are considered "provided" (user explicitly said they have none)
        # None/null values are considered "missing" (user hasn't answered yet)
        total_fields = 14  # Total number of fields
        filled_fields = 6  # Required fields are always filled at this point

        if dietary_restrictions is not None:
            filled_fields += 1
        if allergies is not None:
            filled_fields += 1
        if favorite_foods is not None:
            filled_fields += 1
        if foods_to_avoid is not None:
            filled_fields += 1
        if health_conditions is not None:
            filled_fields += 1
        if meal_frequency is not None:
            filled_fields += 1
        if cooking_skill is not None:
            filled_fields += 1
        if budget_level is not None:
            filled_fields += 1

        completeness = (filled_fields / total_fields) * 100

        # Identify missing optional fields (only None is missing, empty list is valid)
        missing_fields = []
        if dietary_restrictions is None:
            missing_fields.append("dietary_restrictions")
        if allergies is None:
            missing_fields.append("allergies")
        if favorite_foods is None:
            missing_fields.append("favorite_foods")
        if foods_to_avoid is None:
            missing_fields.append("foods_to_avoid")
        if health_conditions is None:
            missing_fields.append("health_conditions")
        if meal_frequency is None:
            missing_fields.append("meal_frequency")
        if cooking_skill is None:
            missing_fields.append("cooking_skill")
        if budget_level is None:
            missing_fields.append("budget_level")

        # Save to session state for other agents to access
        tool_context.state["user_profile"] = user_profile
        tool_context.state["user_profile_completeness"] = round(completeness, 1)

        return {
            "status": "success",
            "user_profile": user_profile,
            "completeness": round(completeness, 1),
            "missing_fields": missing_fields,
            "summary": f"Profile {completeness:.0f}% complete with {len(missing_fields)} optional fields remaining"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error structuring user data: {str(e)}"
        }
