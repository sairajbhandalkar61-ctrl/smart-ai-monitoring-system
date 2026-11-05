import os
import time
import requests
import pandas as pd
import numpy as np
import streamlit as st

# Configuration
API_URL = os.getenv("CLOUD_API_URL", "http://127.0.0.1:8000").rstrip("/")

# Page Configuration
st.set_page_config(
    page_title="SENTINEL AI — Crowd Intelligence Cloud Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Command-Center CSS (Fully Mobile Responsive)
st.markdown("""
<style>
    /* Main App Background & Typography */
    .stApp {
        background-color: #080D18;
        color: #F1F5F9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0B1220 !important;
        border-right: 1px solid #1E293B;
    }
    
    /* Card Container */
    .sentinel-card {
        background: #111B2B;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    /* Header Gradient */
    .sentinel-header {
        font-size: 1.65rem;
        font-weight: 700;
        background: linear-gradient(90deg, #22D3EE 0%, #2DD4BF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    
    .sentinel-subtitle {
        color: #94A3B8;
        font-size: 0.85rem;
        margin-bottom: 20px;
    }
    
    /* Metric Card */
    .metric-box {
        background: #162337;
        border: 1px solid #23354E;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
        margin-bottom: 10px;
    }
    .metric-title {
        color: #94A3B8;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .metric-val {
        color: #F1F5F9;
        font-size: 1.55rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 3px;
    }
    .metric-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.70rem;
        font-weight: 600;
        margin-top: 5px;
    }
    .pill-cyan { background: rgba(34, 211, 238, 0.15); color: #22D3EE; border: 1px solid rgba(34, 211, 238, 0.3); }
    .pill-teal { background: rgba(45, 212, 191, 0.15); color: #2DD4BF; border: 1px solid rgba(45, 212, 191, 0.3); }
    .pill-green { background: rgba(34, 197, 94, 0.15); color: #22C55E; border: 1px solid rgba(34, 197, 94, 0.3); }
    .pill-amber { background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
    .pill-rose { background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* Custom Streamlit Buttons */
    .stButton > button {
        background: #162337;
        color: #22D3EE;
        border: 1px solid #22D3EE;
        border-radius: 6px;
        font-weight: 600;
        padding: 6px 14px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #22D3EE;
        color: #080D18;
        border-color: #22D3EE;
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.3);
    }

    /* Mobile Responsive Viewport Fixes */
    @media (max-width: 768px) {
        .sentinel-header { font-size: 1.35rem; }
        .metric-val { font-size: 1.3rem; }
        .sentinel-card { padding: 14px; }
        .metric-box { padding: 10px 12px; }
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# --- Helper API Fetch Functions ---
def fetch_telemetry():
    try:
        r = requests.get(f"{API_URL}/api/v1/telemetry", timeout=3.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    # Fallback offline telemetry schema
    return {
        "active": False,
        "device_id": "dell-edge-01",
        "camera_source": "Dell Latitude 3420 Webcam",
        "fps": 0.0,
        "inference_latency_ms": 0.0,
        "cpu_percent": 0.0,
        "memory_mb": 0.0,
        "raw_detections_count": 0,
        "active_tracks_count": 0,
        "estimated_occupancy": 0,
        "entries": 0,
        "exits": 0,
        "tripwire_y": 240,
        "activity": "Idle",
        "activity_confidence": 1.0,
        "activity_uncertain": False,
        "quality_status": "Awaiting Edge Telemetry",
        "quality_reliable": True,
        "blur_score": 0.0,
        "brightness": 0.0,
        "zones": [
            {"zone_id": "zone-a", "name": "Zone A (Corridor)", "capacity": 10, "current_count": 0, "density_percentage": 0.0, "status": "Normal"},
            {"zone_id": "zone-b", "name": "Zone B (Hall)", "capacity": 15, "current_count": 0, "density_percentage": 0.0, "status": "Normal"}
        ],
        "recent_alerts": [],
        "edge_connected": False
    }

def fetch_alerts():
    try:
        r = requests.get(f"{API_URL}/api/v1/alerts?limit=20", timeout=3.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def fetch_history():
    try:
        r = requests.get(f"{API_URL}/api/v1/analytics/history?limit=60", timeout=3.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def fetch_edge_devices():
    try:
        r = requests.get(f"{API_URL}/api/v1/edge/status", timeout=3.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"total_registered_devices": 0, "online_devices": 0, "devices": []}

# -------------------------------------------------------------------------------------------------
# AUTHENTICATION GATEWAY
# -------------------------------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("""
        <div style="max-width: 440px; margin: 40px auto 20px auto; text-align: center;">
            <div class="sentinel-header" style="font-size: 2.2rem;">🛡️ SENTINEL AI</div>
            <div class="sentinel-subtitle">Enterprise Edge & Cloud Crowd Monitoring Center</div>
        </div>
    """, unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Secure System Access")
        st.caption("Enter institutional credentials to access the cloud monitoring console.")

        username_input = st.text_input("Username", value="admin")
        password_input = st.text_input("Password", type="password", value="SentinelAdmin2026!")

        if st.button("Sign In to Sentinel Command Center", use_container_width=True):
            try:
                r = requests.post(f"{API_URL}/api/v1/auth/login", json={"username": username_input, "password": password_input}, timeout=4.0)
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.authenticated = True
                    st.session_state.user = data
                    st.success(f"Welcome, {data['username']} ({data['role'].upper()})")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please verify your username and password.")
            except Exception as e:
                # Local fallback check if API offline
                if username_input == "admin" and password_input == "SentinelAdmin2026!":
                    st.session_state.authenticated = True
                    st.session_state.user = {"username": "admin", "role": "admin"}
                    st.success("Authenticated in Standalone Offline Mode.")
                    st.rerun()
                else:
                    st.error(f"Authentication Service Unavailable: {e}")

        st.markdown("""
            <hr style="border-color: #1E293B; margin: 16px 0;">
            <div style="font-size: 0.72rem; color: #64748B;">
                <b>Default Accounts:</b><br>
                • <code>admin</code> / <code>SentinelAdmin2026!</code> (Administrator)<br>
                • <code>operator</code> / <code>Operator2026!</code> (Operator)
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------------------------------------------------------
# AUTHENTICATED APPLICATION
# -------------------------------------------------------------------------------------------------
telemetry = fetch_telemetry()
user_info = st.session_state.user or {"username": "User", "role": "viewer"}
edge_info = fetch_edge_devices()

# Sidebar Brand & User Profile
with st.sidebar:
    st.markdown('<div class="sentinel-header">🛡️ SENTINEL AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Crowd Intelligence & Occupancy Platform</div>', unsafe_allow_html=True)

    # Edge Connectivity Status Badge
    is_edge_online = telemetry.get("edge_connected", False) or telemetry.get("active", False)
    status_color = "#22C55E" if is_edge_online else "#EF4444"
    status_text = "DELL EDGE ONLINE" if is_edge_online else "DELL EDGE OFFLINE"

    st.markdown(f"""
        <div style="background: #111B2B; padding: 10px 14px; border-radius: 6px; border: 1px solid #1E293B; margin-bottom: 16px;">
            <div style="font-size: 0.70rem; color: #94A3B8; text-transform: uppercase;">Edge Node Link</div>
            <div style="color: {status_color}; font-weight: 700; font-size: 0.85rem; display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                <span style="height: 8px; width: 8px; background-color: {status_color}; border-radius: 50%; display: inline-block;"></span>
                {status_text}
            </div>
            <div style="font-size: 0.70rem; color: #64748B; margin-top: 4px;">Host: Dell Latitude 3420 (Win 11)</div>
        </div>
    """, unsafe_allow_html=True)

    # User Profile Pill
    st.markdown(f"""
        <div style="font-size: 0.75rem; color: #94A3B8; margin-bottom: 12px;">
            👤 Signed in as: <b style="color: #22D3EE;">{user_info['username']}</b> 
            <span class="metric-pill pill-cyan">{user_info['role'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "1. Overview",
            "2. Live Monitoring",
            "3. Camera Management",
            "4. Monitoring Zones",
            "5. Occupancy Analytics",
            "6. Activity Intelligence",
            "7. Entry & Exit Analytics",
            "8. Alerts Center",
            "9. Historical Reports",
            "10. AI Model Insights",
            "11. System Health",
            "12. Settings"
        ],
        index=0
    )

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    st.markdown("""
        <div style="font-size: 0.70rem; color: #64748B; margin-top: 14px;">
            <b>Author:</b> Sairaj Bhandalkar (MITCOM-CA)<br>
            <b>Guide:</b> Prof. Pallavi Gaikwad<br>
            <b>Institution:</b> MIT ADT University, Pune
        </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------
# PAGE 1: OVERVIEW
# -------------------------------------------------------------------------------------------------
if page == "1. Overview":
    st.markdown('<div class="sentinel-header">System Overview & Facility Pulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Real-time macro telemetry across all monitored campus zones.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Estimated Occupancy</div>
                <div class="metric-val">{telemetry['estimated_occupancy']}</div>
                <span class="metric-pill pill-cyan">Reconciled Net Count</span>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Active Pedestrians</div>
                <div class="metric-val">{telemetry['active_tracks_count']}</div>
                <span class="metric-pill pill-teal">Tracked in View</span>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Activity Classification</div>
                <div class="metric-val">{telemetry['activity']}</div>
                <span class="metric-pill pill-green">Confidence: {int(telemetry['activity_confidence']*100)}%</span>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Edge Framerate</div>
                <div class="metric-val">{telemetry['fps']} <span style="font-size: 0.85rem; color: #94A3B8;">FPS</span></div>
                <span class="metric-pill pill-amber">Latency: {telemetry['inference_latency_ms']} ms</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.markdown("### 📊 Monitored Zone Capacities")
        zone_data = []
        for z in telemetry.get('zones', []):
            zone_data.append({
                "Zone ID": z["zone_id"],
                "Zone Name": z["name"],
                "Occupancy": z["current_count"],
                "Capacity": z["capacity"],
                "Density %": f"{z['density_percentage']}%",
                "Status": z["status"]
            })
        st.dataframe(pd.DataFrame(zone_data), use_container_width=True, hide_index=True)

    with col_right:
        st.markdown("### 🚨 Active Safety Alerts")
        alerts = fetch_alerts()
        if alerts:
            for alt in alerts[:4]:
                st.warning(f"**[{alt['severity'].upper()}]** {alt['title']} — {alt['desc']} ({alt['time']})")
        else:
            st.info("No active anomalies detected. Facility operating within normal parameters.")

# -------------------------------------------------------------------------------------------------
# PAGE 2: LIVE MONITORING
# -------------------------------------------------------------------------------------------------
elif page == "2. Live Monitoring":
    st.markdown('<div class="sentinel-header">Live Intelligent Crowd Vision</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Real-time edge computer vision stream with bounding boxes, temporary track IDs, and zone analytics.</div>', unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns([1.5, 2, 2])
    with ctrl1:
        st.markdown(f"**Connected Node:** `dell-edge-01`")
    with ctrl2:
        st.markdown(f"**Camera Source:** `{telemetry.get('camera_source', 'Dell Integrated Webcam')}`")
    with ctrl3:
        quality_str = telemetry.get("quality_status", "Assessing...")
        quality_badge = "pill-green" if telemetry.get("quality_reliable", True) else "pill-rose"
        st.markdown(f'**Feed Reliability:** <span class="metric-pill {quality_badge}">{quality_str}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    v_col, hud_col = st.columns([3.6, 1.4])

    with v_col:
        video_placeholder = st.empty()
        if is_edge_online:
            # Display live MJPEG stream if local, or stream snapshot
            stream_url = f"{API_URL}/api/v1/stream/live"
            video_placeholder.markdown(f"""
                <div style="background: #111B2B; border: 1px solid #1E293B; border-radius: 10px; overflow: hidden; text-align: center;">
                    <img src="{stream_url}" style="width: 100%; max-height: 480px; object-fit: contain;" onerror="this.parentElement.innerHTML='<div style=\\'padding: 80px 20px; color: #94A3B8;\\'><h3>Live Telemetry Connected</h3><p>Camera frames are processed on the Dell laptop CPU. Numerical telemetry is updating live on the right.</p></div>';"/>
                </div>
            """, unsafe_allow_html=True)
        else:
            video_placeholder.markdown("""
                <div style="background: #111B2B; border: 2px dashed #1E293B; border-radius: 10px; height: 380px; display: flex; align-items: center; justify-content: center; flex-direction: column; text-align: center; padding: 20px;">
                    <h3 style="color: #64748B;">Dell Edge Agent Standby / Offline</h3>
                    <p style="color: #475569; max-width: 400px;">To push live footage from the Dell Latitude 3420 webcam to this cloud dashboard, start the edge agent using <code>.\\scripts\\run_edge_agent.ps1</code> on the laptop.</p>
                </div>
            """, unsafe_allow_html=True)

    with hud_col:
        st.markdown(f"""
            <div class="sentinel-card">
                <div class="metric-title">ESTIMATED OCCUPANCY</div>
                <div class="metric-val" style="color: #22D3EE;">{telemetry['estimated_occupancy']}</div>
                <hr style="border-color: #1E293B; margin: 10px 0;">
                <div style="font-size: 0.8rem; color: #94A3B8;">Raw Detections: <b>{telemetry['raw_detections_count']}</b></div>
                <div style="font-size: 0.8rem; color: #94A3B8;">Active Tracks: <b>{telemetry['active_tracks_count']}</b></div>
                <div style="font-size: 0.8rem; color: #94A3B8;">Tripwire Entries: <b>{telemetry['entries']}</b></div>
                <div style="font-size: 0.8rem; color: #94A3B8;">Tripwire Exits: <b>{telemetry['exits']}</b></div>
            </div>
            <div class="sentinel-card">
                <div class="metric-title">EDGE PERFORMANCE</div>
                <div style="font-size: 0.82rem; margin-top: 4px;">Framerate: <b>{telemetry['fps']} FPS</b></div>
                <div style="font-size: 0.82rem;">Inference: <b>{telemetry['inference_latency_ms']} ms</b></div>
                <div style="font-size: 0.82rem;">Dell CPU Load: <b>{telemetry['cpu_percent']}%</b></div>
                <div style="font-size: 0.82rem;">Dell RAM: <b>{telemetry['memory_mb']} MB</b></div>
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------
# PAGE 3: CAMERA & EDGE MANAGEMENT
# -------------------------------------------------------------------------------------------------
elif page == "3. Camera Management":
    st.markdown('<div class="sentinel-header">Edge Devices & Registered Cameras</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Manage edge hardware nodes, connected webcams, and network streams.</div>', unsafe_allow_html=True)

    devs = edge_info.get("devices", [])
    if devs:
        dev_rows = []
        for d in devs:
            dev_rows.append({
                "Device ID": d.get("device_id"),
                "Device Name": d.get("device_name"),
                "Camera Interface": d.get("camera_source"),
                "Status": d.get("status"),
                "CPU %": f"{d.get('cpu_percent')}%",
                "RAM": f"{d.get('memory_mb')} MB",
                "Last Heartbeat": f"{d.get('seconds_since_heartbeat', 0)}s ago"
            })
        st.dataframe(pd.DataFrame(dev_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No remote edge devices currently sending heartbeats. Start the Dell Edge Agent to see live telemetry here.")

    st.markdown("### 📋 Dell Latitude 3420 Edge Agent Configuration")
    st.code(f"""
# Environment file for Dell Edge Laptop (.env.edge)
CLOUD_API_URL={API_URL}
EDGE_DEVICE_ID=dell-edge-01
EDGE_DEVICE_TOKEN=sentinel_edge_secure_token_2026
CAMERA_INDEX=0
DETECTOR_TYPE=ssdlite
    """, language="ini")

# -------------------------------------------------------------------------------------------------
# PAGE 4: MONITORING ZONES
# -------------------------------------------------------------------------------------------------
elif page == "4. Monitoring Zones":
    st.markdown('<div class="sentinel-header">Spatial Monitoring Zones & Geometry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Polygon Region of Interest (ROI) definitions and occupancy thresholding.</div>', unsafe_allow_html=True)

    for z in telemetry.get("zones", []):
        with st.expander(f"📍 {z['name']} ({z['zone_id']}) — Capacity: {z['capacity']}", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Current Headcount:** {z['current_count']}")
                st.write(f"**Density Utilization:** {z['density_percentage']}%")
                st.write(f"**Safety Status:** `{z['status']}`")
            with col_b:
                st.write(f"**Zone Geometry:** Polygon coordinates active on edge processor.")

# -------------------------------------------------------------------------------------------------
# PAGE 5: OCCUPANCY ANALYTICS
# -------------------------------------------------------------------------------------------------
elif page == "5. Occupancy Analytics":
    st.markdown('<div class="sentinel-header">Historical Occupancy Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Temporal trends, peak densities, and facility utilization patterns.</div>', unsafe_allow_html=True)

    records = fetch_history()
    if records:
        df = pd.DataFrame(records)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        st.markdown("### 📈 Recent Occupancy Timeline")
        chart_data = df.set_index('datetime')[['detected_count', 'tripwire_occupancy', 'entries', 'exits']]
        st.line_chart(chart_data)
        st.markdown("### 📋 Telemetry Event Log")
        st.dataframe(df[['datetime', 'detected_count', 'active_tracks', 'tripwire_occupancy', 'activity_class', 'confidence', 'blur_score']].tail(15), use_container_width=True)
    else:
        st.info("No persistent telemetry recorded yet. Start monitoring to log occupancy trends.")

# -------------------------------------------------------------------------------------------------
# PAGE 6: ACTIVITY INTELLIGENCE
# -------------------------------------------------------------------------------------------------
elif page == "6. Activity Intelligence":
    st.markdown('<div class="sentinel-header">Activity Intelligence & Kinematic Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Kinematic crowd motion analysis, velocity dispersion, and multi-class probability scoring.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Classified State", telemetry.get('activity', 'Low Activity'))
    c2.metric("Classification Confidence", f"{int(telemetry.get('activity_confidence', 1.0)*100)}%")
    c3.metric("Operator Verification Required", "YES" if telemetry.get('activity_uncertain') else "NO")

# -------------------------------------------------------------------------------------------------
# PAGE 7: ENTRY & EXIT ANALYTICS
# -------------------------------------------------------------------------------------------------
elif page == "7. Entry & Exit Analytics":
    st.markdown('<div class="sentinel-header">Virtual Tripwire & Flow Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Bidirectional pedestrian crossing detection and rate of entry/exit.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Cumulative Entries", telemetry.get('entries', 0))
    c2.metric("Total Cumulative Exits", telemetry.get('exits', 0))
    c3.metric("Net Flow (Entries - Exits)", telemetry.get('entries', 0) - telemetry.get('exits', 0))

# -------------------------------------------------------------------------------------------------
# PAGE 8: ALERTS CENTER
# -------------------------------------------------------------------------------------------------
elif page == "8. Alerts Center":
    st.markdown('<div class="sentinel-header">Safety Alerts & Incident Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Real-time anomaly notifications, quality drops, and threshold triggers.</div>', unsafe_allow_html=True)

    alerts = fetch_alerts()
    if alerts:
        for alt in alerts:
            col_x, col_y = st.columns([4, 1])
            with col_x:
                badge = "🔴" if alt.get('severity') == "high" else "🟡"
                st.write(f"{badge} **[{alt.get('severity','').upper()}] {alt.get('title','')}** — {alt.get('desc','')} ({alt.get('time','')})")
            with col_y:
                if not alt.get('acknowledged'):
                    if st.button("Acknowledge", key=alt.get('id')):
                        try:
                            requests.post(f"{API_URL}/api/v1/alerts/{alt['id']}/acknowledge")
                            st.rerun()
                        except Exception:
                            pass
                else:
                    st.caption("✅ Acknowledged")
    else:
        st.info("No active alerts in the incident log.")

# -------------------------------------------------------------------------------------------------
# PAGE 9: HISTORICAL REPORTS
# -------------------------------------------------------------------------------------------------
elif page == "9. Historical Reports":
    st.markdown('<div class="sentinel-header">Historical Audit & Compliance Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Export facility occupancy logs for compliance, security reviews, and research audits.</div>', unsafe_allow_html=True)

    records = fetch_history()
    if records:
        df = pd.DataFrame(records)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Historical Telemetry (CSV)",
            data=csv,
            file_name="sentinel_occupancy_telemetry.csv",
            mime="text/csv"
        )
        st.dataframe(df.head(20), use_container_width=True)
    else:
        st.warning("No records found in database.")

# -------------------------------------------------------------------------------------------------
# PAGE 10: AI MODEL INSIGHTS
# -------------------------------------------------------------------------------------------------
elif page == "10. AI Model Insights":
    st.markdown('<div class="sentinel-header">Computer Vision Model Benchmarking</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Empirical comparison between Haar Cascade baseline and SSDLite320 Deep Learning detector.</div>', unsafe_allow_html=True)

    comparison = [
        {"Metric": "Target Object", "Haar Cascade Baseline": "Faces & Upper-Body", "SSDLite320 MobileNetV3 (Proposed)": "Full Pedestrian Body (COCO)"},
        {"Metric": "Model Size", "Haar Cascade Baseline": "0.93 MB", "SSDLite320 MobileNetV3 (Proposed)": "13.4 MB"},
        {"Metric": "Intel Core i5 Latency", "Haar Cascade Baseline": "39.91 ms (25.05 FPS)", "SSDLite320 MobileNetV3 (Proposed)": "110.98 ms (9.01 FPS)"},
        {"Metric": "Occlusion Resilience", "Haar Cascade Baseline": "Fails on sideways/backwards heads", "SSDLite320 MobileNetV3 (Proposed)": "Robust across 360-degree angles"},
        {"Metric": "Tracking Stability", "Haar Cascade Baseline": "High count flicker (variance 0.21)", "SSDLite320 MobileNetV3 (Proposed)": "100% flicker elimination"}
    ]
    st.dataframe(pd.DataFrame(comparison), use_container_width=True, hide_index=True)

# -------------------------------------------------------------------------------------------------
# PAGE 11: SYSTEM HEALTH
# -------------------------------------------------------------------------------------------------
elif page == "11. System Health":
    st.markdown('<div class="sentinel-header">Edge Hardware & Environment Health</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Diagnostics for Dell Latitude 3420 CPU, memory, and capture thread.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Dell CPU Utilization", f"{telemetry.get('cpu_percent', 0.0)}%")
    c2.metric("Dell Memory (RSS)", f"{telemetry.get('memory_mb', 0.0)} MB")
    c3.metric("Cloud API Connectivity", "CONNECTED (HTTP 200)" if is_edge_online else "OFFLINE / DISCONNECTED")

# -------------------------------------------------------------------------------------------------
# PAGE 12: SETTINGS
# -------------------------------------------------------------------------------------------------
elif page == "12. Settings":
    st.markdown('<div class="sentinel-header">System Settings & Privacy Policies</div>', unsafe_allow_html=True)
    st.markdown('<div class="sentinel-subtitle">Tune computer vision sensitivity and privacy-preservation rules.</div>', unsafe_allow_html=True)

    st.markdown("### 🔒 Privacy Controls")
    st.checkbox("Enforce No Raw Video Storage (Default: Active)", value=True, disabled=True)
    st.checkbox("Zero Biometric Facial Recognition Guarantee", value=True, disabled=True)
    st.checkbox("Ephemeral Temporary Track IDs Only", value=True, disabled=True)
    st.caption("Privacy policies are enforced in the core edge computer vision pipeline.")
