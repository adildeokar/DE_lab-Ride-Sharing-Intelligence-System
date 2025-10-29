# app.py — Ride-Sharing Intelligence (stable connection, no runtime installs)
import sys
import random
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

# ---------- Page and styles ----------
st.set_page_config(page_title="Ride-Sharing Intelligence", page_icon="🚗", layout="wide", initial_sidebar_state="expanded")  # [web:29]

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 8px; padding: 10px 20px; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)  # [web:29]

# ---------- Mongo connection (cached, retryable) ----------
def mongo_uri():
    return "mongodb://localhost:27017"  # adjust if needed [web:32]

@st.cache_resource(show_spinner="Connecting to MongoDB...", ttl=0)
def get_db(_nonce: int = 0):
    client = MongoClient(mongo_uri(), serverSelectionTimeoutMS=3000)  # 3s timeout [web:94]
    client.admin.command("ping")
    return client["ride_demo"]  # stable app DB name [web:32]

def force_reconnect():
    st.session_state["_mongo_nonce"] = st.session_state.get("_mongo_nonce", 0) + 1
    st.rerun()  # re-exec script and bust cache via nonce [web:89]

# ---------- Seeding ----------
def initialize_database(db):
    try:
        for col in ['drivers', 'riders', 'rides', 'surge_pricing', 'vehicles']:
            db[col].delete_many({})
        # Drivers
        driver_names = ['John Smith','Emma Johnson','Michael Brown','Sarah Davis','David Wilson','Lisa Anderson','James Taylor','Maria Garcia','Robert Martinez','Jennifer Lopez','William Clark','Patricia White']
        drivers = []
        for i, name in enumerate(driver_names, 1):
            drivers.append({
                "driver_id": f"DRV{str(i).zfill(3)}",
                "name": name,
                "phone": f"+1-555-{random.randint(1000, 9999)}",
                "rating": round(random.uniform(4.0, 5.0), 2),
                "total_rides": random.randint(50, 500),
                "status": random.choice(['available', 'busy', 'offline']),
                "location": {"lat": round(random.uniform(40.7, 40.8), 4), "lng": round(random.uniform(-74.0, -73.9), 4)},
                "earnings_today": round(random.uniform(50, 300), 2),
                "vehicle_id": f"VEH{str(i).zfill(3)}"
            })
        db.drivers.insert_many(drivers)

        # Riders
        rider_names = ['Alice Cooper','Bob Martin','Charlie Evans','Diana Prince','Edward Norton','Fiona Apple','George Lucas','Hannah Montana','Ian McKellen','Julia Roberts','Kevin Hart','Laura Palmer']
        riders = []
        for i, name in enumerate(rider_names, 1):
            riders.append({
                "rider_id": f"RDR{str(i).zfill(3)}",
                "name": name,
                "phone": f"+1-555-{random.randint(1000, 9999)}",
                "rating": round(random.uniform(4.0, 5.0), 2),
                "total_rides": random.randint(10, 200),
                "payment_method": random.choice(['Credit Card','PayPal','Apple Pay','Google Pay']),
                "wallet_balance": round(random.uniform(0, 100), 2)
            })
        db.riders.insert_many(riders)

        # Vehicles
        vehicle_data = [('Toyota','Camry',2021),('Honda','Civic',2022),('Ford','Fusion',2020),('Chevrolet','Malibu',2021),('Nissan','Altima',2022),('Hyundai','Sonata',2021),('Kia','Optima',2020),('Mazda','Mazda6',2021),('Volkswagen','Passat',2022),('Subaru','Legacy',2021),('Tesla','Model 3',2023),('BMW','3 Series',2022)]
        colors = ['Black','White','Silver','Blue','Red','Gray','Green','Brown']
        vehicles = []
        for i, (make, model, year) in enumerate(vehicle_data, 1):
            vehicles.append({
                "vehicle_id": f"VEH{str(i).zfill(3)}",
                "make": make, "model": model, "year": year,
                "license_plate": f"{chr(65+random.randint(0,25))}{chr(65+random.randint(0,25))}{random.randint(1000,9999)}",
                "color": random.choice(colors),
                "capacity": random.choice([4,6,8])
            })
        db.vehicles.insert_many(vehicles)

        # Rides
        rides, statuses, street_names = [], ['completed','in_progress','cancelled','pending'], ['Main','Oak','Pine','Maple','Broadway','Park','Market','First','Second','Third']
        for i in range(15):
            start_time = datetime.now() - timedelta(hours=random.randint(0, 72))
            duration = random.randint(10, 60)
            distance = round(random.uniform(2, 25), 2)
            base_fare = round(distance * 1.5 + random.uniform(2, 5), 2)
            surge_multiplier = round(random.uniform(1.0, 2.5), 1)
            status = random.choice(statuses)
            rides.append({
                "ride_id": f"RIDE{str(i + 1).zfill(4)}",
                "driver_id": f"DRV{str(random.randint(1, 12)).zfill(3)}",
                "rider_id": f"RDR{str(random.randint(1, 12)).zfill(3)}",
                "pickup_location": {"address": f"{random.randint(100, 999)} {random.choice(street_names)} St","lat": round(random.uniform(40.7, 40.8), 4),"lng": round(random.uniform(-74.0, -73.9), 4)},
                "dropoff_location": {"address": f"{random.randint(100, 999)} {random.choice(street_names)} Ave","lat": round(random.uniform(40.7, 40.8), 4),"lng": round(random.uniform(-74.0, -73.9), 4)},
                "request_time": start_time.isoformat(),
                "start_time": (start_time + timedelta(minutes=random.randint(2, 8))).isoformat(),
                "end_time": (start_time + timedelta(minutes=duration)).isoformat(),
                "status": status,
                "distance_km": distance,
                "duration_minutes": duration,
                "base_fare": base_fare,
                "surge_multiplier": surge_multiplier,
                "total_fare": round(base_fare * surge_multiplier, 2),
                "payment_status": 'paid' if status == 'completed' else 'pending',
                "rating": round(random.uniform(3.5, 5.0), 1) if status == 'completed' else None
            })
        db.rides.insert_many(rides)

        # Surge data
        zone_types = ['Downtown','Uptown','Midtown','Airport','Business District','Suburb','Mall Area','Train Station','University','Beach Area']
        surge_data = []
        for i in range(12):
            surge_data.append({
                "zone_id": f"ZONE{str(i + 1).zfill(2)}",
                "zone_name": f"{random.choice(zone_types)} {random.choice(['North','South','East','West','Central'])}",
                "current_surge": round(random.uniform(1.0, 2.8), 1),
                "demand_level": random.choice(['low','medium','high','very_high']),
                "available_drivers": random.randint(2, 25),
                "active_requests": random.randint(0, 40),
                "timestamp": datetime.now().isoformat(),
                "avg_wait_time": random.randint(2, 15)
            })
        db.surge_pricing.insert_many(surge_data)
        return True
    except Exception as e:
        st.error(f"Database Initialization Error: {e}")  # UI side effect
        return False  # [web:32]

