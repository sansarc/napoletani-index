# Napoletani Index 🌋

A data visualization project tracking the travel interest ("Hype") of people from Naples (Campania) towards international destinations.

The project features an interactive choropleth map built with Vue 3 and Leaflet, powered by a Python data pipeline that scrapes and normalizes Google Trends data.

## ⚙️ How it works

The **Hype Index** is not based on future sure presence, but on search intent.
1.  **Data Source:** Google Trends (via SerpApi).
2.  **Query Logic:** Composite queries (`Voli [City] + Hotel [City]`) geolocalized in Campania (`IT-72`).
3.  **Normalization:** Since Google Trends returns relative values (0-100 per batch), all data is normalized against a **hidden anchor** (high-volume domestic route) to ensure consistency across different API batches.
4.  **Logic:** The country score is calculated using a "Champion + Bonus" algorithm (Highest scoring city + 15% of other cities' volume) to balance single-destination countries (e.g., Netherlands/Amsterdam) vs multi-destination countries (e.g., Spain).

## 🛠 Tech Stack

* **Frontend:** Vue 3, Leaflet, CSS3.
* **Data Pipeline:** Python 3.9 (SerpApi, Pandas).
* **CI/CD:** GitHub Actions (Weekly cron job).
* **Hosting:** Vercel.

## 📂 Project Structure

* `src/`: Vue frontend application.
* `scripts/`: Python scripts for data fetching and normalization.
* `config.json`: Central configuration for destinations, ISO mapping, and API settings.
* `src/assets/data.json`: The generated dataset (committed automatically by the bot).

## 🚀 Running Locally

### 1. Frontend
```bash
npm install
npm run dev