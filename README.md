# DE_lab-Ride-Sharing-Intelligence-System
Here’s a **GitHub-ready `README.md`** for your Ride-Sharing Intelligence System project, written in clean Markdown with minimal emojis and full code formatting. This version is detailed, structured, and directly copy-pastable to GitHub (or similar platforms).

***

# Ride-Sharing Intelligence System

A Real-Time Analytics & Management Dashboard for Modern Ride-Sharing Ecosystems  
**By:** [Adil Deokar](https://www.linkedin.com/in/adildeokar) & Achute Yesare   

Built with: Streamlit -  MongoDB -  Plotly -  Python

***

## Overview

The Ride-Sharing Intelligence System is an interactive analytics and management dashboard that simulates and analyzes ride-sharing data in **real time**.  
It leverages MongoDB for backend storage and provides a visually rich interface using Streamlit and Plotly.

**Key applications:**
- Real-time visualization of ride, surge, and driver data
- Monitoring essential platform metrics (rides, drivers, revenue)
- Realistic simulation of driver and rider interactions
- Deep analytics for demand-supply balance and surge pricing
- One-click generation of demo data for all entities

***

## Key Features

- Fully interactive **Streamlit dashboard**
- MongoDB-powered persistence and efficient querying
- Dynamic sample data simulation (drivers, riders, rides, surge)
- Real-time ride tracking and geographic mapping
- Driver performance insights (earnings, ratings, rankings)
- Zone-based surge pricing and demand analytics
- One-click "Initialize Database" for instant exploration
- No external runtime dependencies (plug & play local setup)

***

## Tech Stack

| Component      | Technology         | Purpose                                 |
| -------------- | ----------------- | --------------------------------------- |
| Frontend       | Streamlit         | Interactive Python dashboard UI         |
| Visualization  | Plotly Express    | Beautiful, animated charts/graphs       |
| Database       | MongoDB           | NoSQL data store for all app entities   |
| Data Handling  | Pandas            | DataFrames for transformation/analysis  |
| Backend Logic  | Python 3.x        | Main application, seeding, logic        |
| Deployment     | Localhost         | Run locally (or deploy on Streamlit Cloud) |

***

## Installation & Setup

This guide will take you from zero to a fully operational dashboard.

### 1. Install MongoDB

**Windows**
- Download: [MongoDB Download Center](https://www.mongodb.com/try/download/community)
- Run installer, choose "Complete" setup
- Enable "Install MongoDB as a Service"
- By default, MongoDB runs at: `mongodb://localhost:27017`

**Verify installation**
```cmd
mongo --version        # Shows MongoDB version
net start MongoDB      # Starts MongoDB service (if needed)
```

**macOS/Linux**
- Use your package manager or follow [MongoDB installation docs](https://docs.mongodb.com/manual/installation/).

### 2. Setup Python Environment

```bash
python -m venv venv
```
Activate:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

### 3. Install Project Dependencies

```bash
pip install streamlit pymongo plotly pandas
```
(Optional for smoother visuals:)
```bash
pip install streamlit-lottie
```

### 4. Run the Application

Make sure MongoDB is running locally.
```bash
streamlit run app.py
```
Open your browser at: [http://localhost:8501](http://localhost:8501/)

### 5. Initialize the Database

- Use the sidebar in the app
- Click **"Initialize Database"**  
  *(This seeds rich demo data for drivers, riders, vehicles, rides, surge zones)*

***

## App Highlights

- **Dashboard:**  
  Overview metrics (rides, drivers, revenue, ratings), plus pie/bar/line charts.
- **Real-Time Rides:**  
  Live ride list (all statuses), filter/search, geo map for pickups/drop-offs.
- **Driver Management:**  
  Daily performance table, ranks, earnings and rating distributions.
- **Surge Pricing:**  
  Demand/supply analytics by zone, see which areas are surging.
- **Analytics:**  
  Trip efficiency, fare-per-km breakdowns, satisfaction/OLS trends.
- **Add New Ride:**  
  Easy form to create requests and see live updates instantly.

***

## Example Dashboard Metrics

| Metric          | Description                     |
| --------------  | ------------------------------ |
| Total Rides     | All rides stored in the system  |
| Active Drivers  | Drivers currently "available"   |
| Revenue Today   | Total completed fares today     |
| Avg Rating      | Mean across completed rides     |
| Surge Multiplier| Fare inflation in high-demand   |

***

## Project Structure

```
Ride-Sharing-Intelligence/
├── app.py                # Main Streamlit Application
├── requirements.txt      # Dependencies (optional)
├── README.md             # This file
└── /venv                 # Virtual Environment (optional)
```

***

## MongoDB Collections

**Database:** `ride_demo`

- `drivers`
- `riders`
- `vehicles`
- `rides`
- `surge_pricing`

Each collection is automatically seeded for hands-on simulation.

***

## Creators

| Name            | Role                         | LinkedIn                                    |
| --------------- | --------------------------- | ------------------------------------------- |
| Adil Deokar     | Full Stack & AI Developer   | [linkedin.com/in/adildeokar](https://www.linkedin.com/in/adildeokar) |
| Achute Yesare   | Backend/Data Engineer       | —                                           |

***

## Future Directions

- Integration with Google Maps API for precise geocoding
- Mobile dashboard versions for drivers/riders
- Predictive analytics with advanced ML models
- Real-time notifications for demand/surge events

***

## Final Launch Checklist

- MongoDB on `mongodb://localhost:27017`
- App runs at `http://localhost:8501`
- All data persists between app restarts

```bash
streamlit run app.py
```

***

## Conclusion

This dashboard is a robust simulation and analytics suite for the ride-sharing domain—ideal for hackathons, data science demos, research, and developer portfolios.

If you found this project useful, feel free to ⭐ star it, fork, or give feedback!

***

[//]: # (End of README.md)
