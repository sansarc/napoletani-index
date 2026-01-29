import json
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
RESULTS_FILE = os.path.join(BASE_DIR, '..', 'src', 'assets', 'data.json')

# Load environment variables
load_dotenv(ENV_PATH)

# Load configuration
print(f"Reading config from: {CONFIG_FILE}")

try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f: 
        config = json.load(f)
except FileNotFoundError:
    print(f"Fatal: config file not found: {CONFIG_FILE}")
    raise SystemExit(1)
except json.JSONDecodeError:
    print(f"Fatal: invalid JSON in: {CONFIG_FILE}")
    raise SystemExit(1)

# Settings
ANCHOR_CITY = config['settings']['anchor_city']
SCALA_VISIVA = config['settings']['visual_scale']
GEO_CODE = config['settings']['geo']
TIMEFRAME = config['settings']['timeframe']
COUNTRY_NAMES = config['country_names']
DESTINATIONS_DATA = config['destinations']

# Quick ISO lookup
ISO_MAP = {item['city']: item['iso'] for item in DESTINATIONS_DATA}
CITIES_LIST = [item['city'] for item in DESTINATIONS_DATA]

def build_query(city_name):
    """Build a compound query like: 'Voli Milano + Hotel Milano'."""
    return f"Voli {city_name} + Hotel {city_name}"

def clean_query_name(query_string):
    """Extract a display city name: 'Voli Londra + Hotel Londra' -> 'Londra'."""
    return query_string.split(" +")[0].replace("Voli ", "").strip()

def chunks(lst, n):
    """Yield list chunks of size n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

ANCHOR_QUERY = build_query(ANCHOR_CITY)
print(f"Config: anchor='{ANCHOR_CITY}' | scale=x{SCALA_VISIVA} | output='{os.path.basename(RESULTS_FILE)}'")

final_results = []
batches = list(chunks(CITIES_LIST, 4))  # 4 cities + 1 anchor = 5 queries

print(f"Starting scan: {len(CITIES_LIST)} destinations in {len(batches)} batches.")

for i, batch in enumerate(batches):
    batch_queries = [build_query(city) for city in batch]
    current_request_queries = batch_queries + [ANCHOR_QUERY]  # always include anchor

    print(f"\nBatch {i+1}/{len(batches)}: {batch}...")

    params = {
        "engine": "google_trends",
        "q": ",".join(current_request_queries),
        "geo": GEO_CODE,
        "data_type": "TIMESERIES",
        "date": TIMEFRAME,
        "api_key": os.getenv("API_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        if "error" in results:
            print(f"API error: {results['error']}")
            continue

        data_over_time = results.get("interest_over_time", {}).get("timeline_data", [])
        if not data_over_time:
            print("No data returned for this batch.")
            continue

        num_queries_in_batch = len(current_request_queries)
        sums = [0] * num_queries_in_batch
        valid_points_count = 0

        for time_period in data_over_time:
            if "values" in time_period:
                valid_points_count += 1
                for idx, query_val in enumerate(time_period["values"]):
                    sums[idx] += int(query_val.get("extracted_value", 0))

        batch_means = {}
        if valid_points_count > 0:
            for idx, query_string in enumerate(current_request_queries):
                batch_means[query_string] = sums[idx] / valid_points_count
        else:
            continue

        anchor_val = batch_means.get(ANCHOR_QUERY, 0)
        if anchor_val == 0:
            print("Warning: anchor value is 0; skipping normalization for this batch.")
            continue

        for query_string, raw_score in batch_means.items():
            if query_string == ANCHOR_QUERY:
                continue

            normalized_score = (raw_score / anchor_val) * SCALA_VISIVA

            city_name_clean = clean_query_name(query_string)
            iso_code = ISO_MAP.get(city_name_clean, "UNK")
            country_name = COUNTRY_NAMES.get(iso_code, "Mondo")

            final_results.append({
                "name": city_name_clean,
                "country_code": iso_code,
                "country_name": country_name,
                "index": round(normalized_score, 1)
            })

    except Exception as e:
        print(f"Batch error: {e}")

print("\nSaving output...")

try:
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

    print(f"Done. Updated: {os.path.abspath(RESULTS_FILE)}")
except Exception as e:
    print(f"Save error: {e}")