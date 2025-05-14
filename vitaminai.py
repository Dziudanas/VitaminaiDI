# LINKU NUSKAITYMAS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup Chrome headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# Open the page
url = "https://ods.od.nih.gov/factsheets/list-VitaminsMinerals/"
driver.get(url)
time.sleep(3)  # Wait for JS to load

# Get page source after JS is rendered
html = driver.page_source
driver.quit()

# Parse with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

vitamin_names = []
vitamin_links = []

# Find all relevant list items
for li in soup.select('li.category.has-internal-resources'):
    a_tag = li.find('a', class_='handle')
    data_category = li.get("data-resource-category")
    
    if a_tag and data_category:
        name = a_tag.get_text(strip=True).replace('\xa0', ' ')
        formatted_category = ''.join(part.capitalize() for part in data_category.split('-'))
        link = f"https://ods.od.nih.gov/factsheets/{formatted_category}-HealthProfessional/"
        vitamin_names.append(name)
        vitamin_links.append(link)

# Save to Excel
df = pd.DataFrame({
    "Vitamin/Mineral": vitamin_names,
    "Health Pro Link": vitamin_links
})
df.to_excel("vitamin_links.xlsx", index=False)

print("✅ Done. Saved as 'vitamin_links.xlsx'")


#DUOMENU SCRAPINIMAS PAGAL LINKUS
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import time

# Load the Excel file with vitamin names and links
df_links = pd.read_excel("vitamin_links.xlsx")

# Result container
vitamin_data = []

# Loop through each vitamin and its link
for index, row in df_links.iterrows():
    name = row['Vitamin/Mineral']
    url = row['Health Pro Link']
    
    print(f"🔍 Processing: {name}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the content area
    content_area = soup.find('div', id='fact-sheet')
    if not content_area:
        print(f"❌ No content found for {name}")
        continue

    # Extract sections
    section_dict = defaultdict(str)
    section_dict['Vitamin/Mineral'] = name  # Add vitamin name first

    current_section = None

    for tag in content_area.find_all(['h2', 'h3', 'p', 'ul']):
        if tag.name in ['h2', 'h3']:
            current_section = tag.get_text(strip=True)
        elif current_section:
            section_dict[current_section] += tag.get_text(separator=" ", strip=True) + "\n"

    vitamin_data.append(section_dict)
    
    time.sleep(1)  # Be polite to the server

# Convert to DataFrame
df_final = pd.DataFrame(vitamin_data)

# Move 'Vitamin/Mineral' column to the front
columns = df_final.columns.tolist()
columns.insert(0, columns.pop(columns.index('Vitamin/Mineral')))
df_final = df_final[columns]

# Save to Excel
df_final.to_excel("vitamin_info_structured.xlsx", index=False)

print("✅ Done! Saved as 'vitamin_info_structured.xlsx'")


#DUOMENYS I JSON
import pandas as pd
import json

# Load the Excel file
df = pd.read_excel("vitamin_info_structured.xlsx")

# Convert DataFrame rows to list of dictionaries
data = df.to_dict(orient='records')

# Optional: Save to .json file
with open("vitamin_info_structured.json", "w", encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Print a preview
print(json.dumps(data[:2], indent=2, ensure_ascii=False))  # Show first 2 vitamins


#DUOMENYS LONG FORMATU
import pandas as pd

# Load the original wide-format Excel
df = pd.read_excel("vitamin_info_structured.xlsx")

# Convert to long format
long_df = df.melt(
    id_vars=["Vitamin/Mineral"],
    var_name="Section",
    value_name="Content"
)

# Optional: Drop rows where content is missing
long_df = long_df.dropna(subset=["Content"]).reset_index(drop=True)

# Save to a new Excel file
long_df.to_excel("vitamin_info_long_format.xlsx", index=False)

print("✅ Saved as 'vitamin_info_long_format.xlsx'")