# ---------- Data access ----------
def get_dashboard_metrics(db):
    try:
        total_rides = db.rides.count_documents({})
        active_drivers = db.drivers.count_documents({"status": "available"})
        completed_rides = list(db.rides.find({"status": "completed"}))
        total_revenue = sum([ride.get('total_fare', 0) for ride in completed_rides])
        rides_with_rating = list(db.rides.find({"rating": {"$ne": None}}))
        avg_rating = round(sum([r['rating'] for r in rides_with_rating]) / len(rides_with_rating), 2) if rides_with_rating else 0
        return {"total_rides": total_rides,"active_drivers": active_drivers,"total_revenue": total_revenue,"avg_rating": avg_rating}
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
        return {"total_rides": 0, "active_drivers": 0, "total_revenue": 0, "avg_rating": 0}  # [web:32]

def get_all_rides(db):
    try:
        rides = list(db.rides.find({}, {'_id': 0}))
        if rides:
            df = pd.DataFrame(rides)
            if 'request_time' in df.columns:
                df['request_time'] = pd.to_datetime(df['request_time'])
            return df.sort_values('request_time', ascending=False) if not df.empty else df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching rides: {e}")
        return pd.DataFrame()  # [web:32]

def get_all_drivers(db):
    try:
        drivers = list(db.drivers.find({}, {'_id': 0}))
        return pd.DataFrame(drivers)
    except Exception as e:
        st.error(f"Error fetching drivers: {e}")
        return pd.DataFrame()  # [web:32]

def get_surge_data(db):
    try:
        surge = list(db.surge_pricing.find({}, {'_id': 0}))
        return pd.DataFrame(surge)
    except Exception as e:
        st.error(f"Error fetching surge data: {e}")
        return pd.DataFrame()  # [web:32]

