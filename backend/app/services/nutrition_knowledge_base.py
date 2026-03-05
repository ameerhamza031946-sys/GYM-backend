import os
import json

# Force stable keyword-based search for hackathon environment robustness
# In a full production setup, this would use ChromaDB vector search.

NUTRITION_DATA = [
    {
        "id": "bulk_01",
        "goal": "build_muscle",
        "meal_name": "Massive Protein Oatmeal",
        "description": "700 kcal, 45g protein. 1 cup oats, 2 tbsp peanut butter, 1 scoop whey, 1 banana, whole milk.",
        "tags": ["bulking", "high_protein", "breakfast"]
    },
    {
        "id": "cut_01",
        "goal": "lose_weight",
        "meal_name": "Zucchini Turkey Pasta",
        "description": "350 kcal, 40g protein. 250g zucchini noodles, 150g lean ground turkey, sugar-free marinara, spinach.",
        "tags": ["cutting", "low_carb", "high_volume"]
    },
    {
        "id": "keto_01",
        "goal": "keto",
        "meal_name": "Avocado & Bacon Omelet",
        "description": "450 kcal, 25g protein, 35g fat, 5g net carbs. 3 eggs, 2 slices bacon, half avocado, feta cheese.",
        "tags": ["keto", "low_carb", "high_fat"]
    },
    {
        "id": "vegan_01",
        "goal": "vegan",
        "meal_name": "Quinoa Power Bowl",
        "description": "480 kcal, 22g protein. 1 cup quinoa, black beans, kale, nutritional yeast, tahini dressing.",
        "tags": ["vegan", "plant_based", "balanced"]
    },
    {
        "id": "chipotle_lifestyle",
        "goal": "balanced",
        "meal_name": "Chipotle Chicken Lifestyle Bowl",
        "description": "480 kcal, 42g protein. No rice, double chicken, black beans, fajita veggies, fresh tomato salsa.",
        "tags": ["fast_food", "balanced", "high_protein"]
    }
]

def search_nutrition_kb(query: str, limit: int = 2):
    """
    Simulates a RAG retrieval system using keyword matching on nutritional metadata.
    Designed for reliability during hackathon demos.
    """
    q_lower = query.lower()
    matches = []
    
    for item in NUTRITION_DATA:
        score = 0
        search_text = f"{item['meal_name']} {item['goal']} {' '.join(item['tags'])} {item['description']}".lower()
        
        # Simple keyword scoring
        for word in q_lower.split():
            if word in search_text:
                score += 1
        
        if score > 0:
            matches.append((item, score))
    
    # Sort by score and return top results
    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches[:limit]]

def get_context_for_prompt(query: str):
    """Formats retrieved data for LLM inclusion."""
    results = search_nutrition_kb(query)
    if not results:
        return "No specific meal data found in the knowledge base."
    
    context = "RELEVANT MEALS FROM KNOWLEDGE BASE:\n"
    for item in results:
        context += f"- {item['meal_name']}: {item['description']} (Goal: {item['goal']})\n"
    return context
