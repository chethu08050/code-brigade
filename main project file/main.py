import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pyttsx3
from io import BytesIO
import time
import smtplib
import numpy as np



# App configuration
st.set_page_config(
    page_title="Spacecraft Telemetry Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown(
    """
    <style>
    .stApp { background-color: #0f1117; color: white; }
    .stButton>button { background-color: #1f77b4; color: white; }
    .stDownloadButton>button { background-color: #2ca02c; color: white; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App header
st.title("🛰️ Universal Spacecraft Telemetry Analyzer")
st.markdown("Advanced analytics platform for spacecraft telemetry data with real-time anomaly detection")

# Define telemetry fields and their properties
telemetry_fields = {
    "temperature": {
        "label": "Temperature",
        "y_label": "°C",
        "thresholds": {"low": 0, "high": 40},
        "alert_msg": lambda val: f"{'Low' if val < 0 else 'High'} temperature detected: {val}°C"
    },
    "pressure": {
        "label": "Pressure",
        "y_label": "atm",
        "thresholds": {"low": 0.8, "high": 1.2},
        "alert_msg": lambda val: f"{'Low' if val < 0.8 else 'High'} pressure detected: {val} atm"
    },
    "velocity": {
        "label": "Velocity",
        "y_label": "m/s",
        "thresholds": {"low": None, "high": None},
        "alert_msg": None
    },
    "battery": {
        "label": "Battery Level",
        "y_label": "%",
        "thresholds": {"low": 20, "high": None},
        "alert_msg": lambda val: f"Battery critically low: {val}%"
    },
    "fuel": {
        "label": "Fuel Level",
        "y_label": "%",
        "thresholds": {"low": 20, "high": None},
        "alert_msg": lambda val: f"Fuel critically low: {val}%"
    }
}

# TTS for alerts
def speak_alerts(alerts):
    try:
        engine = pyttsx3.init()
        for msg in alerts:
            st.info(f"🔊 {msg}")
            engine.say(msg)
            engine.runAndWait()
            time.sleep(1)
    except Exception as e:
        st.error(f"❌ Audio alert error: {e}")

# Highlight cells in dataframe based on thresholds
def highlight_cell(val, col):
    if col in telemetry_fields:
        thresholds = telemetry_fields[col]["thresholds"]
        try:
            if thresholds["low"] is not None and val < thresholds["low"]:
                return 'color: red; background-color: rgba(255, 0, 0, 0.1)'
            if thresholds["high"] is not None and val > thresholds["high"]:
                return 'color: red; background-color: rgba(255, 0, 0, 0.1)'
            # Normal values in green
            return 'color: green'
        except:
            pass
    return ''

def style_dataframe(df):
    return df.style.apply(
        lambda row: [highlight_cell(row[col], col) if col in telemetry_fields and col in df.columns else '' 
                    for col in df.columns],
        axis=1
    )

# Check for anomalies in the data
def detect_anomalies(df):
    alerts = []
    
    for col, meta in telemetry_fields.items():
        if col in df.columns and meta["alert_msg"] is not None:
            thresholds = meta["thresholds"]
            
            if thresholds["low"] is not None and (df[col] < thresholds["low"]).any():
                min_val = df[col].min()
                alerts.append(meta["alert_msg"](min_val))
                
            if thresholds["high"] is not None and (df[col] > thresholds["high"]).any():
                max_val = df[col].max()
                alerts.append(meta["alert_msg"](max_val))
                
    return alerts

# Generate 2D plots for each telemetry field
def create_2d_plots(df):
    tabs = st.tabs([meta["label"] for meta in telemetry_fields.values()])
    
    for idx, (col, meta) in enumerate(telemetry_fields.items()):
        if col in df.columns:
            with tabs[idx]:
                st.subheader(f"{meta['label']} Over Time")
                
                # Create the plot
                fig, ax = plt.subplots(figsize=(10, 5))
                x = df["timestamp"] if "timestamp" in df.columns else df.index
                ax.plot(x, df[col], color='cyan', marker='o')
                ax.set_ylabel(meta["y_label"])
                ax.grid(True)
                
                # Add threshold lines if defined
                if meta["thresholds"]["low"] is not None:
                    ax.axhline(y=meta["thresholds"]["low"], color='r', linestyle='--', 
                              label=f"Low {meta['label']} Threshold")
                if meta["thresholds"]["high"] is not None:
                    ax.axhline(y=meta["thresholds"]["high"], color='r', linestyle='--', 
                              label=f"High {meta['label']} Threshold")
                
                if meta["thresholds"]["low"] is not None or meta["thresholds"]["high"] is not None:
                    ax.legend()
                
                st.pyplot(fig)
                
                # Download PNG
                buf = BytesIO()
                fig.savefig(buf, format="png")
                buf.seek(0)
                st.download_button(
                    f"📥 Download {meta['label']} Graph",
                    buf,
                    file_name=f"{col}_graph.png",
                    mime="image/png"
                )

# Create 3D visualizations
def create_3d_visualizations(df):
    st.header("🌐 3D Telemetry Visualizations")
    
    # Check for required columns for 3D visualization
    vis_cols = ["velocity", "fuel", "battery"]
    if all(col in df.columns for col in vis_cols):
        col1, col2 = st.columns(2)
        
        # Scatter plot
        with col1:
            st.subheader("3D Scatter Plot")
            scatter_fig = px.scatter_3d(
                df, 
                x="velocity", 
                y="fuel", 
                z="battery",
                color="temperature" if "temperature" in df.columns else None,
                size="fuel", 
                hover_data=["timestamp"] if "timestamp" in df.columns else None,
                title="Velocity-Fuel-Battery Relationship"
            )
            st.plotly_chart(scatter_fig, use_container_width=True)
        
        # Mesh visualization
        with col2:
            st.subheader("3D Structured Mesh")
            mesh_fig = go.Figure(data=[
                go.Mesh3d(
                    x=df["velocity"],
                    y=df["fuel"],
                    z=df["battery"],
                    opacity=0.7,
                    color="lightblue",
                    alphahull=0
                )
            ])
            mesh_fig.update_layout(
                scene=dict(
                    xaxis_title="Velocity (m/s)",
                    yaxis_title="Fuel (%)",
                    zaxis_title="Battery (%)"
                )
            )
            st.plotly_chart(mesh_fig, use_container_width=True)
    else:
        st.warning("3D visualization requires velocity, fuel, and battery columns")

# Main sidebar
with st.sidebar:
    st.header("📁 Data Input")
    file = st.file_uploader("Upload Telemetry CSV", type=["csv"])
    
    if file:
        st.success("✅ File loaded")
        
        # Email notification option
        st.subheader("📧 Email Alerts")
        enable_email = st.checkbox("Enable email notifications")
        
        if enable_email:
            email_address = st.text_input("Email address for alerts")
            
            # This would be connected to actual email sending logic
            if st.button("Test Email Connection"):
                st.info("Email test functionality would go here")
    
    # Audio alerts toggle
    st.subheader("🔊 Audio Alerts")
    enable_audio = st.checkbox("Enable audio notifications", value=True)

# Main processing logic
if file:
    try:
        # Load and parse the CSV
        df = pd.read_csv(file)
        
        # Handle timestamp column if present
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d-%m-%Y %H:%M", dayfirst=True, errors="coerce")
            df["timestamp"] = df["timestamp"].astype('datetime64[ns]')   # Force correct type
        
        # Display raw data preview with tabs
        st.header("📊 Data Analysis")
        tab1, tab2 = st.tabs(["Data Preview", "Styled Data"])
        
        with tab1:
            st.dataframe(df, use_container_width=True)
        
        with tab2:
            styled_df = style_dataframe(df)
            st.dataframe(styled_df, use_container_width=True)
        
        # Detect anomalies
        anomalies = detect_anomalies(df)
        
        # Display and speak alerts if any
        if anomalies:
            st.header("⚠️ Critical Alerts")
            for alert in anomalies:
                st.warning(alert)
            
            # Speak alerts if enabled
            if enable_audio:
                speak_alerts(anomalies)
        
        # Create visualization tabs
        st.header("📈 Telemetry Graphs")
        create_2d_plots(df)
        
        # 3D visualizations
        create_3d_visualizations(df)
        
        # Export options
        st.header("📥 Export Analysis")
        
        # Excel download
        out = BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        out.seek(0)
        st.download_button(
            "📊 Download Excel Report", 
            out.getvalue(), 
            file_name="spacecraft_telemetry_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Generate summary stats
        st.header("📑 Summary Statistics")
        st.dataframe(df.describe(), use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Processing error: {e}")
else:
    # No file uploaded yet
    st.info("Please upload a telemetry CSV file. The file should include columns such as 'timestamp', 'temperature', 'pressure', 'velocity', 'battery', and 'fuel'.")
    
    # Show sample data structure
    st.header("📋 Expected Data Format")
    sample_data = {
        "timestamp": ["2025-04-25 09:00:00", "2025-04-25 10:00:00", "2025-04-25 11:00:00"],
        "temperature": [22.5, 23.1, 41.5],
        "pressure": [1.01, 0.98, 1.05],
        "velocity": [1200, 1250, 1300],
        "battery": [95, 90, 85],
        "fuel": [80, 75, 70]
    }
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True)

    # Add after the sidebar file uploader
use_simulated_data = st.sidebar.checkbox("Use simulated data stream")

if use_simulated_data:
    st.sidebar.subheader("Simulation Settings")
    simulation_duration = st.sidebar.slider("Duration (minutes)", 5, 60, 15)
    simulation_freq = st.sidebar.slider("Data frequency (seconds)", 1, 30, 5)
    anomaly_chance = st.sidebar.slider("Anomaly chance (%)", 0, 100, 20)
    
    if st.sidebar.button("Start Simulation"):
        # Generate simulated telemetry data
        sim_start = pd.Timestamp.now() - pd.Timedelta(minutes=simulation_duration)
        sim_end = pd.Timestamp.now()
        sim_index = pd.date_range(sim_start, sim_end, freq=f"{simulation_freq}S")
        
        sim_data = {
            "timestamp": sim_index,
            "temperature": np.random.normal(25, 8, size=len(sim_index)),
            "pressure": np.random.normal(1.0, 0.1, size=len(sim_index)),
            "velocity": np.random.normal(1200, 100, size=len(sim_index)),
            "battery": np.random.normal(80, 10, size=len(sim_index)),
            "fuel": np.random.normal(70, 15, size=len(sim_index))
        }
        
        # Add anomalies based on chance
        if anomaly_chance > 0:
            for field in ["temperature", "pressure", "battery", "fuel"]:
                if np.random.rand() < anomaly_chance/100:
                    anomaly_idx = np.random.choice(range(len(sim_index)), size=max(1, int(len(sim_index)*0.1)))
                    thresholds = telemetry_fields[field]["thresholds"]
                    
                    # Generate values outside thresholds
                    if thresholds["low"] is not None and np.random.choice([True, False]):
                        sim_data[field][anomaly_idx] = np.random.uniform(
                            thresholds["low"] - 20, 
                            thresholds["low"] - 1, 
                            size=len(anomaly_idx)
                        )
                    elif thresholds["high"] is not None:
                        sim_data[field][anomaly_idx] = np.random.uniform(
                            thresholds["high"] + 1, 
                            thresholds["high"] + 20, 
                            size=len(anomaly_idx)
                        )
        
        df = pd.DataFrame(sim_data)
        file = True  # Trick the system to process the simulated data

        # Add to sidebar after the file uploader section
with st.sidebar:
    # Keep existing sidebar code and add:
    st.header("🚀 Mission Profiles")
    
    mission_profiles = {
        "LEO Satellite": {
            "temperature": {"low": -5, "high": 35},
            "pressure": {"low": 0.9, "high": 1.1},
            "battery": {"low": 30, "high": None},
            "fuel": {"low": 25, "high": None}
        },
        "Deep Space Probe": {
            "temperature": {"low": -20, "high": 30},
            "pressure": {"low": 0.7, "high": 1.0},
            "battery": {"low": 40, "high": None},
            "fuel": {"low": 35, "high": None}
        },
        "Mars Mission": {
            "temperature": {"low": -40, "high": 25},
            "pressure": {"low": 0.6, "high": 0.9},
            "battery": {"low": 50, "high": None},
            "fuel": {"low": 40, "high": None}
        },
        "Venus Orbiter": {
            "temperature": {"low": 10, "high": 60},
            "pressure": {"low": 0.8, "high": 1.2},
            "battery": {"low": 35, "high": None},
            "fuel": {"low": 30, "high": None}
        },
        "Lunar Lander": {
            "temperature": {"low": -30, "high": 40},
            "pressure": {"low": 0.85, "high": 1.05},
            "battery": {"low": 45, "high": None},
            "fuel": {"low": 20, "high": None}
        }
    }
    
    selected_profile = st.selectbox("Select mission profile", 
                                   ["Custom"] + list(mission_profiles.keys()))
    
    if selected_profile != "Custom":
        st.info(f"Using {selected_profile} thresholds")
        # Override thresholds with profile values
        for field, values in mission_profiles[selected_profile].items():
            if field in telemetry_fields:
                telemetry_fields[field]["thresholds"] = values
                
        # Show the selected profile's thresholds
        st.subheader("Profile Thresholds")
        profile_data = []
        for field, values in mission_profiles[selected_profile].items():
            if field in telemetry_fields:
                low_val = values["low"] if values["low"] is not None else "N/A"
                high_val = values["high"] if values["high"] is not None else "N/A"
                profile_data.append({
                    "Parameter": telemetry_fields[field]["label"],
                    "Low Threshold": low_val,
                    "High Threshold": high_val,
                    "Unit": telemetry_fields[field]["y_label"]
                })
        
        st.dataframe(pd.DataFrame(profile_data), use_container_width=True)
        
        # Option to save current thresholds as a custom profile
        if st.button("Save Current as Custom Profile"):
            with st.expander("Create Custom Profile"):
                profile_name = st.text_input("Profile Name")
                if st.button("Save Profile") and profile_name:
                    # Would save to a database or file in a real implementation
                    st.success(f"Profile '{profile_name}' saved successfully!")
    else:
        # Show custom threshold adjustment UI
        st.subheader("Custom Thresholds")
        for field, meta in telemetry_fields.items():
            st.markdown(f"**{meta['label']}**")
            col1, col2 = st.columns(2)
            
            with col1:
                current_low = meta["thresholds"].get("low", None)
                new_low = st.number_input(
                    f"Low {meta['label']} ({meta['y_label']})",
                    value=float(current_low) if current_low is not None else 0.0,
                    step=0.1
                )
                telemetry_fields[field]["thresholds"]["low"] = new_low if new_low != 0.0 else None
                
            with col2:
                current_high = meta["thresholds"].get("high", None)
                new_high = st.number_input(
                    f"High {meta['label']} ({meta['y_label']})",
                    value=float(current_high) if current_high is not None else 0.0,
                    step=0.1
                )
                telemetry_fields[field]["thresholds"]["high"] = new_high if new_high != 0.0 else None

                # Add near the top of main analysis section
if file:
    # Health status indicators
    st.header("🛡️ System Health Status")
    status_cols = st.columns(len(telemetry_fields))
    
    # For each telemetry field, create a gauge
    for idx, (field, meta) in enumerate(telemetry_fields.items()):
        if field in df.columns:
            with status_cols[idx]:
                current_val = df[field].iloc[-1]
                thresholds = meta["thresholds"]
                
                # Calculate health status
                if ((thresholds["low"] is not None and current_val < thresholds["low"]) or
                    (thresholds["high"] is not None and current_val > thresholds["high"])):
                    status = "Critical"
                    color = "red"
                elif ((thresholds["low"] is not None and current_val < thresholds["low"] * 1.1) or
                      (thresholds["high"] is not None and current_val > thresholds["high"] * 0.9)):
                    status = "Warning"
                    color = "orange"
                else:
                    status = "Nominal" 
                    color = "green"
                
                # Create gauge
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=current_val,
                    title={"text": meta["label"]},
                    gauge={
                        "axis": {"range": [df[field].min() * 0.9, df[field].max() * 1.1]},
                        "bar": {"color": color},
                        "steps": [
                            {"range": [df[field].min() * 0.9, df[field].max() * 1.1], "color": "lightgray"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": thresholds["low"] if thresholds["low"] is not None else (
                                thresholds["high"] if thresholds["high"] is not None else df[field].mean()
                            )
                        }
                    }
                ))
                gauge.update_layout(height=200)
                st.plotly_chart(gauge, use_container_width=True)
                st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)

                