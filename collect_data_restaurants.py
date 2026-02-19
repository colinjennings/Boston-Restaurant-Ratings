import requests
import pandas as pd
import time

# put your own api key from places_api
API_KEY = "your_api_key"


def search_restaurants(query, page_token=None):
    """Search for restaurants using Google Places Text Search API"""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": API_KEY,
    }
    if page_token:
        params["pagetoken"] = page_token

    response = requests.get(url, params=params)
    return response.json()


def get_place_details(place_id):
    """Get detailed info for a specific place"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,geometry,rating,user_ratings_total,price_level,types,business_status,opening_hours",
        "key": API_KEY,
    }
    response = requests.get(url, params=params)
    return response.json()


# Search queries to maximize coverage across Boston neighborhoods and cuisines
queries = [
    "restaurants in Boston MA",
    "restaurants in Back Bay Boston",
    "restaurants in South End Boston",
    "restaurants in North End Boston",
    "restaurants in Fenway Boston",
    "restaurants in Allston Boston",
    "restaurants in Brighton Boston",
    "restaurants in Brookline MA",
    "restaurants in Cambridge MA",
    "restaurants in Somerville MA",
    "restaurants in Jamaica Plain Boston",
    "restaurants in Dorchester Boston",
    "restaurants in Charlestown Boston",
    "restaurants in Beacon Hill Boston",
    "restaurants in Chinatown Boston",
    "restaurants in Seaport Boston",
    "Italian restaurants Boston",
    "Chinese restaurants Boston",
    "Mexican restaurants Boston",
    "Thai restaurants Boston",
    "Indian restaurants Boston",
    "Japanese restaurants Boston",
    "Pizza Boston",
    "Seafood restaurants Boston",
    "Brunch Boston",
    "Cheap eats Boston",
    "Fine dining Boston",
    "Korean restaurants Boston",
    "Vietnamese restaurants Boston",
    "Mediterranean restaurants Boston",
]

# Use dict to avoid duplicates by place_id
all_places = {}

for query in queries:
    print(f"Searching: {query}")

    # First page
    results = search_restaurants(query)

    if results.get("status") != "OK":
        print(f"  Error: {results.get('status')}")
        continue

    for place in results.get("results", []):
        pid = place["place_id"]
        if pid not in all_places:
            all_places[pid] = {
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
                "rating": place.get("rating"),
                "review_count": place.get("user_ratings_total"),
                "price_level": place.get("price_level"),
                "types": ", ".join(place.get("types", [])),
                "business_status": place.get("business_status"),
            }

    print(f"  Found {len(results.get('results', []))} results. Total unique: {len(all_places)}")

    # Get additional pages (Google returns up to 3 pages of 20 results each)
    while results.get("next_page_token"):
        time.sleep(2)  # Google requires a short delay before using next_page_token
        results = search_restaurants(query, page_token=results["next_page_token"])

        if results.get("status") != "OK":
            break

        for place in results.get("results", []):
            pid = place["place_id"]
            if pid not in all_places:
                all_places[pid] = {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                    "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
                    "rating": place.get("rating"),
                    "review_count": place.get("user_ratings_total"),
                    "price_level": place.get("price_level"),
                    "types": ", ".join(place.get("types", [])),
                    "business_status": place.get("business_status"),
                }

        print(f"  Next page. Total unique: {len(all_places)}")

    time.sleep(1)

# Convert to dataframe
df = pd.DataFrame(all_places.values())

# Filter to only operational restaurants
df = df[df["business_status"] == "OPERATIONAL"]

# Map price_level numbers to symbols
price_map = {0: "Free", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
df["price_category"] = df["price_level"].map(price_map)


# Try to extract neighborhood from address
def get_neighborhood(address):
    if pd.isna(address):
        return "Unknown"
    parts = address.split(",")
    if len(parts) >= 2:
        return parts[1].strip()
    return "Unknown"


df["neighborhood"] = df["address"].apply(get_neighborhood)

# Save to CSV
df.to_csv("boston_restaurants.csv", index=False)

print(f"\n=== DONE ===")
print(f"Total restaurants collected: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nRating stats:")
print(df["rating"].describe())
print(f"\nPrice level distribution:")
print(df["price_category"].value_counts())
print(f"\nSaved to boston_restaurants.csv")