"""
KBJU Calculator Tool

Calculates personalized nutritional requirements (Calories, Protein, Fat, Carbohydrates)
based on user data using validated formulas.

This tool implements:
- Mifflin-St Jeor Equation for BMR (Basal Metabolic Rate)
- Activity level multipliers
- Goal-based caloric adjustments
- Evidence-based macro distribution
"""

from typing import Dict, Literal
from google.adk.tools.tool_context import ToolContext


def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Literal["male", "female"]
) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.

    This is the most accurate modern formula for BMR calculation.

    Args:
        weight_kg: Body weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: Biological sex ("male" or "female")

    Returns:
        BMR in calories per day
    """
    if gender == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    return bmr


def get_activity_multiplier(
    activity_level: Literal[
        "sedentary",
        "lightly_active",
        "moderately_active",
        "very_active",
        "extremely_active"
    ]
) -> float:
    """
    Get activity level multiplier for TDEE calculation.

    Args:
        activity_level: User's typical activity level

    Returns:
        Multiplier for BMR to get TDEE (Total Daily Energy Expenditure)
    """
    multipliers = {
        "sedentary": 1.2,           # Little or no exercise
        "lightly_active": 1.375,    # Light exercise 1-3 days/week
        "moderately_active": 1.55,  # Moderate exercise 3-5 days/week
        "very_active": 1.725,       # Hard exercise 6-7 days/week
        "extremely_active": 1.9     # Very hard exercise, physical job
    }
    return multipliers.get(activity_level, 1.2)


def calculate_kbju(
    tool_context: ToolContext,
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Literal["male", "female"],
    activity_level: Literal[
        "sedentary",
        "lightly_active",
        "moderately_active",
        "very_active",
        "extremely_active"
    ],
    goal: Literal["weight_loss", "maintenance", "muscle_gain", "recomp"] = "maintenance",
    goal_rate: Literal["slow", "moderate", "aggressive"] = "moderate"
) -> Dict:
    """
    Calculate personalized KBJU (Calories, Protein, Fat, Carbs) requirements.

    This tool calculates daily nutritional targets based on validated formulas
    and evidence-based recommendations. Results are automatically saved to
    session state for other agents to access.

    Args:
        tool_context: Tool context with access to session state
        weight_kg: Current body weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: Biological sex ("male" or "female")
        activity_level: Typical activity level
        goal: Primary fitness/health goal
        goal_rate: Rate of progress (affects caloric deficit/surplus)

    Returns:
        Dictionary with status and KBJU calculations:
        Success: {
            "status": "success",
            "bmr": float,
            "tdee": float,
            "target_calories": float,
            "protein_g": float,
            "fat_g": float,
            "carbs_g": float,
            "protein_cal": float,
            "fat_cal": float,
            "carbs_cal": float,
            "notes": str
        }
        Error: {"status": "error", "error_message": str}
    """
    try:
        # Input validation
        if weight_kg <= 0 or height_cm <= 0 or age <= 0:
            return {
                "status": "error",
                "error_message": "Weight, height, and age must be positive values"
            }

        if age < 18:
            return {
                "status": "error",
                "error_message": "This calculator is designed for adults 18+. Please consult a pediatric nutritionist."
            }

        # Calculate BMR
        bmr = calculate_bmr(weight_kg, height_cm, age, gender)

        # Calculate TDEE (Total Daily Energy Expenditure)
        activity_multiplier = get_activity_multiplier(activity_level)
        tdee = bmr * activity_multiplier

        # Adjust for goal
        goal_adjustments = {
            "weight_loss": {
                "slow": -250,        # ~0.25 kg/week
                "moderate": -500,    # ~0.5 kg/week
                "aggressive": -750   # ~0.75 kg/week
            },
            "maintenance": {
                "slow": 0,
                "moderate": 0,
                "aggressive": 0
            },
            "muscle_gain": {
                "slow": 200,         # Lean bulk
                "moderate": 350,     # Moderate bulk
                "aggressive": 500    # Aggressive bulk
            },
            "recomp": {
                "slow": 0,           # Body recomposition
                "moderate": 0,
                "aggressive": 0
            }
        }

        adjustment = goal_adjustments[goal][goal_rate]
        target_calories = tdee + adjustment

        # Ensure safe minimum calories
        min_calories = 1200 if gender == "female" else 1500
        if target_calories < min_calories:
            target_calories = min_calories
            notes = f"Calories adjusted to safe minimum ({min_calories} kcal)"
        else:
            notes = f"Calculation based on {goal} goal at {goal_rate} rate"

        # Calculate macros
        macros = calculate_macro_distribution(
            target_calories=target_calories,
            weight_kg=weight_kg,
            goal=goal,
            activity_level=activity_level
        )

        if macros["status"] == "error":
            return macros

        result = {
            "status": "success",
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "target_calories": round(target_calories, 1),
            "protein_g": macros["protein_g"],
            "fat_g": macros["fat_g"],
            "carbs_g": macros["carbs_g"],
            "protein_cal": macros["protein_cal"],
            "fat_cal": macros["fat_cal"],
            "carbs_cal": macros["carbs_cal"],
            "protein_percent": macros["protein_percent"],
            "fat_percent": macros["fat_percent"],
            "carbs_percent": macros["carbs_percent"],
            "notes": notes
        }

        # Automatically save to session state for other agents
        tool_context.state["kbju_calculation"] = result

        return result

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error calculating KBJU: {str(e)}"
        }


def calculate_macro_distribution(
    target_calories: float,
    weight_kg: float,
    goal: Literal["weight_loss", "maintenance", "muscle_gain", "recomp"],
    activity_level: str
) -> Dict:
    """
    Calculate optimal macro distribution (Protein, Fat, Carbs) based on goal.

    Uses evidence-based recommendations for macro ratios.

    Args:
        target_calories: Daily caloric target
        weight_kg: Body weight in kg
        goal: Primary fitness/health goal
        activity_level: Activity level (affects protein needs)

    Returns:
        Dictionary with status and macro breakdown
    """
    try:
        # Protein calculation (most important, set first)
        # Recommendations: 1.6-2.2 g/kg for active individuals
        if goal == "muscle_gain":
            protein_per_kg = 2.2
        elif goal in ["recomp", "weight_loss"]:
            protein_per_kg = 2.0
        else:  # maintenance
            protein_per_kg = 1.8

        # Adjust for activity level
        if activity_level in ["very_active", "extremely_active"]:
            protein_per_kg += 0.2

        protein_g = weight_kg * protein_per_kg
        protein_cal = protein_g * 4  # 4 cal per gram

        # Fat calculation (set second, essential for hormones)
        # Minimum: 0.8 g/kg, typically 20-35% of calories
        fat_percent = 0.25  # 25% default
        if goal == "weight_loss":
            fat_percent = 0.25
        elif goal == "muscle_gain":
            fat_percent = 0.25
        else:
            fat_percent = 0.30

        fat_cal = target_calories * fat_percent
        fat_g = fat_cal / 9  # 9 cal per gram

        # Ensure minimum fat intake
        min_fat_g = weight_kg * 0.8
        if fat_g < min_fat_g:
            fat_g = min_fat_g
            fat_cal = fat_g * 9

        # Carbs calculation (remainder of calories)
        carbs_cal = target_calories - protein_cal - fat_cal
        carbs_g = carbs_cal / 4  # 4 cal per gram

        # Validation
        if carbs_g < 0:
            return {
                "status": "error",
                "error_message": "Unable to fit macros within calorie target. Protein and fat requirements exceed total calories."
            }

        # Calculate percentages
        protein_percent = round((protein_cal / target_calories) * 100, 1)
        fat_percent = round((fat_cal / target_calories) * 100, 1)
        carbs_percent = round((carbs_cal / target_calories) * 100, 1)

        return {
            "status": "success",
            "protein_g": round(protein_g, 1),
            "fat_g": round(fat_g, 1),
            "carbs_g": round(carbs_g, 1),
            "protein_cal": round(protein_cal, 1),
            "fat_cal": round(fat_cal, 1),
            "carbs_cal": round(carbs_cal, 1),
            "protein_percent": protein_percent,
            "fat_percent": fat_percent,
            "carbs_percent": carbs_percent
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error calculating macro distribution: {str(e)}"
        }


def retrieve_kbju_calculation(tool_context: ToolContext) -> Dict:
    """
    Retrieve KBJU calculation results from session state.

    This allows downstream agents to access the nutritional targets.

    Args:
        tool_context: Tool context with access to session state

    Returns:
        Dictionary with KBJU data or error
    """
    try:
        kbju_data = tool_context.state.get("kbju_calculation")

        if not kbju_data:
            return {
                "status": "error",
                "error_message": "No KBJU calculation found in session. Analysis must be completed first."
            }

        return {
            "status": "success",
            "kbju_data": kbju_data,
            "message": "KBJU calculation retrieved successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error retrieving KBJU calculation: {str(e)}"
        }
