"""
Kaggle Recipe Dataset Tool - Uses real recipe data from Kaggle

Dataset: Better Recipes for a Better Life
Source: https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life

This tool loads recipes from the Kaggle dataset and filters them based on:
- Nutritional targets (calories, protein, fat, carbs)
- Dietary restrictions (vegetarian, vegan, gluten-free, etc.)
- Allergens
- Meal type preferences

Falls back to AI generation if dataset is not available.
"""

import os
import pandas as pd
import ast
from typing import Optional, List, Literal
from pathlib import Path


# Dataset paths
DATA_DIR = Path(__file__).parent.parent / "data"
DATASET_FILES = [
    "recipes.csv",
    "recipes_data.csv",
    "full_dataset.csv",
    "better-recipes.csv"
]

# Global dataset cache
_dataset = None
_dataset_loaded = False


def load_recipe_dataset() -> Optional[pd.DataFrame]:
    """
    Load the Kaggle recipe dataset.

    Returns:
        DataFrame with recipe data, or None if not found
    """
    global _dataset, _dataset_loaded

    # Return cached dataset
    if _dataset_loaded:
        return _dataset

    # Try to find and load the dataset
    for filename in DATASET_FILES:
        filepath = DATA_DIR / filename
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                _dataset = df
                _dataset_loaded = True
                print(f"✓ Loaded Kaggle recipe dataset: {filename} ({len(df)} recipes)")
                return df
            except Exception as e:
                print(f"⚠ Error loading {filename}: {e}")
                continue

    # Dataset not found
    _dataset_loaded = True  # Don't try again
    print("⚠ Kaggle recipe dataset not found in data/ directory")
    print("   Download from: https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life")
    return None


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to expected format.

    Common variations:
    - Name, title, recipe_name → name
    - Calories, calories, cal → calories
    - Protein, protein_g, ProteinContent → protein_g
    """
    if df is None:
        return None

    # Column mapping (from possible names → standard name)
    column_mapping = {
        # Name
        'title': 'name',
        'recipe_name': 'name',
        'recipename': 'name',

        # Calories
        'cal': 'calories',
        'Calories': 'calories',
        'CalorieContent': 'calories',

        # Protein
        'Protein': 'protein_g',
        'ProteinContent': 'protein_g',
        'protein': 'protein_g',

        # Fat
        'Fat': 'fat_g',
        'FatContent': 'fat_g',
        'fat': 'fat_g',

        # Carbs
        'Carbs': 'carbs_g',
        'Carbohydrates': 'carbs_g',
        'CarbohydrateContent': 'carbs_g',
        'carbs': 'carbs_g',
        'carbohydrates': 'carbs_g',

        # Fiber
        'Fiber': 'fiber_g',
        'FiberContent': 'fiber_g',
        'fiber': 'fiber_g',

        # Other fields
        'RecipeCategory': 'meal_type',
        'Category': 'meal_type',
        'category': 'meal_type',
        'Keywords': 'tags',
        'keywords': 'tags',
        'RecipeIngredientParts': 'ingredients',
        'RecipeInstructions': 'instructions',
    }

    # Rename columns
    df = df.rename(columns=column_mapping)

    # Parse nutrition list if it exists as a single column
    # Format: ['calories', 'total_fat_g', 'sugar_g', 'sodium_mg', 'protein_g', 'saturated_fat_g', 'carbs_g']
    if 'nutrition' in df.columns:
        def parse_nutrition(nutrition_str):
            """Parse nutrition list into individual values"""
            try:
                if pd.isna(nutrition_str):
                    return pd.Series([0, 0, 0, 0, 0, 0, 0])

                # Parse the string list
                nutrition_list = ast.literal_eval(str(nutrition_str))

                if isinstance(nutrition_list, list) and len(nutrition_list) >= 7:
                    return pd.Series([
                        float(nutrition_list[0]),  # calories
                        float(nutrition_list[1]),  # total_fat_g
                        float(nutrition_list[2]),  # sugar_g
                        float(nutrition_list[3]),  # sodium_mg
                        float(nutrition_list[4]),  # protein_g
                        float(nutrition_list[5]),  # saturated_fat_g
                        float(nutrition_list[6])   # carbs_g
                    ])
                else:
                    return pd.Series([0, 0, 0, 0, 0, 0, 0])
            except:
                return pd.Series([0, 0, 0, 0, 0, 0, 0])

        # Apply parsing and create new columns
        df[['calories', 'fat_g', 'sugar_g', 'sodium_mg', 'protein_g', 'saturated_fat_g', 'carbs_g']] = \
            df['nutrition'].apply(parse_nutrition)

    return df


def search_kaggle_recipes(
    meal_type: Optional[str] = None,
    min_calories: Optional[float] = None,
    max_calories: Optional[float] = None,
    min_protein_g: Optional[float] = None,
    max_protein_g: Optional[float] = None,
    min_carbs_g: Optional[float] = None,
    max_carbs_g: Optional[float] = None,
    min_fat_g: Optional[float] = None,
    max_fat_g: Optional[float] = None,
    dietary_restrictions: Optional[List[str]] = None,
    exclude_allergens: Optional[List[str]] = None,
    exclude_ingredients: Optional[List[str]] = None,
    max_results: int = 20
) -> dict:
    """
    Search Kaggle recipe dataset for recipes matching criteria.

    Args:
        meal_type: breakfast, lunch, dinner, snack, dessert (optional)
        min_calories: Minimum calories
        max_calories: Maximum calories
        min_protein_g: Minimum protein in grams
        max_protein_g: Maximum protein in grams
        min_carbs_g: Minimum carbs in grams
        max_carbs_g: Maximum carbs in grams
        min_fat_g: Minimum fat in grams
        max_fat_g: Maximum fat in grams
        dietary_restrictions: List like ["vegetarian", "vegan", "gluten_free"]
        exclude_allergens: List like ["dairy", "nuts", "eggs"]
        exclude_ingredients: Specific ingredients to avoid
        max_results: Maximum number of recipes to return

    Returns:
        Dictionary with status and filtered recipes:
        Success: {
            "status": "success",
            "recipes": [...],
            "count": int,
            "source": "kaggle_dataset",
            "message": str
        }
        Fallback (no dataset): {
            "status": "fallback",
            "message": "Dataset not available, use AI generation"
        }
        Error: {
            "status": "error",
            "error_message": str
        }
    """
    try:
        # Load dataset
        df = load_recipe_dataset()

        if df is None:
            return {
                "status": "fallback",
                "message": "Kaggle dataset not available. Use generate_custom_recipe() or generate_meal_plan_recipes() instead.",
                "fallback_to": "ai_generation"
            }

        # Normalize column names
        df = normalize_column_names(df)

        # Start with full dataset
        filtered = df.copy()

        # Filter by meal type
        if meal_type and 'meal_type' in filtered.columns:
            meal_type_lower = meal_type.lower()
            filtered = filtered[
                filtered['meal_type'].str.lower().str.contains(meal_type_lower, na=False)
            ]

        # Filter by calories
        if 'calories' in filtered.columns:
            if min_calories is not None:
                filtered = filtered[filtered['calories'] >= min_calories]
            if max_calories is not None:
                filtered = filtered[filtered['calories'] <= max_calories]

        # Filter by protein
        if 'protein_g' in filtered.columns:
            if min_protein_g is not None:
                filtered = filtered[filtered['protein_g'] >= min_protein_g]
            if max_protein_g is not None:
                filtered = filtered[filtered['protein_g'] <= max_protein_g]

        # Filter by carbs
        if 'carbs_g' in filtered.columns:
            if min_carbs_g is not None:
                filtered = filtered[filtered['carbs_g'] >= min_carbs_g]
            if max_carbs_g is not None:
                filtered = filtered[filtered['carbs_g'] <= max_carbs_g]

        # Filter by fat
        if 'fat_g' in filtered.columns:
            if min_fat_g is not None:
                filtered = filtered[filtered['fat_g'] >= min_fat_g]
            if max_fat_g is not None:
                filtered = filtered[filtered['fat_g'] <= max_fat_g]

        # Filter by dietary restrictions
        dietary_restrictions = dietary_restrictions or []
        if dietary_restrictions and 'tags' in filtered.columns:
            for restriction in dietary_restrictions:
                restriction_lower = restriction.lower().replace('_', ' ')
                filtered = filtered[
                    filtered['tags'].str.lower().str.contains(restriction_lower, na=False) |
                    filtered.get('name', pd.Series()).str.lower().str.contains(restriction_lower, na=False)
                ]

        # Filter out allergens
        exclude_allergens = exclude_allergens or []
        if exclude_allergens and 'ingredients' in filtered.columns:
            for allergen in exclude_allergens:
                allergen_lower = allergen.lower()
                filtered = filtered[
                    ~filtered['ingredients'].str.lower().str.contains(allergen_lower, na=False)
                ]

        # Filter out specific ingredients
        exclude_ingredients = exclude_ingredients or []
        if exclude_ingredients and 'ingredients' in filtered.columns:
            for ingredient in exclude_ingredients:
                ingredient_lower = ingredient.lower()
                filtered = filtered[
                    ~filtered['ingredients'].str.lower().str.contains(ingredient_lower, na=False)
                ]

        # Remove duplicates by name
        if 'name' in filtered.columns:
            filtered = filtered.drop_duplicates(subset=['name'])

        # Limit results
        filtered = filtered.head(max_results)

        # Convert to list of dicts
        recipes = []
        for _, row in filtered.iterrows():
            recipe = {
                "name": row.get('name', 'Unknown Recipe'),
                "calories": float(row.get('calories', 0)) if pd.notna(row.get('calories')) else 0,
                "protein_g": float(row.get('protein_g', 0)) if pd.notna(row.get('protein_g')) else 0,
                "fat_g": float(row.get('fat_g', 0)) if pd.notna(row.get('fat_g')) else 0,
                "carbs_g": float(row.get('carbs_g', 0)) if pd.notna(row.get('carbs_g')) else 0,
                "fiber_g": float(row.get('fiber_g', 0)) if pd.notna(row.get('fiber_g')) else 0,
                "source": "kaggle_dataset"
            }

            # Add optional fields if available
            if 'ingredients' in row and pd.notna(row['ingredients']):
                recipe['ingredients'] = str(row['ingredients'])
            if 'instructions' in row and pd.notna(row['instructions']):
                recipe['instructions'] = str(row['instructions'])
            if 'tags' in row and pd.notna(row['tags']):
                recipe['tags'] = str(row['tags'])
            if 'meal_type' in row and pd.notna(row['meal_type']):
                recipe['meal_type'] = str(row['meal_type'])

            recipes.append(recipe)

        if len(recipes) == 0:
            return {
                "status": "fallback",
                "message": "No recipes found in dataset matching criteria. Use AI generation.",
                "fallback_to": "ai_generation",
                "filters_applied": {
                    "meal_type": meal_type,
                    "calories": f"{min_calories}-{max_calories}" if min_calories or max_calories else "any",
                    "dietary_restrictions": dietary_restrictions,
                    "exclude_allergens": exclude_allergens
                }
            }

        return {
            "status": "success",
            "recipes": recipes,
            "count": len(recipes),
            "source": "kaggle_dataset",
            "message": f"Found {len(recipes)} recipes from Kaggle dataset",
            "total_in_dataset": len(df)
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error searching Kaggle dataset: {str(e)}",
            "fallback_to": "ai_generation"
        }


def create_meal_plan_from_kaggle(
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
    foods_to_avoid: Optional[List[str]] = None
) -> dict:
    """
    Create a complete meal plan using Kaggle recipe dataset.

    This replaces AI generation with real recipes from the dataset.
    Falls back to AI generation if dataset is not available.

    Args:
        tool_context: Tool context for session state
        num_days: Number of days for meal plan
        daily_calories: Daily calorie target
        daily_protein_g: Daily protein target
        daily_fat_g: Daily fat target
        daily_carbs_g: Daily carbs target
        meals_per_day: Number of main meals (default 3)
        snacks_per_day: Number of snacks (default 2)
        dietary_restrictions: Dietary restrictions
        exclude_allergens: Allergens to exclude
        foods_to_avoid: Specific foods to avoid

    Returns:
        Dictionary with meal plan or fallback instruction
    """
    try:
        # Check if dataset is available
        df = load_recipe_dataset()

        if df is None:
            return {
                "status": "fallback",
                "message": "Kaggle dataset not available. Use generate_meal_plan_recipes() with AI instead.",
                "fallback_to": "ai_generation"
            }

        # Calculate meal calorie distribution
        breakfast_cal = daily_calories * 0.25
        lunch_cal = daily_calories * 0.30
        dinner_cal = daily_calories * 0.30
        snack_cal = daily_calories * 0.15 / snacks_per_day if snacks_per_day > 0 else 0

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

        # Generate meals for each day
        for day in range(1, num_days + 1):
            day_meals = {
                "day": day,
                "meals": []
            }

            # Breakfast
            breakfast_result = search_kaggle_recipes(
                meal_type="breakfast",
                max_calories=breakfast_cal * 1.15,  # 15% tolerance
                min_calories=breakfast_cal * 0.85,
                dietary_restrictions=dietary_restrictions,
                exclude_allergens=exclude_allergens,
                exclude_ingredients=foods_to_avoid,
                max_results=5
            )

            if breakfast_result["status"] == "success" and breakfast_result["recipes"]:
                day_meals["meals"].append({
                    "meal_type": "breakfast",
                    "recipe": breakfast_result["recipes"][0]  # Take first match
                })

            # Lunch
            lunch_result = search_kaggle_recipes(
                meal_type="lunch",
                max_calories=lunch_cal * 1.15,
                min_calories=lunch_cal * 0.85,
                dietary_restrictions=dietary_restrictions,
                exclude_allergens=exclude_allergens,
                exclude_ingredients=foods_to_avoid,
                max_results=5
            )

            if lunch_result["status"] == "success" and lunch_result["recipes"]:
                day_meals["meals"].append({
                    "meal_type": "lunch",
                    "recipe": lunch_result["recipes"][0]
                })

            # Dinner
            dinner_result = search_kaggle_recipes(
                meal_type="dinner",
                max_calories=dinner_cal * 1.15,
                min_calories=dinner_cal * 0.85,
                dietary_restrictions=dietary_restrictions,
                exclude_allergens=exclude_allergens,
                exclude_ingredients=foods_to_avoid,
                max_results=5
            )

            if dinner_result["status"] == "success" and dinner_result["recipes"]:
                day_meals["meals"].append({
                    "meal_type": "dinner",
                    "recipe": dinner_result["recipes"][0]
                })

            # Snacks
            for snack_num in range(snacks_per_day):
                snack_result = search_kaggle_recipes(
                    meal_type="snack",
                    max_calories=snack_cal * 1.2,
                    min_calories=snack_cal * 0.8,
                    dietary_restrictions=dietary_restrictions,
                    exclude_allergens=exclude_allergens,
                    exclude_ingredients=foods_to_avoid,
                    max_results=5
                )

                if snack_result["status"] == "success" and snack_result["recipes"]:
                    day_meals["meals"].append({
                        "meal_type": f"snack_{snack_num + 1}",
                        "recipe": snack_result["recipes"][min(snack_num, len(snack_result["recipes"]) - 1)]
                    })

            meal_plan["days"].append(day_meals)

        # Auto-save to session
        tool_context.state["meal_plan"] = meal_plan

        return {
            "status": "success",
            "meal_plan": meal_plan,
            "source": "kaggle_dataset",
            "message": f"Created {num_days}-day meal plan from Kaggle recipe dataset"
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error creating meal plan from Kaggle dataset: {str(e)}",
            "fallback_to": "ai_generation"
        }
