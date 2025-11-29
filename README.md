# Nutrition Agent v3.0 - Clean Version

## Overview
Clean, production-ready version of the AI-powered nutrition consultation agent built with Google's Agent Development Kit (ADK) and Gemini AI.

## What's New in v3.0

### ✨ Key Features
- **Real Recipe Integration**: Uses Kaggle "Better Recipes for a Better Life" dataset (1.6MB, thousands of real recipes)
- **Nutritional Data Parsing**: Fixed nutrition list parsing to extract calories, protein, fat, carbs correctly
- **Unified Tools**: Streamlined from 11 tools to 10 essential tools
- **Edge Case Validation**: Detects dietary contradictions before processing
- **Auto-Save Session State**: All calculations and meal plans saved automatically

### 🔧 Fixed Issues (from v2.x)
- ✅ Nutrition data parsing from Kaggle dataset (list format → separate columns)
- ✅ Removed dead code and legacy agent files
- ✅ Fixed import errors and cleaned up dependencies
- ✅ API key loading order corrected

## Project Structure

```
nutrition-agent 3.0/
├── main.py                          # Entry point
├── .env                             # API key configuration
├── config.yaml                      # Agent configuration
├── requirements.txt                 # Python dependencies
│
├── agents/
│   ├── __init__.py
│   └── unified_consultation_agent.py   # Main consultation agent (Gemini 2.0 Flash)
│
├── tools/
│   ├── __init__.py
│   ├── data_collection_tool.py         # User profile collection
│   ├── kbju_calculator.py              # KBJU/TDEE calculations
│   ├── validation_tool.py              # Edge case & contradiction detection
│   ├── session_data_tool.py            # Unified session retrieval
│   ├── kaggle_recipe_tool.py           # Real recipe search from dataset
│   ├── recipe_generator_tool.py        # AI recipe generation (fallback)
│   ├── meal_plan_tool.py               # Meal plan storage & breakdown
│   └── nutrition_db_tool.py            # Nutrition database search
│
├── services/
│   ├── __init__.py
│   ├── session_service.py              # Session management
│   └── memory_bank.py                  # Persistent memory
│
└── data/
    ├── recipes.csv                     # Kaggle recipe dataset (1.6MB)
    └── README.md                       # Dataset information
```

## Agent Tools (10 Total)

1. **save_user_profile_data** - Collects user information (age, weight, goals, restrictions)
2. **calculate_kbju** - Calculates daily calorie and macro needs
3. **validate_consultation_data** - Checks for contradictions and impossible requirements
4. **get_session_data** - Unified retrieval of profile, KBJU, and meal plans
5. **search_kaggle_recipes** - Searches real recipes from Kaggle dataset
6. **create_meal_plan_from_kaggle** - Creates meal plans using real recipes
7. **generate_custom_recipe** - AI-generated custom recipes (fallback)
8. **generate_meal_plan_recipes** - AI-generated meal plans (fallback)
9. **get_meal_nutrition_breakdown** - Returns per-meal nutritional breakdown
10. **search_nutrition_db** - Searches USDA nutrition database (not yet implemented)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Edit `.env` file and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run the Agent
```bash
python main.py
```

## Usage Example

```
User: Hi, I want to lose weight
Agent: [Collects profile data: age, weight, height, activity, goals]

User: I'm 30, 80kg, 175cm, moderate activity, want to lose weight
Agent: [Calculates KBJU: 1800 cal, 135g protein, 60g fat, 180g carbs]

User: Create a 3-day meal plan, I'm vegetarian
Agent: [Searches Kaggle dataset for vegetarian recipes]
Agent: [Creates meal plan with real recipes matching macros]

User: How much protein in each meal?
Agent: [Returns detailed breakdown per meal]
```

## Dataset Information

**Source**: [Better Recipes for a Better Life (Kaggle)](https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life)

**Size**: 1.6MB (thousands of recipes)

**Nutrition Format**: List format `[calories, fat, sugar, sodium, protein, saturated_fat, carbs]`
- **v3.0 Fix**: Parses list correctly into separate columns

**Fallback**: If dataset unavailable, agent uses AI generation

## Technical Details

### Models Used
- **Main Agent**: Gemini 2.0 Flash Experimental
- **Recipe Generation**: Gemini 2.5 Flash Lite (fallback)

### Session Management
- Uses ADK's SessionService for persistent state
- SQLite database: `nutrition_memory.db`
- Auto-saves all calculations and meal plans

### Retry Configuration
All API calls use retry logic:
- Max attempts: 5
- Exponential backoff: base 7
- Handles: 429, 500, 503, 504 errors

## What's NOT Included (vs. old version)

❌ Test files (test_*.py)
❌ Debug scripts (inspect_dataset.py, fix_kaggle_tool.py)
❌ Setup scripts (setup_kaggle_dataset.sh/bat)
❌ Documentation files (CLEANUP_SUMMARY.md, IMPORT_FIX.md, etc.)
❌ Legacy agent files (analysis_agent.py, interview_agent.py, etc.)
❌ __pycache__ directories
❌ Old database files

## Version History

- **v3.0** (Nov 24, 2024) - Fixed Kaggle nutrition parsing + clean version
- **v2.3** (Nov 24, 2024) - Removed dead code
- **v2.2** (Nov 24, 2024) - Kaggle dataset integration
- **v2.1** (Nov 24, 2024) - Tool reduction (11 → 7)
- **v2.0** (Nov 23, 2024) - Unified consultation agent
- **v1.0** (Nov 23, 2024) - Multi-agent architecture (deprecated)

## License

Educational project for Kaggle 5-day AI Agents course.

## Support

For issues or questions, refer to the Google ADK documentation or Kaggle course materials.
