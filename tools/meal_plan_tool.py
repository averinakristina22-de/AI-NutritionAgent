"""
Meal Plan Storage Tool - Saves and retrieves meal plans in session state

This tool provides functions to:
- Save generated meal plans to session for later access
- Retrieve meal plan details
- Get nutritional breakdown per meal
"""

from typing import Optional, Any
from google.adk.tools.tool_context import ToolContext


def save_meal_plan(
    tool_context: ToolContext,
    meal_plan: dict
) -> dict:
    """
    Save a generated meal plan to the session state for later retrieval.

    This allows the agent to remember the meal plan and answer detailed
    questions about individual meals, recipes, and nutritional content.

    Args:
        tool_context: Tool context with access to session state
        meal_plan: Complete meal plan dictionary from generate_meal_plan_recipes()
                   Should include: duration_days, daily_targets, days (with meals)

    Returns:
        Dictionary with status:
        Success: {
            "status": "success",
            "message": "Meal plan saved",
            "summary": str (brief summary of the plan)
        }
        Error: {"status": "error", "error_message": str}
    """
    try:
        # Validate meal plan structure
        if not isinstance(meal_plan, dict):
            return {
                "status": "error",
                "error_message": "meal_plan must be a dictionary"
            }

        required_keys = ["duration_days", "daily_targets", "days"]
        missing_keys = [k for k in required_keys if k not in meal_plan]

        if missing_keys:
            return {
                "status": "error",
                "error_message": f"meal_plan missing required keys: {', '.join(missing_keys)}"
            }

        # Save to session state
        tool_context.state["meal_plan"] = meal_plan

        # Create summary
        num_days = meal_plan.get("duration_days", 0)
        total_meals = sum(len(day.get("meals", [])) for day in meal_plan.get("days", []))

        summary = f"Saved {num_days}-day meal plan with {total_meals} total meals/snacks"

        return {
            "status": "success",
            "message": "Meal plan saved successfully",
            "summary": summary
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error saving meal plan: {str(e)}"
        }


def retrieve_meal_plan(
    tool_context: ToolContext,
    day_number: Optional[int] = None
) -> dict:
    """
    Retrieve the saved meal plan from session state.

    Can retrieve the entire plan or just a specific day's meals.

    Args:
        tool_context: Tool context with access to session state
        day_number: Optional - if provided, only return that day's meals

    Returns:
        Dictionary with meal plan data or error:
        Success: {
            "status": "success",
            "meal_plan": {...} or specific day data,
            "message": str
        }
        Error: {"status": "error", "error_message": str}
    """
    try:
        meal_plan = tool_context.state.get("meal_plan")

        if not meal_plan:
            return {
                "status": "error",
                "error_message": "No meal plan found in session. Generate a meal plan first."
            }

        # If specific day requested
        if day_number is not None:
            days = meal_plan.get("days", [])

            # Find the day (day numbers are 1-indexed)
            matching_day = None
            for day in days:
                if day.get("day") == day_number:
                    matching_day = day
                    break

            if not matching_day:
                return {
                    "status": "error",
                    "error_message": f"Day {day_number} not found in meal plan (plan has {len(days)} days)"
                }

            return {
                "status": "success",
                "day_data": matching_day,
                "daily_targets": meal_plan.get("daily_targets"),
                "message": f"Retrieved day {day_number} meal data"
            }

        # Return entire meal plan
        return {
            "status": "success",
            "meal_plan": meal_plan,
            "message": "Retrieved complete meal plan"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error retrieving meal plan: {str(e)}"
        }


def get_meal_nutrition_breakdown(tool_context: ToolContext) -> dict:
    """
    Get detailed nutritional breakdown for all meals in the saved meal plan.

    This provides per-meal macros (calories, protein, fat, carbs) so users
    can see exactly what each meal contributes to their daily targets.

    Args:
        tool_context: Tool context with access to session state

    Returns:
        Dictionary with nutritional breakdown:
        Success: {
            "status": "success",
            "daily_targets": {...},
            "meals_breakdown": [
                {
                    "day": 1,
                    "meals": [
                        {
                            "meal_type": "breakfast",
                            "recipe_name": str,
                            "calories": float,
                            "protein_g": float,
                            "fat_g": float,
                            "carbs_g": float,
                            "fiber_g": float
                        },
                        ...
                    ],
                    "daily_total": {
                        "calories": float,
                        "protein_g": float,
                        "fat_g": float,
                        "carbs_g": float
                    }
                },
                ...
            ]
        }
        Error: {"status": "error", "error_message": str}
    """
    try:
        meal_plan = tool_context.state.get("meal_plan")

        if not meal_plan:
            return {
                "status": "error",
                "error_message": "No meal plan found. Generate a meal plan first."
            }

        daily_targets = meal_plan.get("daily_targets", {})
        days = meal_plan.get("days", [])

        meals_breakdown = []

        for day in days:
            day_number = day.get("day")
            day_meals = day.get("meals", [])

            # Extract nutrition for each meal
            meal_details = []
            day_totals = {
                "calories": 0,
                "protein_g": 0,
                "fat_g": 0,
                "carbs_g": 0,
                "fiber_g": 0
            }

            for meal in day_meals:
                recipe = meal.get("recipe", {})
                meal_type = meal.get("meal_type", "unknown")

                meal_nutrition = {
                    "meal_type": meal_type,
                    "recipe_name": recipe.get("name", "Unknown"),
                    "calories": recipe.get("calories", 0),
                    "protein_g": recipe.get("protein_g", 0),
                    "fat_g": recipe.get("fat_g", 0),
                    "carbs_g": recipe.get("carbs_g", 0),
                    "fiber_g": recipe.get("fiber_g", 0)
                }

                meal_details.append(meal_nutrition)

                # Add to daily totals
                day_totals["calories"] += meal_nutrition["calories"]
                day_totals["protein_g"] += meal_nutrition["protein_g"]
                day_totals["fat_g"] += meal_nutrition["fat_g"]
                day_totals["carbs_g"] += meal_nutrition["carbs_g"]
                day_totals["fiber_g"] += meal_nutrition["fiber_g"]

            meals_breakdown.append({
                "day": day_number,
                "meals": meal_details,
                "daily_total": day_totals
            })

        return {
            "status": "success",
            "daily_targets": daily_targets,
            "meals_breakdown": meals_breakdown,
            "message": f"Retrieved nutrition breakdown for {len(meals_breakdown)} days"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error getting meal breakdown: {str(e)}"
        }
