# Sembako Analytics Dashboard API Reference

Welcome to the Sembako Analytics API documentation. This API powers the interactive visual analytics for the Macro Dashboard and Micro Deep-Dive features of the Sembako Analytics Platform.

## 1. Authentication

All analytical and core endpoints are protected. Clients must authenticate by passing an API key in the request headers.

**Header Name:** `X-API-Key`  
**Example:**
```http
GET /api/v1/analytics/volatility HTTP/1.1
Host: api.sembako-dashboard.id
X-API-Key: YOUR_API_KEY_HERE
```

## 2. Critical Architectural Rule: Static Dimensions

> **⚠️ CRITICAL:** The Dimension APIs (`Province`, `Regency`, `Commodity`, `Market`) are **strictly static endpoints** based on fixed integer IDs. 
> 
> Clients **MUST NOT** use string names (e.g., `"DKI Jakarta"`, `"Beras Medium"`) to query the Analytics endpoints. You must first fetch the master data from the Dimension endpoints to retrieve the correct ID (e.g., `commodity_id=1`, `regency_id=3171`), and pass those static IDs as path or query parameters in all subsequent analytical queries.

---

## 3. Data Flow & Master Data Dependency

To ensure data integrity and avoid mismatching string names, developers must strictly adhere to the following two-step workflow when integrating with the Sembako Analytics Engine.

### The Two-Step Workflow

**Step 1: Fetch Dimension IDs**
Before calling any `/analytics` endpoints, your application must fetch the required static IDs from the Master Data endpoints. These endpoints return read-only, statically mapped dimension tables.
- `GET /api/v1/locations/provinces` -> Returns `province_id`
- `GET /api/v1/locations/regencies` -> Returns `regency_id`
- `GET /api/v1/commodities/items` -> Returns `commodity_id`
- `GET /api/v1/markets` -> Returns `market_id`

*Note: The dimension endpoints are purely static. Clients cannot `POST`, `PUT`, or dynamically create new provinces, commodities, or markets via this API. The data is synchronized via an internal ETL pipeline from the national database.*

**Step 2: Feed IDs into Analytics**
Once you have the required `regency_id` and `commodity_id`, inject them as query parameters into the Analytics endpoints.

Example workflow to get Volatility for "Beras Medium" in "DKI Jakarta":
1. Query `/commodities/items` to find "Beras Medium" -> gets ID `1`.
2. Query `/locations/provinces` to find "DKI Jakarta" -> gets ID `31`.
3. Query `/analytics/volatility?commodity_id=1&province_id=31`.

---

## 4. Analytics Methodology

The Sembako Analytics API heavily relies on complex SQL aggregations, window functions, and integrated Machine Learning algorithms. Below is a summary of the math driving our Micro and Macro insights.

### 3.1. Market Behavior Clusters
- **Goal:** Segment local markets based on price stability.
- **Math:** We aggregate 30 days of market prices to compute the Mean (X-axis) and Standard Deviation (Y-axis). 
- **Algorithm:** Uses Scikit-Learn's K-Means clustering ($k=3$) to group markets. If the sample size is too small ($N < 5$), it gracefully falls back to Statistical Binning using percentiles.

### 3.2. Market Type Spread (Supply Chain Disparity)
- **Goal:** Identify price gouging or premium margins between retail types.
- **Math:** Groups daily prices by Market Type (Traditional vs. Modern vs. Wholesale).
- **Formula:** `Margin Premium (%) = ((Modern_Price - Traditional_Price) / Traditional_Price) * 100`
- **Insight:** Widening margins often indicate logistical bottlenecks at the traditional level.

### 3.3. Historical Anomalies
- **Goal:** Early warning system for price spikes and drops.
- **Math:** We utilize a **7-Day Moving Average (7D MA)** as our dynamic baseline.
- **Trigger:** An anomaly is recorded if the current daily price deviates from the 7D MA by more than the predefined volatility threshold ($0.3\%$).

### 3.4. Volatility Index
- **Goal:** Compare the risk of completely different commodities (e.g., Rice vs. Beef) fairly.
- **Formula:** Uses the **Coefficient of Variation (CV)**: `(Population_StdDev / Mean) * 100`.
- **Insight:** This normalizes volatility. A $1,000 IDR shift is massive for Rice but negligible for Beef.

### 3.5. Predictive Price Trajectory
- **Goal:** Forecast the next 14 days of commodity prices.
- **Math:** Extracts the last 90 days of price data. Interpolates any missing dates linearly.
- **Algorithm:** Uses a **Degree-1 Polynomial Fit (Linear Regression)** via NumPy.
- **Uncertainty:** An expanding confidence interval (from 2% to 5%) is added to the upper and lower bounds to visually denote increasing prediction uncertainty over time.

### 3.6. Cross-Commodity Correlation
- **Goal:** Find substitute or complementary goods.
- **Math:** Pivots 90 days of price data for all commodities into a matrix.
- **Algorithm:** Computes the **Pearson Correlation Coefficient** matrix ($-1.0$ to $1.0$).
- **Output:** Returns the top 5 commodities with the highest absolute correlation to the target.

---

## 5. Core Analytics Endpoints

*(Note: For interactive testing and dynamic schema exploration, please visit the `/docs` or `/redoc` Swagger UI hosted on your local or production FastAPI server).*

### Macro Analytics Endpoints
- `GET /analytics/seasonality`: Fetches time-series data aggregated by day to expose seasonal harvesting effects.
- `GET /analytics/disparity`: Calculates regional averages vs. the national baseline for choropleth mapping.
- `GET /analytics/anomalies`: Identifies the top 5 historical anomalies across all commodities.
- `GET /analytics/macro-anomalies`: Identifies regencies experiencing current price shocks.
- `GET /analytics/regional-matrix`: Rolls up prices to the Provincial level.
- `GET /analytics/volatility`: Returns a ranked list of commodities by their 30-day CV index.
- `GET /analytics/inflation-heatmap`: Computes Month-over-Month (MoM) inflation percentage differences.
- `GET /analytics/affordability-basket`: Computes the total price of a custom basket of goods across regions.

### Micro Deep-Dive Analytics Endpoints
- `GET /analytics/spread/market-types`: Computes structural pricing spreads between Market Types.
- `GET /analytics/supply-chain-margin`: Computes absolute margins across Produsen, Wholesale, and Retail nodes.
- `GET /analytics/predictive-trajectory`: Forecasts 14 days of prices using Linear Regression.
- `GET /analytics/correlation`: Returns the top 5 correlated commodities via Pearson coefficient.
- `GET /analytics/market-clusters`: Segments markets into high/low risk clusters using K-Means.

---
*Generated by Antigravity*