# ---------- App ----------
def main():
    st.markdown('<h1 class="main-header">🚗 Ride-Sharing Intelligence System</h1>', unsafe_allow_html=True)  # [web:29]

    # Robust connection with retry
    nonce = st.session_state.get("_mongo_nonce", 0)
    try:
        db = get_db(nonce)
    except (ServerSelectionTimeoutError, OperationFailure) as e:
        st.error(f"❌ MongoDB connection failed: {e}")
        colr1, colr2 = st.columns([1,1])
        with colr1:
            if st.button("🔁 Retry Connection", use_container_width=True):
                force_reconnect()
        with colr2:
            st.info("Ensure mongod is running on localhost:27017, then click Retry.")  # [web:32]
        return

    # Sidebar
    with st.sidebar:
        st.title("Navigation")  # [web:29]
        if st.button("🔄 Initialize Database", use_container_width=True):
            with st.spinner("Initializing database with sample data..."):
                if initialize_database(db):
                    st.success("✅ Database initialized successfully!")
                    st.balloons()
                    st.rerun()  # refresh UI after seeding [web:89]
        st.divider()
        page = st.radio("Select View", ["📊 Dashboard","🚕 Real-Time Rides","👨‍✈️ Driver Management","📈 Surge Pricing","📉 Analytics","➕ Add New Ride"])
        st.divider()
        try:
            db.command('ping')
            st.success("🟢 MongoDB Connected")
        except Exception:
            st.error("🔴 MongoDB Disconnected")
        if st.button("🔁 Reconnect to MongoDB", use_container_width=True):
            force_reconnect()

    # Dashboard
    if page == "📊 Dashboard":
        metrics = get_dashboard_metrics(db)
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Rides", metrics['total_rides'], "↑ 12%")
        with col2: st.metric("Active Drivers", metrics['active_drivers'], "↑ 5%")
        with col3: st.metric("Revenue Today", f"${metrics['total_revenue']:.2f}", "↑ 8%")
        with col4: st.metric("Avg Rating", f"⭐ {metrics['avg_rating']}", "↑ 0.2")

        st.divider()
        rides_df = get_all_rides(db)
        drivers_df = get_all_drivers(db)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Ride Status Distribution")
            if not rides_df.empty:
                status_counts = rides_df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, color_discrete_sequence=px.colors.qualitative.Set3, hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No ride data. Initialize the database.")

        with c2:
            st.subheader("🚗 Driver Availability")
            if not drivers_df.empty:
                status_counts = drivers_df['status'].value_counts()
                fig = px.bar(x=status_counts.index, y=status_counts.values, color=status_counts.index, labels={'x': 'Status', 'y': 'Count'}, color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No driver data. Initialize the database.")

        st.subheader("💰 Revenue Trends (Last 7 Days)")
        if not rides_df.empty and 'request_time' in rides_df.columns:
            rides_df['date'] = rides_df['request_time'].dt.date
            daily_revenue = rides_df[rides_df['status'] == 'completed'].groupby('date')['total_fare'].sum().reset_index()
            if not daily_revenue.empty:
                fig = px.line(daily_revenue, x='date', y='total_fare', markers=True, labels={'total_fare': 'Revenue ($)', 'date': 'Date'})
                fig.update_traces(line_color='#667eea', line_width=3)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No completed rides to show revenue trends.")

    elif page == "🚕 Real-Time Rides":
        st.subheader("🚕 Real-Time Ride Monitoring")
        rides_df = get_all_rides(db)
        if not rides_df.empty:
            f1, _ = st.columns([2,1])
            with f1:
                status_filter = st.multiselect("Filter by Status", rides_df['status'].unique().tolist(), default=rides_df['status'].unique().tolist())
            filtered_rides = rides_df[rides_df['status'].isin(status_filter)]
            st.dataframe(filtered_rides[['ride_id','driver_id','rider_id','status','distance_km','total_fare','surge_multiplier','request_time']], use_container_width=True, hide_index=True)
            st.subheader("📍 Ride Locations Map")
            map_data = []
            for _, ride in filtered_rides.iterrows():
                for key in ["pickup_location","dropoff_location"]:
                    try:
                        map_data.append({'lat': ride[key]['lat'], 'lon': ride[key]['lng']})
                    except Exception:
                        pass
            if map_data:
                st.map(pd.DataFrame(map_data), zoom=11)
            else:
                st.info("No location data available for mapping.")
        else:
            st.warning("⚠️ No rides found. Initialize the database.")

    elif page == "👨‍✈️ Driver Management":
        st.subheader("👨‍✈️ Driver Performance Dashboard")
        drivers_df = get_all_drivers(db)
        if not drivers_df.empty:
            c1, c2 = st.columns([2,1])
            with c1:
                st.dataframe(drivers_df[['driver_id','name','rating','total_rides','status','earnings_today']], use_container_width=True, hide_index=True)
            with c2:
                st.subheader("🏆 Top Performers")
                for _, driver in drivers_df.nlargest(5, 'earnings_today').iterrows():
                    st.metric(driver['name'], f"${driver['earnings_today']:.2f}", f"⭐ {driver['rating']}")
            c3, c4 = st.columns(2)
            with c3:
                st.subheader("📊 Driver Ratings Distribution")
                st.plotly_chart(px.histogram(drivers_df, x='rating', nbins=20, color_discrete_sequence=['#764ba2']).update_layout(xaxis_title="Rating", yaxis_title="Drivers"), use_container_width=True)
            with c4:
                st.subheader("💰 Top 10 Earnings")
                top_earn = drivers_df.nlargest(10, 'earnings_today')
                st.plotly_chart(px.bar(top_earn, x='name', y='earnings_today', color='earnings_today', color_continuous_scale='Viridis').update_layout(xaxis_title="Driver", yaxis_title="Earnings ($)"), use_container_width=True)
        else:
            st.warning("⚠️ No drivers found. Initialize the database.")

    elif page == "📈 Surge Pricing":
        st.subheader("📈 Surge Pricing & Demand Analysis")
        surge_df = get_surge_data(db)
        if not surge_df.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🔥 Current Surge Multipliers")
                fig = px.bar(surge_df, x='zone_name', y='current_surge', color='current_surge', color_continuous_scale='Reds')
                fig.update_layout(xaxis_title="Zone", yaxis_title="Surge Multiplier"); fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.subheader("📊 Demand vs Supply")
                st.plotly_chart(px.scatter(surge_df, x='available_drivers', y='active_requests', size='current_surge', color='demand_level', hover_data=['zone_name'], color_discrete_map={'low':'green','medium':'yellow','high':'orange','very_high':'red'}), use_container_width=True)
            st.subheader("📋 Zone Details")
            st.dataframe(surge_df[['zone_name','current_surge','demand_level','available_drivers','active_requests','avg_wait_time']], use_container_width=True, hide_index=True)
            high_surge = surge_df[surge_df['current_surge'] > 2.0]
            if not high_surge.empty:
                st.warning(f"⚠️ High Surge Alert: {len(high_surge)} zones above 2.0x")
                for _, zone in high_surge.iterrows():
                    st.error(f"🔴 {zone['zone_name']}: {zone['current_surge']}x | {zone['active_requests']} requests | {zone['available_drivers']} drivers")
        else:
            st.warning("⚠️ No surge data. Initialize the database.")

    elif page == "📉 Analytics":
        st.subheader("📉 Advanced Analytics & Insights")
        rides_df = get_all_rides(db)
        if not rides_df.empty:
            tab1, tab2, tab3 = st.tabs(["Trip Efficiency","Revenue Analysis","Performance Metrics"])
            with tab1:
                c1, c2 = st.columns(2)
                completed = rides_df[rides_df['status'] == 'completed']
                with c1:
                    st.subheader("⏱️ Duration vs Distance")
                    if not completed.empty:
                        st.plotly_chart(px.scatter(completed, x='distance_km', y='duration_minutes', color='surge_multiplier', size='total_fare', trendline='ols'), use_container_width=True)
                with c2:
                    st.subheader("📏 Distance Distribution")
                    if not completed.empty:
                        st.plotly_chart(px.box(completed, y='distance_km', color_discrete_sequence=['#667eea']), use_container_width=True)
                if not completed.empty:
                    avg_speed = completed['distance_km'].sum() / max(1, completed['duration_minutes'].sum())
                    st.metric("Average Speed (km/min)", f"{avg_speed:.2f}")
            with tab2:
                st.subheader("💵 Revenue Breakdown")
                c1, c2 = st.columns(2)
                with c1:
                    revenue_by_status = rides_df.groupby('status')['total_fare'].sum()
                    st.plotly_chart(px.pie(values=revenue_by_status.values, names=revenue_by_status.index, title="Revenue by Ride Status", hole=0.3), use_container_width=True)
                with c2:
                    safe = rides_df[rides_df['distance_km'] > 0].copy()
                    if not safe.empty:
                        safe['fare_per_km'] = safe['total_fare'] / safe['distance_km']
                        st.plotly_chart(px.histogram(safe[safe['fare_per_km'] < 50], x='fare_per_km', nbins=30, title="Fare per Kilometer Distribution"), use_container_width=True)
            with tab3:
                st.subheader("⭐ Rating Analysis")
                rated = rides_df[(rides_df['status'] == 'completed') & (rides_df['rating'].notna())]
                if not rated.empty:
                    c1, c2 = st.columns(2)
                    with c1:
                        rd = rated['rating'].value_counts().sort_index()
                        st.plotly_chart(px.bar(x=rd.index, y=rd.values, labels={'x':'Rating','y':'Count'}, title="Rating Distribution"), use_container_width=True)
                    with c2:
                        st.plotly_chart(px.scatter(rated, x='total_fare', y='rating', trendline='ols', title="Fare vs Rating"), use_container_width=True)
                else:
                    st.info("No completed rides with ratings yet.")
        else:
            st.warning("⚠️ No analytics data. Initialize the database.")

    elif page == "➕ Add New Ride":
        st.subheader("➕ Request New Ride")
        drivers_df = get_all_drivers(db)
        riders_df = pd.DataFrame(list(db.riders.find({}, {'_id': 0})))
        if not drivers_df.empty and not riders_df.empty:
            available = drivers_df[drivers_df['status'] == 'available']
            if available.empty:
                st.warning("⚠️ No available drivers right now.")
                return
            with st.form("new_ride_form"):
                c1, c2 = st.columns(2)
                with c1:
                    rider = st.selectbox("Select Rider", riders_df['rider_id'].tolist())
                    pickup_addr = st.text_input("Pickup Address", "123 Main Street")
                    pickup_lat = st.number_input("Pickup Latitude", value=40.7589, format="%.4f")
                    pickup_lng = st.number_input("Pickup Longitude", value=-73.9851, format="%.4f")
                with c2:
                    driver = st.selectbox("Assign Driver", available['driver_id'].tolist())
                    dropoff_addr = st.text_input("Dropoff Address", "456 Broadway")
                    dropoff_lat = st.number_input("Dropoff Latitude", value=40.7614, format="%.4f")
                    dropoff_lng = st.number_input("Dropoff Longitude", value=-73.9776, format="%.4f")
                distance = st.number_input("Estimated Distance (km)", min_value=0.5, value=5.0, step=0.5)
                surge = st.slider("Surge Multiplier", 1.0, 3.0, 1.0, 0.1)
                submitted = st.form_submit_button("🚀 Create Ride Request", use_container_width=True)
                if submitted:
                    base = round(distance * 1.5 + 3.0, 2)
                    total = round(base * surge, 2)
                    next_id = db.rides.count_documents({}) + 1
                    new_ride = {
                        "ride_id": f"RIDE{str(next_id).zfill(4)}",
                        "driver_id": driver, "rider_id": rider,
                        "pickup_location": {"address": pickup_addr,"lat": pickup_lat,"lng": pickup_lng},
                        "dropoff_location": {"address": dropoff_addr,"lat": dropoff_lat,"lng": dropoff_lng},
                        "request_time": datetime.now().isoformat(),
                        "start_time": None, "end_time": None,
                        "status": "pending","distance_km": distance,"duration_minutes": None,
                        "base_fare": base,"surge_multiplier": surge,"total_fare": total,
                        "payment_status": "pending","rating": None
                    }
                    try:
                        db.rides.insert_one(new_ride)
                        st.success(f"✅ Ride {new_ride['ride_id']} created successfully!")
                        st.balloons()
                        c1, c2, c3 = st.columns(3)
                        with c1: st.metric("Ride ID", new_ride['ride_id'])
                        with c2: st.metric("Estimated Fare", f"${total}")
                        with c3: st.metric("Distance", f"{distance} km")
                    except Exception as e:
                        st.error(f"❌ Error creating ride: {e}")
        else:
            st.warning("⚠️ Initialize the database to load drivers and riders.")

if __name__ == "__main__":
    main()
