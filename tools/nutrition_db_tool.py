"""
Nutrition Database Tool (MCP Custom Tool)

This tool provides access to a nutrition and recipe database.
In production, this would connect to a real database (SQL, NoSQL, or API).

For now, this is a mock implementation that demonstrates the MCP tool pattern.
You can replace this with actual database connections later.
"""

from typing import Dict, List, Optional, Literal
import json


class NutritionDBTool:
    """
    MCP-style custom tool for nutrition database access.

    This tool provides methods to:
    - Search recipes by criteria
    - Filter by dietary restrictions
    - Get nutritional information
    - Query ingredients
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the nutrition database tool.

        Args:
            db_path: Path to database file (for mock data, this is JSON file)
        """
        self.db_path = db_path
        # In production, initialize database connection here
        self._mock_recipes = self._load_mock_data()

    def _load_mock_data(self) -> List[Dict]:
        """
        Load mock recipe data for development.

        In production, replace this with actual database queries.
        """
        # Mock recipe database
        return [
            {
                "id": "recipe_001",
                "name": "Grilled Chicken Salad",
                "meal_type": "lunch",
                "cuisine": "mediterranean",
                "calories": 350,
                "protein_g": 35,
                "fat_g": 12,
                "carbs_g": 25,
                "fiber_g": 8,
                "prep_time_min": 25,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "chicken breast", "amount": 150, "unit": "g"},
                    {"name": "mixed greens", "amount": 100, "unit": "g"},
                    {"name": "cherry tomatoes", "amount": 50, "unit": "g"},
                    {"name": "olive oil", "amount": 1, "unit": "tbsp"},
                    {"name": "lemon juice", "amount": 1, "unit": "tbsp"}
                ],
                "allergens": [],
                "dietary_tags": ["high_protein", "low_carb", "gluten_free"],
                "restrictions_compatible": ["pescatarian", "none"]
            },
            {
                "id": "recipe_002",
                "name": "Oatmeal with Berries",
                "meal_type": "breakfast",
                "cuisine": "american",
                "calories": 320,
                "protein_g": 12,
                "fat_g": 8,
                "carbs_g": 52,
                "fiber_g": 10,
                "prep_time_min": 10,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "rolled oats", "amount": 60, "unit": "g"},
                    {"name": "almond milk", "amount": 240, "unit": "ml"},
                    {"name": "mixed berries", "amount": 100, "unit": "g"},
                    {"name": "honey", "amount": 1, "unit": "tbsp"},
                    {"name": "almonds", "amount": 15, "unit": "g"}
                ],
                "allergens": ["tree_nuts"],
                "dietary_tags": ["vegetarian", "high_fiber"],
                "restrictions_compatible": ["vegetarian", "pescatarian"]
            },
            {
                "id": "recipe_003",
                "name": "Tofu Stir-Fry",
                "meal_type": "dinner",
                "cuisine": "asian",
                "calories": 380,
                "protein_g": 22,
                "fat_g": 16,
                "carbs_g": 38,
                "fiber_g": 6,
                "prep_time_min": 30,
                "difficulty": "medium",
                "servings": 1,
                "ingredients": [
                    {"name": "firm tofu", "amount": 200, "unit": "g"},
                    {"name": "mixed vegetables", "amount": 150, "unit": "g"},
                    {"name": "brown rice", "amount": 80, "unit": "g"},
                    {"name": "soy sauce", "amount": 2, "unit": "tbsp"},
                    {"name": "sesame oil", "amount": 1, "unit": "tsp"}
                ],
                "allergens": ["soy"],
                "dietary_tags": ["vegan", "vegetarian", "high_protein"],
                "restrictions_compatible": ["vegan", "vegetarian", "pescatarian"]
            },
            {
                "id": "recipe_004",
                "name": "Greek Yogurt Parfait",
                "meal_type": "breakfast",
                "cuisine": "mediterranean",
                "calories": 280,
                "protein_g": 20,
                "fat_g": 5,
                "carbs_g": 38,
                "fiber_g": 6,
                "prep_time_min": 5,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "greek yogurt", "amount": 200, "unit": "g"},
                    {"name": "granola", "amount": 30, "unit": "g"},
                    {"name": "fresh berries", "amount": 80, "unit": "g"},
                    {"name": "honey", "amount": 1, "unit": "tsp"}
                ],
                "allergens": ["dairy"],
                "dietary_tags": ["vegetarian", "high_protein"],
                "restrictions_compatible": ["vegetarian", "pescatarian"]
            },
            {
                "id": "recipe_005",
                "name": "Salmon with Roasted Vegetables",
                "meal_type": "dinner",
                "cuisine": "mediterranean",
                "calories": 420,
                "protein_g": 38,
                "fat_g": 18,
                "carbs_g": 28,
                "fiber_g": 7,
                "prep_time_min": 35,
                "difficulty": "medium",
                "servings": 1,
                "ingredients": [
                    {"name": "salmon fillet", "amount": 150, "unit": "g"},
                    {"name": "broccoli", "amount": 100, "unit": "g"},
                    {"name": "sweet potato", "amount": 150, "unit": "g"},
                    {"name": "olive oil", "amount": 1, "unit": "tbsp"}
                ],
                "allergens": ["fish"],
                "dietary_tags": ["pescatarian", "high_protein", "omega3"],
                "restrictions_compatible": ["pescatarian"]
            },
            {
                "id": "recipe_006",
                "name": "Protein Smoothie Bowl",
                "meal_type": "breakfast",
                "cuisine": "american",
                "calories": 340,
                "protein_g": 28,
                "fat_g": 9,
                "carbs_g": 42,
                "fiber_g": 8,
                "prep_time_min": 10,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "protein powder", "amount": 30, "unit": "g"},
                    {"name": "banana", "amount": 1, "unit": "whole"},
                    {"name": "spinach", "amount": 50, "unit": "g"},
                    {"name": "almond milk", "amount": 200, "unit": "ml"},
                    {"name": "chia seeds", "amount": 1, "unit": "tbsp"}
                ],
                "allergens": [],
                "dietary_tags": ["high_protein", "post_workout"],
                "restrictions_compatible": ["vegetarian", "vegan", "pescatarian"]
            },
            {
                "id": "recipe_007",
                "name": "Quinoa Buddha Bowl",
                "meal_type": "lunch",
                "cuisine": "mediterranean",
                "calories": 390,
                "protein_g": 18,
                "fat_g": 14,
                "carbs_g": 48,
                "fiber_g": 12,
                "prep_time_min": 25,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "quinoa", "amount": 80, "unit": "g"},
                    {"name": "chickpeas", "amount": 100, "unit": "g"},
                    {"name": "avocado", "amount": 50, "unit": "g"},
                    {"name": "mixed vegetables", "amount": 100, "unit": "g"},
                    {"name": "tahini", "amount": 2, "unit": "tbsp"}
                ],
                "allergens": ["sesame"],
                "dietary_tags": ["vegan", "vegetarian", "high_fiber", "gluten_free"],
                "restrictions_compatible": ["vegan", "vegetarian", "pescatarian", "gluten_free"]
            },
            {
                "id": "recipe_008",
                "name": "Turkey and Cheese Wrap",
                "meal_type": "lunch",
                "cuisine": "american",
                "calories": 365,
                "protein_g": 32,
                "fat_g": 12,
                "carbs_g": 32,
                "fiber_g": 5,
                "prep_time_min": 10,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "turkey breast", "amount": 100, "unit": "g"},
                    {"name": "whole wheat tortilla", "amount": 1, "unit": "whole"},
                    {"name": "cheddar cheese", "amount": 30, "unit": "g"},
                    {"name": "lettuce", "amount": 30, "unit": "g"},
                    {"name": "tomato", "amount": 50, "unit": "g"}
                ],
                "allergens": ["dairy", "gluten"],
                "dietary_tags": ["high_protein"],
                "restrictions_compatible": []
            },
            {
                "id": "recipe_009",
                "name": "Protein Pancakes",
                "meal_type": "breakfast",
                "cuisine": "american",
                "calories": 310,
                "protein_g": 24,
                "fat_g": 8,
                "carbs_g": 36,
                "fiber_g": 4,
                "prep_time_min": 15,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "protein powder", "amount": 30, "unit": "g"},
                    {"name": "oat flour", "amount": 40, "unit": "g"},
                    {"name": "egg", "amount": 2, "unit": "whole"},
                    {"name": "banana", "amount": 1, "unit": "whole"},
                    {"name": "almond milk", "amount": 50, "unit": "ml"}
                ],
                "allergens": ["eggs"],
                "dietary_tags": ["high_protein", "vegetarian"],
                "restrictions_compatible": ["vegetarian", "pescatarian"]
            },
            {
                "id": "recipe_010",
                "name": "Lentil Curry with Rice",
                "meal_type": "dinner",
                "cuisine": "indian",
                "calories": 410,
                "protein_g": 20,
                "fat_g": 10,
                "carbs_g": 62,
                "fiber_g": 15,
                "prep_time_min": 40,
                "difficulty": "medium",
                "servings": 1,
                "ingredients": [
                    {"name": "red lentils", "amount": 100, "unit": "g"},
                    {"name": "basmati rice", "amount": 80, "unit": "g"},
                    {"name": "coconut milk", "amount": 100, "unit": "ml"},
                    {"name": "curry spices", "amount": 2, "unit": "tsp"},
                    {"name": "spinach", "amount": 50, "unit": "g"}
                ],
                "allergens": [],
                "dietary_tags": ["vegan", "vegetarian", "high_fiber", "gluten_free"],
                "restrictions_compatible": ["vegan", "vegetarian", "pescatarian", "gluten_free"]
            },
            {
                "id": "recipe_011",
                "name": "Cottage Cheese Snack Bowl",
                "meal_type": "snack",
                "cuisine": "american",
                "calories": 180,
                "protein_g": 22,
                "fat_g": 4,
                "carbs_g": 14,
                "fiber_g": 2,
                "prep_time_min": 5,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "cottage cheese", "amount": 150, "unit": "g"},
                    {"name": "cucumber", "amount": 50, "unit": "g"},
                    {"name": "cherry tomatoes", "amount": 50, "unit": "g"},
                    {"name": "black pepper", "amount": 1, "unit": "pinch"}
                ],
                "allergens": ["dairy"],
                "dietary_tags": ["vegetarian", "high_protein", "low_carb"],
                "restrictions_compatible": ["vegetarian", "pescatarian"]
            },
            {
                "id": "recipe_012",
                "name": "Protein Energy Balls",
                "meal_type": "snack",
                "cuisine": "american",
                "calories": 160,
                "protein_g": 8,
                "fat_g": 8,
                "carbs_g": 16,
                "fiber_g": 4,
                "prep_time_min": 15,
                "difficulty": "easy",
                "servings": 1,
                "ingredients": [
                    {"name": "oats", "amount": 30, "unit": "g"},
                    {"name": "peanut butter", "amount": 20, "unit": "g"},
                    {"name": "honey", "amount": 1, "unit": "tsp"},
                    {"name": "protein powder", "amount": 10, "unit": "g"},
                    {"name": "dark chocolate chips", "amount": 10, "unit": "g"}
                ],
                "allergens": ["peanuts"],
                "dietary_tags": ["vegetarian", "high_protein"],
                "restrictions_compatible": ["vegetarian", "pescatarian"]
            }
        ]

    def search_recipes(
        self,
        meal_type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = None,
        max_calories: Optional[float] = None,
        min_protein: Optional[float] = None,
        dietary_restriction: Optional[str] = None,
        exclude_allergens: Optional[List[str]] = None,
        max_prep_time: Optional[int] = None,
        cuisine: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """
        Search recipes based on multiple criteria.

        Args:
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            max_calories: Maximum calories per serving
            min_protein: Minimum protein in grams
            dietary_restriction: Dietary restriction (vegan, vegetarian, etc.)
            exclude_allergens: List of allergens to exclude
            max_prep_time: Maximum preparation time in minutes
            cuisine: Cuisine type
            limit: Maximum number of results to return

        Returns:
            Dictionary with status and matching recipes:
            Success: {"status": "success", "recipes": [...], "count": int}
            Error: {"status": "error", "error_message": str}
        """
        try:
            results = self._mock_recipes.copy()

            # Apply filters
            if meal_type:
                results = [r for r in results if r["meal_type"] == meal_type]

            if max_calories:
                results = [r for r in results if r["calories"] <= max_calories]

            if min_protein:
                results = [r for r in results if r["protein_g"] >= min_protein]

            if dietary_restriction:
                results = [
                    r for r in results
                    if dietary_restriction in r["restrictions_compatible"]
                    or dietary_restriction in r["dietary_tags"]
                ]

            if exclude_allergens:
                for allergen in exclude_allergens:
                    results = [
                        r for r in results
                        if allergen not in r["allergens"]
                    ]

            if max_prep_time:
                results = [r for r in results if r["prep_time_min"] <= max_prep_time]

            if cuisine:
                results = [r for r in results if r["cuisine"] == cuisine]

            # Limit results
            results = results[:limit]

            return {
                "status": "success",
                "recipes": results,
                "count": len(results)
            }

        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Error searching recipes: {str(e)}"
            }

    def get_recipe_by_id(self, recipe_id: str) -> Dict:
        """
        Retrieve a specific recipe by ID.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            Dictionary with status and recipe data
        """
        try:
            recipe = next(
                (r for r in self._mock_recipes if r["id"] == recipe_id),
                None
            )

            if recipe:
                return {
                    "status": "success",
                    "recipe": recipe
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Recipe with ID '{recipe_id}' not found"
                }

        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Error retrieving recipe: {str(e)}"
            }

    def get_compatible_recipes_for_goals(
        self,
        target_calories_per_meal: float,
        target_protein_per_meal: float,
        dietary_restrictions: List[str],
        exclude_allergens: List[str],
        meal_type: str,
        tolerance: float = 0.15
    ) -> Dict:
        """
        Find recipes that match specific nutritional goals.

        Args:
            target_calories_per_meal: Target calories for the meal
            target_protein_per_meal: Target protein in grams
            dietary_restrictions: List of dietary restrictions
            exclude_allergens: List of allergens to exclude
            meal_type: Type of meal
            tolerance: Acceptable deviation from targets (default 15%)

        Returns:
            Dictionary with compatible recipes scored by fit
        """
        try:
            # Search with basic filters
            all_recipes = self.search_recipes(
                meal_type=meal_type,
                exclude_allergens=exclude_allergens,
                limit=50
            )

            if all_recipes["status"] == "error":
                return all_recipes

            # Score recipes by nutritional fit
            scored_recipes = []
            for recipe in all_recipes["recipes"]:
                # Check dietary restrictions
                compatible = any(
                    restriction in recipe["restrictions_compatible"]
                    for restriction in dietary_restrictions
                ) if dietary_restrictions else True

                if not compatible:
                    continue

                # Calculate fit score (0-100)
                cal_diff = abs(recipe["calories"] - target_calories_per_meal) / target_calories_per_meal
                protein_diff = abs(recipe["protein_g"] - target_protein_per_meal) / target_protein_per_meal

                # Only include if within tolerance
                if cal_diff <= tolerance and protein_diff <= tolerance:
                    fit_score = 100 - (cal_diff * 50 + protein_diff * 50)

                    scored_recipes.append({
                        "recipe": recipe,
                        "compatibility_score": round(fit_score, 1),
                        "calorie_diff": round(cal_diff * 100, 1),
                        "protein_diff": round(protein_diff * 100, 1)
                    })

            # Sort by compatibility score
            scored_recipes.sort(key=lambda x: x["compatibility_score"], reverse=True)

            return {
                "status": "success",
                "compatible_recipes": scored_recipes,
                "count": len(scored_recipes)
            }

        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Error finding compatible recipes: {str(e)}"
            }


