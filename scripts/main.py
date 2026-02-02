import json
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from datetime import datetime

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
VISUAL_SCALE_FACTOR = config['settings']['visual_scale']
GEO_CODE = config['settings']['geo']
TIMEFRAME = config['settings']['timeframe']
COUNTRY_NAMES = config['country_names']
DESTINATIONS_DATA = config['destinations']

# Quick ISO lookup
ISO_MAP = {item['city']: item['iso'] for item in DESTINATIONS_DATA}
CITIES_LIST = [item['city'] for item in DESTINATIONS_DATA]

def build_query(city_name):
    return f"Voli {city_name} + Hotel {city_name}"

def clean_query_name(query_string):
    return query_string.split(" +")[0].replace("Voli ", "").strip()

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

ANCHOR_KEYWORD = build_query(ANCHOR_CITY)
print(f"Config: anchor='{ANCHOR_CITY}' | scale=x{VISUAL_SCALE_FACTOR} | output='{os.path.basename(RESULTS_FILE)}'")

# reading old data
old_indices = {}

if os.path.exists(RESULTS_FILE):
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)

            for item in old_data:
                # use city name as key to recover previous index
                if 'name' in item and 'index' in item:
                    old_indices[item['name']] = item['index']
        print(f"recuperati {len(old_indices)} indici precedenti per il calcolo trend.")
    except Exception as e:
        print(f"Impossibile leggere dati vecchi: {e}. I trend saranno nulli.")

final_results = []
batches = list(chunks(CITIES_LIST, 4))  # 4 cities + 1 anchor = 5 queries

print(f"Starting scan: {len(CITIES_LIST)} destinations in {len(batches)} batches.")

for i, batch in enumerate(batches):
    batch_queries = [build_query(city) for city in batch]
    current_request_queries = batch_queries + [ANCHOR_KEYWORD]  # always include anchor

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
            for idx, keyword in enumerate(current_request_queries):
                batch_means[keyword] = sums[idx] / valid_points_count
        else:
            continue

        anchor_val = batch_means.get(ANCHOR_KEYWORD, 0)
        if anchor_val == 0:
            print("Warning: anchor value is 0; skipping normalization for this batch.")
            continue

        for keyword, raw_score in batch_means.items():
            if keyword == ANCHOR_KEYWORD:
                continue

            normalized_score = (raw_score / anchor_val) * VISUAL_SCALE_FACTOR
            index = round(normalized_score, 1)

            city_name_clean = clean_query_name(keyword)
            old_index = old_indices.get(city_name_clean, 0)
            diff = index - old_index

            trend_direction = "stable"
            if diff > 1.0:
                trend_direction = "up"
            elif diff < -1.0:
                trend_direction = "down"

            iso_code = ISO_MAP.get(city_name_clean, "UNK")
            country_name = COUNTRY_NAMES.get(iso_code, "Mondo")
            today = datetime.now().strftime("%Y-%m-%d")

            final_results.append({
                "name": city_name_clean,
                "country_code": iso_code,
                "country_name": country_name,
                "index": index,
                "trend": trend_direction,
                "trend_diff": round(diff, 1),
                "last_updated": today
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