"""
Recipe Generator Tool - Creates custom recipes using AI when database doesn't have matches

Uses Gemini to generate recipes that match:
- User's nutritional targets
- Dietary restrictions and allergies
- Budget and cooking skill level
- Meal type and preferences
"""

from typing import Dict, List, Optional, Literal
from google.genai import types
from google.genai.client import Client
import json
import os

# Initialize Gemini client
client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_custom_recipe(
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"],
    target_calories: float,
    target_protein_g: float,
    target_fat_g: float,
    target_carbs_g: float,
    dietary_restrictions: Optional[List[str]] = None,
    exclude_allergens: Optional[List[str]] = None,
    foods_to_avoid: Optional[List[str]] = None,
    cooking_skill: str = "intermediate",
    budget_level: str = "medium",
    cuisine_preference: Optional[str] = None
) -> Dict:
    """
    Generate a custom recipe using AI that matches the specified nutritional targets and restrictions.

    Args:
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
        target_calories: Target calories for this meal
        target_protein_g: Target protein in grams
        target_fat_g: Target fat in grams
        target_carbs_g: Target carbohydrates in grams
        dietary_restrictions: List of dietary restrictions (e.g., ["gluten_free", "vegan"])
        exclude_allergens: List of allergens to exclude (e.g., ["dairy", "tree_nuts"])
        foods_to_avoid: List of foods to avoid (e.g., ["fruits", "mushrooms"])
        cooking_skill: User's cooking skill level
        budget_level: Budget constraint
        cuisine_preference: Preferred cuisine type (optional)

    Returns:
        Dictionary with generated recipe in the database format, or error
    """
    try:
        # Build the prompt
        dietary_restrictions = dietary_restrictions or []
        exclude_allergens = exclude_allergens or []
        foods_to_avoid = foods_to_avoid or []

        restrictions_text = ", ".join(dietary_restrictions) if dietary_restrictions else "none"
        allergens_text = ", ".join(exclude_allergens) if exclude_allergens else "none"
        avoid_text = ", ".join(foods_to_avoid) if foods_to_avoid else "none"
        cuisine_text = cuisine_preference or "any cuisine"

        prompt = f"""Create a {meal_type} recipe that matches these exact requirements:

**NUTRITIONAL TARGETS (must be close):**
- Calories: {target_calories} kcal (±10%)
- Protein: {target_protein_g}g (±5g)
- Fat: {target_fat_g}g (±5g)
- Carbohydrates: {target_carbs_g}g (±10g)

**DIETARY REQUIREMENTS:**
- Dietary restrictions: {restrictions_text}
- Allergens to exclude: {allergens_text}
- Foods to avoid: {avoid_text}
- Cooking skill level: {cooking_skill}
- Budget: {budget_level}
- Cuisine preference: {cuisine_text}

**IMPORTANT RULES:**
1. The recipe MUST respect ALL dietary restrictions and allergens
2. Do NOT use any foods from the "avoid" list
3. Keep it simple for the specified cooking skill level
4. Use affordable ingredients for the budget level
5. Provide realistic portion sizes (servings: 1)
6. Calculate accurate nutritional values

**OUTPUT FORMAT (JSON only, no other text):**
{{
    "name": "Recipe Name",
    "meal_type": "{meal_type}",
    "cuisine": "cuisine type",
    "calories": <number>,
    "protein_g": <number>,
    "fat_g": <number>,
    "carbs_g": <number>,
    "fiber_g": <number>,
    "prep_time_min": <number>,
    "difficulty": "easy/medium/hard",
    "servings": 1,
    "ingredients": [
        {{"name": "ingredient name", "amount": <number>, "unit": "g/ml/tbsp/tsp/whole"}},
        ...
    ],
    "instructions": [
        "Step 1 instruction",
        "Step 2 instruction",
        ...
    ],
    "allergens": ["list of allergens present"],
    "dietary_tags": ["gluten_free", "vegan", etc],
    "restrictions_compatible": ["vegetarian", "vegan", etc]
}}

Generate the recipe now. Return ONLY valid JSON, nothing else."""

        # Call Gemini to generate the recipe
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2000,
            )
        )

        # Extract JSON from response
        recipe_text = response.text.strip()

        # Remove markdown code blocks if present
        if recipe_text.startswith("```json"):
            recipe_text = recipe_text[7:]
        if recipe_text.startswith("```"):
            recipe_text = recipe_text[3:]
        if recipe_text.endswith("```"):
            recipe_text = recipe_text[:-3]

        recipe_text = recipe_text.strip()

        # Parse JSON
        try:
            recipe = json.loads(recipe_text)
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error_message": f"Failed to parse generated recipe JSON: {str(e)}"
            }

        # Add unique ID
        import time
        recipe["id"] = f"generated_{int(time.time())}"

        # Validate nutritional targets are close
        cal_diff = abs(recipe["calories"] - target_calories)
        if cal_diff > target_calories * 0.15:  # More than 15% off
            return {
                "status": "warning",
                "recipe": recipe,
                "message": f"Generated recipe calories ({recipe['calories']}) differ from target ({target_calories})"
            }

        return {
            "status": "success",
            "recipe": recipe,
            "message": f"Generated custom {meal_type} recipe: {recipe['name']}"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error generating recipe: {str(e)}"
        }


