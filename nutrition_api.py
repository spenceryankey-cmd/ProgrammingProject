# nutrition_api.py

import json
import os
import requests
from translation_map import TRANSLATIONS

# Cache file stored in the data folder
CACHE_FILE = "data/nutrition_cache.json"

def load_cache():
    """Loads the local nutrition cache if it exists."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Saves the current nutrition data to the local cache file."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_nutrition_data(item_name, app_id="4ab78244", app_key="
2c8f940dfe2ac77498fd8b586fe9dba9	"):
    """
    Fetches nutrition data from Edamam API, translating local dishes if necessary.
    Uses a local cache to avoid redundant API calls.
    """
    cache = load_cache()
    
    # Check cache first
    if item_name in cache:
        return cache[item_name]
        
    # Use translated query for local meals; default to original name
    query = TRANSLATIONS.get(item_name, item_name)
    
    url = "https://api.edamam.com/api/food-database/v2/parser"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "ingr": query
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data_json = response.json()
        
        parsed_food = data_json["parsed"][0]["food"]
        nutrients = parsed_food.get("nutrients", {})
        
        data = {
            "calories": round(nutrients.get("ENERC_KCAL", 0), 1),
            "protein": round(nutrients.get("PROCNT", 0), 1),
            "allergens": parsed_food.get("healthLabels", []) # Edamam returns diet/health labels here
        }
    except (IndexError, KeyError, requests.RequestException):
        # Fallback values if API fails, item isn't found, or keys are invalid
        data = {"calories": 0.0, "protein": 0.0, "allergens": []}

    # Save new data to cache
    cache[item_name] = data
    save_cache(cache)
    
    return data
