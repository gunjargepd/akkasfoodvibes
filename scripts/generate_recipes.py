import os
import sys
import json
import random
import re
import time
from datetime import datetime
import google.generativeai as genai

# Setup Category Images from Unsplash (Premium & High-Res)
CATEGORY_IMAGES = {
    "Breakfast": [
        "https://images.unsplash.com/photo-1528207776546-365bb710ee93?auto=format&fit=crop&w=800&q=80", # Waffles
        "https://images.unsplash.com/photo-1541532713592-79a0317b6b77?auto=format&fit=crop&w=800&q=80", # Avocado Toast
        "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?auto=format&fit=crop&w=800&q=80", # Healthy Bowl
        "https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?auto=format&fit=crop&w=800&q=80"  # Pancakes
    ],
    "Lunch": [
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80", # Salad Bowl
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80", # Healthy Plate
        "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80", # Breakfast/Lunch Wrap
        "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=800&q=80"  # Gourmet Veggies
    ],
    "Dinner": [
        "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80", # Steak
        "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80", # Gourmet Fish
        "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80", # Pasta
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80"  # Pizza
    ],
    "Dessert": [
        "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80", # Chocolate Cake
        "https://images.unsplash.com/photo-1524351199679-46cddf530c04?auto=format&fit=crop&w=800&q=80", # Cheesecake
        "https://images.unsplash.com/photo-1551024601-bec78aea704b?auto=format&fit=crop&w=800&q=80", # Donuts
        "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?auto=format&fit=crop&w=800&q=80"  # Cupcakes
    ],
    "Snack": [
        "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=800&q=80", # Cookies
        "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=800&q=80", # Nut Mix
        "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80", # Samosa
        "https://images.unsplash.com/photo-1541832676-9b763b0239ab?auto=format&fit=crop&w=800&q=80"  # Roasted Seeds
    ]
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80"

CUISINES = ["Mumbai Special", "Puneri Thali", "Kolhapuri Tadka", "Konkani Coastal", "Malvani Cuisine", "Vidarbha Spicy Special", "Khandeshi Style"]
CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"]

MAHARASHTRIAN_DISHES = [
    "Misal Pav", "Vada Pav", "Puran Poli", "Pav Bhaji", "Kanda Poha", "Sabudana Khichdi", 
    "Kothimbir Vadi", "Thalipeeth", "Pitla Bhakri", "Aluchi Vadi", "Batata Vada", "Katachi Amti", 
    "Shev Bhaji", "Bharli Vangi", "Solkadhi", "Modak", "Shrikhand", "Basundi", "Karanji"
]

def to_iso_duration(minutes):
    if not minutes:
        return "PT0M"
    hours = minutes // 60
    mins = minutes % 60
    duration = "PT"
    if hours > 0:
        duration += f"{hours}H"
    if mins > 0:
        duration += f"{mins}M"
    return duration

def sanitize_filename(title):
    filename = title.lower().strip()
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[\s_-]+', '-', filename)
    return filename + ".html"

def generate_recipe_data(cuisine, category):
    famous_dish = random.choice(MAHARASHTRIAN_DISHES)
    prompt = f"""
    Create a highly detailed, professional, and attractive culinary recipe for a traditional Maharashtrian delicacy.
    The recipe must be based on or inspired by '{famous_dish}' and prepared in a '{cuisine}' style, categorized as '{category}'.
    
    IMPORTANT - MULTILINGUAL REQUIREMENT:
    The target audience understands both English and Hindi. Therefore:
    - The 'title' must be a catchy, premium English title (e.g., "Authentic Kolhapuri Misal Pav" or "Gourmet Puran Poli with Cardamom Ghee").
    - The 'description' MUST contain two versions side-by-side or line-by-line: first in English, followed by a clear, natural translation in Hindi (e.g. "An iconic, spicy sprouted moth bean curry... / यह एक पारंपरिक, तीखा और स्वादिष्ट कोल्हापुरी मिसल पाव है...").
    - Each item in the 'ingredients' array MUST be bilingual, listing the ingredient in English and Hindi (e.g., "2 cups sprouted moth beans / २ कप अंकुरित मटकी", "1 tsp mustard seeds / १ छोटा चम्मच राई").
    - For each instruction step in 'instructions':
      - The 'title' should be in English (e.g., "Prepare the Kat (Spicy Gravy)").
      - The 'text' MUST contain the step details in English, followed by the translation in clear, natural Hindi (e.g. "Heat 2 tbsp oil in a pan and add mustard seeds. / एक पैन में २ चम्मच तेल गर्म करें और राई डालें।").
      
    Make sure the Hindi is natural and written in Devanagari script.
    
    You MUST respond with a single, valid JSON object strictly matching this schema:
    {{
      "title": " Catchy English title",
      "description": "Engaging description in both English & Hindi",
      "prepTime": 15, // Integer representing prep time in minutes
      "cookTime": 30, // Integer representing cooking time in minutes
      "yield": "4 servings", // String representing the yield
      "difficulty": "Medium", // "Easy", "Medium", or "Hard"
      "category": "{category}",
      "keywords": "comma-separated, SEO-optimized keywords",
      "ingredients": [
        "ingredient 1 in English / ingredient 1 in Hindi",
        "ingredient 2 in English / ingredient 2 in Hindi"
      ],
      "instructions": [
        {{
          "title": "Step 1 Title in English",
          "text": "Step 1 text in English. / स्टेप १ का विवरण हिंदी में।"
        }},
        {{
          "title": "Step 2 Title in English",
          "text": "Step 2 text in English. / स्टेप २ का विवरण हिंदी में।"
        }}
      ],
      "nutrition": {{
        "calories": 350,
        "fat": 12,
        "protein": 8,
        "carbs": 45
      }}
    }}
    """
    
    # Run Gemini API Call
    model = genai.GenerativeModel("gemini-2.5-flash")
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        data["cuisine"] = cuisine
        return data
    except Exception as e:
        print(f"Gemini API Error (likely Quota Exceeded): {e}")
        return None

def build_feed_xml(recipes):
    rss_items = []
    for r in recipes[:15]: # Last 15 recipes in RSS
        url = f"https://akkasfoodvibes.github.io/{r['fileName']}"
        date_parsed = datetime.strptime(r['date'], "%Y-%m-%d")
        pub_date = date_parsed.strftime("%a, %d %b %Y 00:00:00 +0000")
        
        rss_items.append(f"""    <item>
      <title><![CDATA[{r['title']}]]></title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{pub_date}</pubDate>
      <category><![CDATA[{r['category']}]]></category>
      <description><![CDATA[{r['description']}]]></description>
      <content:encoded><![CDATA[
        <img src="{r['imageUrl']}" alt="{r['title']}" style="max-width:100%; height:auto; margin-bottom:15px;"/>
        <p>{r['description']}</p>
        <p><a href="{url}" style="font-weight: bold; color: #E05A47;">Read the full recipe instructions and ingredients on AkkasFoodVibes &rarr;</a></p>
      ]]></content:encoded>
    </item>""")
        
    rss_items_joined = "\n".join(rss_items)
    xml_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>AkkasFoodVibes | Fresh Delicious Recipes Everyday</title>
    <link>https://akkasfoodvibes.github.io</link>
    <description>Discover gourmet recipes generated daily. Learn to cook professional dishes with easy, step-by-step instructions. Optimized for Google News.</description>
    <language>en-us</language>
    <lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
    <atom:link href="https://akkasfoodvibes.github.io/feed.xml" rel="self" type="application/rss+xml" />
{rss_items_joined}
  </channel>
</rss>"""
    return xml_content

def build_sitemap_xml(recipes):
    sitemap_items = ["""  <url>
    <loc>https://akkasfoodvibes.github.io/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""]
    
    for r in recipes:
        url = f"https://akkasfoodvibes.github.io/{r['fileName']}"
        sitemap_items.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{r['date']}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
        
    sitemap_items_joined = "\n".join(sitemap_items)
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_items_joined}
</urlset>"""
    return xml_content

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("CRITICAL ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
        
    genai.configure(api_key=api_key)
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    
    template_path = os.path.join(root_dir, "recipe-template.html")
    recipes_db_path = os.path.join(root_dir, "recipes.json")
    
    # Load Template
    if not os.path.exists(template_path):
        print(f"CRITICAL ERROR: Template file {template_path} does not exist.")
        sys.exit(1)
        
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()
        
    # Load existing database
    existing_recipes = []
    if os.path.exists(recipes_db_path):
        try:
            with open(recipes_db_path, "r", encoding="utf-8") as f:
                existing_recipes = json.load(f)
        except Exception as e:
            print(f"Warning: Could not parse existing recipes.json: {e}. Starting fresh.")
            existing_recipes = []

    today_str = datetime.today().strftime("%Y-%m-%d")
    
    # Pick 1 unique combination of cuisine and category
    selected_combos = []
    while len(selected_combos) < 1:
        cui = random.choice(CUISINES)
        cat = random.choice(CATEGORIES)
        combo = (cui, cat)
        if combo not in selected_combos:
            selected_combos.append(combo)
            
    print(f"Generating 1 new recipe for {today_str}...")
    new_recipes = []
    
    # Ensure recipes output folder exists
    os.makedirs(os.path.join(root_dir, "recipes"), exist_ok=True)
    
    for idx, (cuisine, category) in enumerate(selected_combos, 1):
        if idx > 1:
            print("Waiting 15 seconds to avoid API rate limits...")
            time.sleep(15)
        print(f"Recipe {idx}/1: Generating {cuisine} {category}...")
        recipe_data = generate_recipe_data(cuisine, category)
        
        if not recipe_data:
            print(f"Skipping recipe {idx} due to generation error.")
            continue
            
        # Complete recipe properties
        recipe_id = f"{today_str}-{idx}"
        filename = "recipes/" + sanitize_filename(recipe_data["title"])
        
        # Select image based on keywords in the recipe title
        title_lower = recipe_data["title"].lower()
        KEYWORD_IMAGES = {
            "idli": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80",
            "dosa": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80",
            "misal": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?auto=format&fit=crop&w=800&q=80",
            "pav bhaji": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?auto=format&fit=crop&w=800&q=80",
            "vada pav": "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?auto=format&fit=crop&w=800&q=80",
            "batata vada": "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?auto=format&fit=crop&w=800&q=80",
            "samosa": "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?auto=format&fit=crop&w=800&q=80",
            "biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80",
            "pulao": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80",
            "rice": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80",
            "kheer": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
            "basundi": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
            "shrikhand": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
            "vadi": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
            "sweet": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
            "dessert": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
            "modak": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
            "puri": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=800&q=80",
            "poori": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=800&q=80",
            "chole": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=800&q=80",
            "bhature": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?auto=format&fit=crop&w=800&q=80",
            "paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80",
            "dal": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80",
            "curry": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=800&q=80",
            "pitla": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=800&q=80",
            "gravy": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=800&q=80",
            "solkadhi": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
            "chai": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
            "tea": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
            "coffee": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80",
            "papad": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?auto=format&fit=crop&w=800&q=80",
            "roti": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?auto=format&fit=crop&w=800&q=80",
            "naan": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?auto=format&fit=crop&w=800&q=80",
            "flatbread": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?auto=format&fit=crop&w=800&q=80",
            "paratha": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?auto=format&fit=crop&w=800&q=80",
            "bhakri": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?auto=format&fit=crop&w=800&q=80",
            "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
            "chicken": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80",
            "mutton": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80"
        }
        
        image_url = None
        for kw, img in KEYWORD_IMAGES.items():
            if kw in title_lower:
                image_url = img
                break
                
        if not image_url:
            images = CATEGORY_IMAGES.get(category, [DEFAULT_IMAGE])
            image_url = random.choice(images)
        
        recipe_data["id"] = recipe_id
        recipe_data["fileName"] = filename
        recipe_data["imageUrl"] = image_url
        recipe_data["date"] = today_str
        
        new_recipes.append(recipe_data)
        
    if not new_recipes:
        print("ERROR: No recipes were successfully generated today.")
        sys.exit(1)
        
    # Write new HTML files & build content placeholders
    for r in new_recipes:
        # Build ingredients list HTML
        ingredients_html = ""
        for ing in r["ingredients"]:
            ingredients_html += f'<li class="ingredient-item"><input type="checkbox"> <span>{ing}</span></li>\n'
            
        # Build instructions steps HTML
        instructions_html = ""
        for i, step in enumerate(r["instructions"], 1):
            instructions_html += f"""
        <div class="step-card">
          <div class="step-num">{i:02d}</div>
          <div class="step-content">
            <h3>{step["title"]}</h3>
            <p>{step["text"]}</p>
          </div>
        </div>\n"""
        
        # Build Schema JSON-LD
        schema_steps = []
        for step in r["instructions"]:
            schema_steps.append({
                "@type": "HowToStep",
                "text": step["text"]
            })
            
        schema_dict = {
          "@context": "https://schema.org/",
          "@type": "Recipe",
          "name": r["title"],
          "image": [r["imageUrl"]],
          "author": {
            "@type": "Organization",
            "name": "AkkasFoodVibes"
          },
          "datePublished": r["date"],
          "description": r["description"],
          "prepTime": to_iso_duration(r["prepTime"]),
          "cookTime": to_iso_duration(r["cookTime"]),
          "totalTime": to_iso_duration(r["prepTime"] + r["cookTime"]),
          "recipeYield": r["yield"],
          "recipeCategory": r["category"],
          "recipeCuisine": r["cuisine"],
          "keywords": r["keywords"],
          "recipeIngredient": r["ingredients"],
          "recipeInstructions": schema_steps,
          "nutrition": {
            "@type": "NutritionInformation",
            "calories": f"{r['nutrition']['calories']} calories",
            "fatContent": f"{r['nutrition']['fat']} grams fat",
            "proteinContent": f"{r['nutrition']['protein']} grams protein",
            "carbohydratesContent": f"{r['nutrition']['carbs']} grams carbs"
          }
        }
        
        schema_json = json.dumps(schema_dict, indent=2)
        
        # Replace tokens in template
        page_html = html_template
        page_html = page_html.replace("{{TITLE}}", r["title"])
        page_html = page_html.replace("{{DESCRIPTION}}", r["description"])
        page_html = page_html.replace("{{KEYWORDS}}", r["keywords"])
        page_html = page_html.replace("{{FILE_NAME}}", r["fileName"])
        page_html = page_html.replace("{{CATEGORY}}", r["category"])
        page_html = page_html.replace("{{PREP_TIME}}", str(r["prepTime"]))
        page_html = page_html.replace("{{COOK_TIME}}", str(r["cookTime"]))
        page_html = page_html.replace("{{YIELD}}", r["yield"])
        page_html = page_html.replace("{{DIFFICULTY}}", r["difficulty"])
        page_html = page_html.replace("{{IMAGE_URL}}", r["imageUrl"])
        page_html = page_html.replace("{{DATE}}", r["date"])
        page_html = page_html.replace("{{INGREDIENTS_LIST}}", ingredients_html)
        page_html = page_html.replace("{{INSTRUCTIONS_STEPS}}", instructions_html)
        page_html = page_html.replace("{{CALORIES}}", str(r["nutrition"]["calories"]))
        page_html = page_html.replace("{{FAT}}", str(r["nutrition"]["fat"]))
        page_html = page_html.replace("{{PROTEIN}}", str(r["nutrition"]["protein"]))
        page_html = page_html.replace("{{CARBS}}", str(r["nutrition"]["carbs"]))
        page_html = page_html.replace("{{SCHEMA_JSON_LD}}", schema_json)
        
        # Write to file
        file_dest = os.path.join(root_dir, r["fileName"])
        with open(file_dest, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Created recipe page: {r['fileName']}")
        
    # Append new recipes to database
    all_recipes = new_recipes + existing_recipes
    
    # Save recipes.json
    with open(recipes_db_path, "w", encoding="utf-8") as f:
        json.dump(all_recipes, f, indent=2, ensure_ascii=False)
    print("Updated recipes.json")
    
    # Save sitemap.xml
    sitemap_xml = build_sitemap_xml(all_recipes)
    sitemap_path = os.path.join(root_dir, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print("Updated sitemap.xml")
    
    # Save feed.xml
    feed_xml = build_feed_xml(all_recipes)
    feed_path = os.path.join(root_dir, "feed.xml")
    with open(feed_path, "w", encoding="utf-8") as f:
        f.write(feed_xml)
    print("Updated feed.xml (RSS Feed)")
    
    print("Successfully completed generation cycle!")

if __name__ == "__main__":
    main()