def generate_meal_plan_recipes(
    tool_context,
    num_days: int,
    daily_calories: float,
    daily_protein_g: float,
    daily_fat_g: float,
    daily_carbs_g: float,
    meals_per_day: int = 3,
    snacks_per_day: int = 2,
    dietary_restrictions: Optional[List[str]] = None,
    exclude_allergens: Optional[List[str]] = None,
    foods_to_avoid: Optional[List[str]] = None,
    cooking_skill: str = "intermediate",
    budget_level: str = "medium",
    cuisine_preference: Optional[str] = None
) -> dict:
    """
    Generate a complete meal plan with custom recipes for specified number of days.

    This creates recipes for all meals across the specified days, ensuring
    variety and hitting daily nutritional targets. The meal plan is automatically
    saved to session state for later retrieval.

    Args:
        num_days: Number of days for the meal plan
        daily_calories: Daily calorie target
        daily_protein_g: Daily protein target
        daily_fat_g: Daily fat target
        daily_carbs_g: Daily carbs target
        meals_per_day: Number of main meals (default 3)
        snacks_per_day: Number of snacks (default 2)
        dietary_restrictions: List of dietary restrictions
        exclude_allergens: List of allergens to exclude
        foods_to_avoid: List of foods to avoid
        cooking_skill: Cooking skill level
        budget_level: Budget constraint
        cuisine_preference: Preferred cuisine

    Returns:
        Dictionary with complete meal plan or error
    """
    try:
        # Calculate calorie distribution
        total_meals = meals_per_day + snacks_per_day

        # Standard distribution
        breakfast_cal = daily_calories * 0.25
        lunch_cal = daily_calories * 0.30
        dinner_cal = daily_calories * 0.30
        snack_cal = daily_calories * 0.15 / snacks_per_day if snacks_per_day > 0 else 0

        # Distribute macros proportionally
        breakfast_protein = daily_protein_g * 0.25
        breakfast_fat = daily_fat_g * 0.25
        breakfast_carbs = daily_carbs_g * 0.25

        lunch_protein = daily_protein_g * 0.30
        lunch_fat = daily_fat_g * 0.30
        lunch_carbs = daily_carbs_g * 0.30

        dinner_protein = daily_protein_g * 0.30
        dinner_fat = daily_fat_g * 0.30
        dinner_carbs = daily_carbs_g * 0.30

        snack_protein = daily_protein_g * 0.15 / snacks_per_day if snacks_per_day > 0 else 0
        snack_fat = daily_fat_g * 0.15 / snacks_per_day if snacks_per_day > 0 else 0
        snack_carbs = daily_carbs_g * 0.15 / snacks_per_day if snacks_per_day > 0 else 0

        meal_plan = {
            "duration_days": num_days,
            "daily_targets": {
                "calories": daily_calories,
                "protein_g": daily_protein_g,
                "fat_g": daily_fat_g,
                "carbs_g": daily_carbs_g
            },
            "days": []
        }

        # Generate recipes for each day
        for day in range(1, num_days + 1):
            day_meals = {
                "day": day,
                "meals": []
            }

            # Breakfast
            breakfast_result = generate_custom_recipe(
                meal_type="breakfast",
                target_calories=breakfast_cal,
                target_protein_g=breakfast_protein,
                target_fat_g=breakfast_fat,
                target_carbs_g=breakfast_carbs,
                dietary_restrictions=dietary_restrictions,
                exclude_allergens=exclude_allergens,
                foods_to_avoid=foods_to_avoid,
                cooking_skill=cooking_skill,
                budget_level=budget_level,
                cuisine_preference=cuisine_preference
            )

            if breakfast_result["status"] in ["success", "warning"]:
                day_meals["meals"].append({
                    "meal_type": "breakfast",
                    "recipe": breakfast_result["recipe"]
                })

            # Lunch
            lunch_result = generate_custom_recipe(
                meal_type="lunch",
                target_calories=lunch_cal,
                target_protein_g=lunch_protein,
                target_fat_g=lunch_fat,
                target_carbs_g=lunch_carbs,
                dietary_restrictions=dietary_restrictions,
                exclude_allergens=exclude_allergens,
                foods_to_avoid=foods_to_avoid,
                cooking_skill=cooking_skill,
                budget_level=budget_level,
                cuisine_preference=cuisine_preference
            )

            if lunch_result["status"] in ["success", "warning"]:
                day_meals["meals"].append({
                    "meal_type": "lunch",
                    "recipe": lunch_result["recipe"]
                })

            # Dinner
            dinner_result = generate_custom_recipe(
                meal_type="dinner",
                target_calories=dinner_cal,
                target_protein_g=dinner_protein,
                target_fat_g=dinner_fat,
                target_carbs_g=dinner_carbs,
                dietary_restrictions=dietary_restrictions,
                exclude_allergens=exclude_allergens,
                foods_to_avoid=foods_to_avoid,
                cooking_skill=cooking_skill,
                budget_level=budget_level,
                cuisine_preference=cuisine_preference
            )

            if dinner_result["status"] in ["success", "warning"]:
                day_meals["meals"].append({
                    "meal_type": "dinner",
                    "recipe": dinner_result["recipe"]
                })

            # Snacks
            for snack_num in range(snacks_per_day):
                snack_result = generate_custom_recipe(
                    meal_type="snack",
                    target_calories=snack_cal,
                    target_protein_g=snack_protein,
                    target_fat_g=snack_fat,
                    target_carbs_g=snack_carbs,
                    dietary_restrictions=dietary_restrictions,
                    exclude_allergens=exclude_allergens,
                    foods_to_avoid=foods_to_avoid,
                    cooking_skill=cooking_skill,
                    budget_level=budget_level,
                    cuisine_preference=cuisine_preference
                )

                if snack_result["status"] in ["success", "warning"]:
                    day_meals["meals"].append({
                        "meal_type": f"snack_{snack_num + 1}",
                        "recipe": snack_result["recipe"]
                    })

            meal_plan["days"].append(day_meals)

        # Automatically save to session state for later retrieval
        tool_context.state["meal_plan"] = meal_plan

        return {
            "status": "success",
            "meal_plan": meal_plan,
            "message": f"Generated {num_days}-day meal plan with custom recipes"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error generating meal plan: {str(e)}"
        }
