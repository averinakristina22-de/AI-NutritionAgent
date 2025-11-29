# Recipe Dataset Setup

## Download Instructions

1. **Install Kaggle CLI** (if not already installed):
   ```bash
   pip install kaggle
   ```

2. **Setup Kaggle API credentials**:
   - Go to https://www.kaggle.com/settings
   - Click "Create New API Token"
   - This downloads `kaggle.json`
   - Place it in: `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\Users\<Username>\.kaggle\kaggle.json` (Windows)

3. **Download the dataset**:
   ```bash
   cd nutrition-agent/data
   kaggle datasets download thedevastator/better-recipes-for-a-better-life
   unzip better-recipes-for-a-better-life.zip
   ```

## Alternative: Manual Download

1. Go to: https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life
2. Click "Download"
3. Extract the ZIP file to this directory

## Expected Files

After extraction, you should have:
- `recipes.csv` (or similar)
- Contains: recipe names, ingredients, nutrition info (calories, protein, fat, carbs)

The tool will automatically load this data when available.