# Singleton instance for efficiency
_nutrition_db_instance = None


def get_nutrition_db() -> NutritionDBTool:
    """Get or create the singleton nutrition database instance."""
    global _nutrition_db_instance
    if _nutrition_db_instance is None:
        _nutrition_db_instance = NutritionDBTool()
    return _nutrition_db_instance


# Function wrappers for ADK tool integration
def search_nutrition_db(
    meal_type: Optional[str] = None,
    max_calories: Optional[float] = None,
    min_protein: Optional[float] = None,
    dietary_restriction: Optional[str] = None,
    exclude_allergens: Optional[List[str]] = None
) -> Dict:
    """
    Search the nutrition database for recipes.

    This is a wrapper function that can be used directly as an ADK tool.
    Uses a singleton database instance for efficiency.

    Args:
        meal_type: Type of meal to search for ("breakfast", "lunch", "dinner", "snack")
        max_calories: Maximum calories per serving
        min_protein: Minimum protein in grams
        dietary_restriction: Dietary restriction to filter by (e.g., "vegan", "vegetarian")
        exclude_allergens: List of allergens to exclude (e.g., ["dairy", "tree_nuts"])

    Returns:
        Dictionary with status and search results:
        Success: {"status": "success", "recipes": [...], "count": int}
        Error: {"status": "error", "error_message": str}
    """
    db_tool = get_nutrition_db()
    return db_tool.search_recipes(
        meal_type=meal_type,
        max_calories=max_calories,
        min_protein=min_protein,
        dietary_restriction=dietary_restriction,
        exclude_allergens=exclude_allergens if exclude_allergens else []
    )
