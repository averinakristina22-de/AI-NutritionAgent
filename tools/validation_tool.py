"""
Validation Tool - Checks for contradictions and logical issues before processing

This tool proactively identifies problems like:
- Conflicting dietary preferences (vegetarian + wants beef)
- Impossible nutritional targets
- Missing required data
- Logical inconsistencies

The agent should call this BEFORE attempting recipe generation or meal planning.
"""

from typing import Optional, List


def validate_consultation_data(
    dietary_restrictions: Optional[List[str]] = None,
    foods_to_avoid: Optional[List[str]] = None,
    favorite_foods: Optional[List[str]] = None,
    target_calories: Optional[float] = None,
    target_protein_g: Optional[float] = None,
    target_fat_g: Optional[float] = None,
    target_carbs_g: Optional[float] = None,
    weight_kg: Optional[float] = None,
    goal: Optional[str] = None
) -> dict:
    """
    Validate consultation data for contradictions and logical issues.

    This catches problems early before wasting API calls on impossible requests.

    Args:
        dietary_restrictions: User's dietary restrictions (e.g., ["vegetarian", "vegan"])
        foods_to_avoid: Foods user wants to avoid
        favorite_foods: User's favorite foods
        target_calories: Daily calorie target
        target_protein_g: Daily protein target (grams)
        target_fat_g: Daily fat target (grams)
        target_carbs_g: Daily carbs target (grams)
        weight_kg: User's weight in kg
        goal: User's goal (weight_loss, muscle_gain, etc.)

    Returns:
        Dictionary with validation results:
        Success (no issues): {
            "status": "success",
            "valid": True,
            "message": "All data is consistent"
        }
        Warnings (potential issues): {
            "status": "warning",
            "valid": True,
            "warnings": [...],
            "suggestions": [...],
            "message": "Found potential issues"
        }
        Errors (critical contradictions): {
            "status": "error",
            "valid": False,
            "errors": [...],
            "suggested_resolution": str,
            "message": "Found contradictions that must be resolved"
        }
    """
    errors = []
    warnings = []
    suggestions = []

    # Define dietary restriction rules
    MEAT_FOODS = ["beef", "pork", "chicken", "turkey", "lamb", "duck", "venison", "meat"]
    ANIMAL_PRODUCTS = MEAT_FOODS + ["eggs", "dairy", "milk", "cheese", "yogurt", "butter", "honey"]
    SEAFOOD = ["fish", "salmon", "tuna", "shrimp", "shellfish", "lobster", "crab", "seafood"]
    GLUTEN_FOODS = ["wheat", "bread", "pasta", "flour", "barley", "rye", "gluten"]
    DAIRY_FOODS = ["milk", "cheese", "yogurt", "butter", "cream", "dairy"]

    dietary_restrictions = [d.lower() for d in (dietary_restrictions or [])]
    foods_to_avoid = [f.lower() for f in (foods_to_avoid or [])]
    favorite_foods = [f.lower() for f in (favorite_foods or [])]

    # ============================================================================
    # 1. CHECK DIETARY RESTRICTION CONTRADICTIONS
    # ============================================================================

    # Vegetarian contradictions
    if "vegetarian" in dietary_restrictions:
        # Check favorite foods
        conflicting_favorites = [f for f in favorite_foods if any(meat in f for meat in MEAT_FOODS)]
        if conflicting_favorites:
            errors.append({
                "type": "dietary_contradiction",
                "severity": "high",
                "issue": f"User is vegetarian but lists meat as favorites: {', '.join(conflicting_favorites)}",
                "resolution": "Ask user to clarify: Do you want vegetarian recipes, or would you like to include meat?"
            })

        # Pescatarian suggestion if they like seafood
        seafood_favorites = [f for f in favorite_foods if any(fish in f for fish in SEAFOOD)]
        if seafood_favorites:
            suggestions.append(f"User likes seafood ({', '.join(seafood_favorites)}) - consider asking if they're pescatarian instead of vegetarian")

    # Vegan contradictions
    if "vegan" in dietary_restrictions:
        # Check favorite foods
        conflicting_favorites = [f for f in favorite_foods if any(animal in f for animal in ANIMAL_PRODUCTS)]
        if conflicting_favorites:
            errors.append({
                "type": "dietary_contradiction",
                "severity": "critical",
                "issue": f"User is vegan but lists animal products as favorites: {', '.join(conflicting_favorites)}",
                "resolution": "Ask user: Do you want strictly vegan recipes, or are you flexible with some animal products?"
            })

        # Vegan includes vegetarian
        if "vegetarian" not in dietary_restrictions:
            suggestions.append("User is vegan - automatically including vegetarian as well since vegan is more restrictive")

    # Gluten-free contradictions
    if "gluten_free" in dietary_restrictions or "gluten-free" in dietary_restrictions:
        conflicting_favorites = [f for f in favorite_foods if any(gluten in f for gluten in GLUTEN_FOODS)]
        if conflicting_favorites:
            warnings.append({
                "type": "dietary_warning",
                "severity": "medium",
                "issue": f"User is gluten-free but lists gluten-containing foods as favorites: {', '.join(conflicting_favorites)}",
                "resolution": "Offer gluten-free alternatives to their favorite foods"
            })

    # Lactose intolerant / dairy-free contradictions
    if "lactose_intolerant" in dietary_restrictions or "dairy_free" in dietary_restrictions:
        conflicting_favorites = [f for f in favorite_foods if any(dairy in f for dairy in DAIRY_FOODS)]
        if conflicting_favorites:
            warnings.append({
                "type": "dietary_warning",
                "severity": "medium",
                "issue": f"User is lactose intolerant/dairy-free but lists dairy as favorites: {', '.join(conflicting_favorites)}",
                "resolution": "Suggest lactose-free or dairy-free alternatives"
            })

    # ============================================================================
    # 2. CHECK MACRO TARGET VALIDITY
    # ============================================================================

    if target_calories and target_protein_g and target_fat_g and target_carbs_g:
        # Calculate calories from macros
        protein_cal = target_protein_g * 4
        fat_cal = target_fat_g * 9
        carbs_cal = target_carbs_g * 4
        total_macro_cal = protein_cal + fat_cal + carbs_cal

        # Check if macros match target calories (±10% tolerance)
        calorie_difference = abs(total_macro_cal - target_calories)
        if calorie_difference > target_calories * 0.10:
            errors.append({
                "type": "macro_mismatch",
                "severity": "high",
                "issue": f"Macro calories ({total_macro_cal:.0f}) don't match target calories ({target_calories:.0f})",
                "resolution": f"Adjust macros to match calorie target. Difference: {calorie_difference:.0f} calories"
            })

        # Check protein is reasonable (1.6-2.5g per kg is typical range)
        if weight_kg:
            protein_per_kg = target_protein_g / weight_kg
            if protein_per_kg < 0.8:
                warnings.append({
                    "type": "low_protein",
                    "severity": "medium",
                    "issue": f"Protein target is very low ({protein_per_kg:.1f}g/kg). Minimum recommended: 0.8g/kg",
                    "resolution": "Consider increasing protein to at least 0.8g per kg body weight"
                })
            elif protein_per_kg > 3.0:
                warnings.append({
                    "type": "high_protein",
                    "severity": "medium",
                    "issue": f"Protein target is very high ({protein_per_kg:.1f}g/kg). Typical range: 1.6-2.5g/kg",
                    "resolution": "Verify this protein level is intentional and safe for the user"
                })

        # Check if vegan/vegetarian with very high protein targets
        if ("vegan" in dietary_restrictions or "vegetarian" in dietary_restrictions):
            if target_protein_g > 150:
                warnings.append({
                    "type": "difficult_target",
                    "severity": "medium",
                    "issue": f"Very high protein target ({target_protein_g}g) with vegan/vegetarian diet may be challenging",
                    "resolution": "May need protein supplements or extensive legume/tofu consumption"
                })

    # ============================================================================
    # 3. CHECK GOAL CONSISTENCY
    # ============================================================================

    if goal and target_calories and weight_kg:
        # Rough estimates for goal validation
        if goal == "weight_loss":
            if target_calories > weight_kg * 30:  # Very rough upper bound
                warnings.append({
                    "type": "goal_mismatch",
                    "severity": "low",
                    "issue": f"Weight loss goal but calories ({target_calories}) seem high for weight ({weight_kg}kg)",
                    "resolution": "Verify the calorie target matches the weight loss goal"
                })

        elif goal == "muscle_gain":
            if target_calories < weight_kg * 25:  # Very rough lower bound
                warnings.append({
                    "type": "goal_mismatch",
                    "severity": "low",
                    "issue": f"Muscle gain goal but calories ({target_calories}) may be too low",
                    "resolution": "Consider increasing calories for muscle growth"
                })

    # ============================================================================
    # 4. CHECK FOR CONFLICTING RESTRICTIONS
    # ============================================================================

    # Check if too many restrictions make meal planning impossible
    restriction_count = len(dietary_restrictions)
    avoid_count = len(foods_to_avoid)

    if restriction_count >= 4:
        warnings.append({
            "type": "too_restrictive",
            "severity": "medium",
            "issue": f"User has many dietary restrictions ({restriction_count}) which may limit recipe variety",
            "resolution": "Consider prioritizing the most important restrictions if recipe options are limited"
        })

    if avoid_count >= 10:
        warnings.append({
            "type": "too_many_avoided_foods",
            "severity": "medium",
            "issue": f"User avoids many foods ({avoid_count}) which may make meal planning difficult",
            "resolution": "Focus on core allergens/dislikes; consider if all are strictly necessary"
        })

    # ============================================================================
    # COMPILE RESULTS
    # ============================================================================

    if errors:
        # Critical contradictions found
        error_messages = [e["issue"] for e in errors]
        resolutions = [e["resolution"] for e in errors]

        return {
            "status": "error",
            "valid": False,
            "errors": errors,
            "error_count": len(errors),
            "suggested_resolution": " OR ".join(resolutions[:2]),  # Top 2 resolutions
            "message": f"Found {len(errors)} critical contradiction(s): {'; '.join(error_messages[:2])}"
        }

    elif warnings:
        # Potential issues, but not blocking
        warning_messages = [w["issue"] for w in warnings]

        result = {
            "status": "warning",
            "valid": True,
            "warnings": warnings,
            "warning_count": len(warnings),
            "message": f"Found {len(warnings)} potential issue(s) that should be reviewed"
        }

        if suggestions:
            result["suggestions"] = suggestions

        return result

    else:
        # All clear
        result = {
            "status": "success",
            "valid": True,
            "message": "All data is consistent - no contradictions found"
        }

        if suggestions:
            result["suggestions"] = suggestions

        return result
