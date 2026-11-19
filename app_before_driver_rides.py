"""
app.py
Cab Flow - Delhi NCR Mobility Portal with Interactive Live Maps & Simple Language.
Features:
- Dual Portal: Customer (Easy Cab Booking) and Driver (Live Demand Map).
- OpenStreetMap / Leaflet interactive maps:
  * Customer Map: Shows Pickup point, Drop point, distance, and direct route line with animated car.
  * Driver Map: Live NCR Heatmap Circles showing where demand is High (Red/Orange) vs Low (Green).
- Simple, clear everyday language for easy understanding.
- Zero emojis (clean vector icons only).
- Dark and Light mode support.
- Fully connected to the backend Machine Learning API (port 8000).
"""

import os
import json
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# Delhi NCR Locations & Real Coordinates Matrix
NCR_LOCATIONS_MAP = {
    "Barakhamba Road, Connaught Place": [28.6315, 77.2215],
    "Central Secretariat, Central Delhi": [28.6186, 77.2089],
    "Chanakyapuri (Embassy Zone)": [28.5983, 77.1895],
    "Chandni Chowk, Old Delhi": [28.6506, 77.2303],
    "Delhi Gate, Central Delhi": [28.6406, 77.2405],
    "Pragati Maidan / Bharat Mandapam": [28.6182, 77.2425],
    "AIIMS, South Delhi": [28.5672, 77.2100],
    "Hauz Khas Social, South Delhi": [28.5528, 77.1950],
    "Greater Kailash (M-Block), South Delhi": [28.5492, 77.2425],
    "Saket District Centre, South Delhi": [28.5284, 77.2185],
    "Nehru Place IT Hub, South Delhi": [28.5494, 77.2528],
    "Malviya Nagar, South Delhi": [28.5398, 77.2066],
    "Mehrauli / Qutub Minar, South Delhi": [28.5244, 77.1855],
    "Badarpur Border, South East Delhi": [28.5034, 77.3012],
    "Akshardham, East Delhi": [28.6127, 77.2773],
    "Anand Vihar ISBT, East Delhi": [28.6469, 77.3160],
    "Laxmi Nagar Metro Hub, East Delhi": [28.6304, 77.2772],
    "Dilshad Garden, East Delhi": [28.6759, 77.3210],
    "Tilak Nagar / Rajouri Garden, West Delhi": [28.6415, 77.1060],
    "Rohini Sector 18 / West Delhi Hub": [28.7292, 77.1260],
    "Dwarka Sector 21, South West Delhi": [28.5523, 77.0583],
    "Indira Gandhi International Airport (DEL T3)": [28.5562, 77.1000],
    "Vishwavidyalaya (Delhi University North Campus)": [28.6974, 77.2074],
    "Cyber City / Cyber Hub, DLF Gurugram": [28.4952, 77.0895],
    "Ambience Mall, Gurugram": [28.5042, 77.0967],
    "Udyog Vihar Phase 1-5, Gurugram": [28.5065, 77.0782],
    "Sohna Road / Golf Course Extn, Gurugram": [28.4180, 77.0420],
    "Palam Vihar, Gurugram": [28.5132, 77.0450],
    "Khandsa / Manesar Industrial Corridor": [28.3750, 76.9420],
    "Noida Sector 18 (Atta Market / Mall of India)": [28.5708, 77.3261],
    "Noida Electronic City / Sector 62": [28.6280, 77.3649],
    "Ghaziabad Railway Station / Hub": [28.6678, 77.4320],
    "Faridabad Sector 15 / Bata Chowk": [28.3965, 77.3150],
    "New Delhi Railway Station (Paharganj)": [28.6429, 77.2195],
    "Old Delhi Railway Station (Chandni Chowk)": [28.6565, 77.2285]
}

NCR_LOCATIONS = list(NCR_LOCATIONS_MAP.keys())

st.set_page_config(
    page_title="Cab Flow | Delhi NCR Cab Booking & Driver Demand Map",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Theme State
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

is_dark = st.session_state.theme_mode == "Dark"

# Top Bar Switcher
bar_col1, bar_col2 = st.columns([8, 2])
with bar_col2:
    theme_choice = st.radio(
        "Display Mode",
        ["Dark", "Light"],
        horizontal=True,
        index=0 if is_dark else 1,
        label_visibility="collapsed"
    )
    if theme_choice != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_choice
        st.rerun()

# Theme Colors
bg_hex = "#06080E" if is_dark else "#F8FAFC"
surface_hex = "#0D121D" if is_dark else "#FFFFFF"
border_hex = "#1E2A3E" if is_dark else "#E2E8F0"
text_main = "#F8FAFC" if is_dark else "#0F172A"
text_sub = "#94A3B8" if is_dark else "#475569"
text_dim = "#64748B" if is_dark else "#94A3B8"
input_bg = "#090D15" if is_dark else "#F1F5F9"
accent_hex = "#2563EB"

html_application = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<!-- Leaflet OpenStreetMap Engine -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<style>
    * {{
        box-sizing: border-box;
        margin: 0; padding: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    body {{
        background: {bg_hex};
        color: {text_main};
        padding: 10px 18px 40px;
        overflow-x: hidden;
        min-height: 100vh;
        position: relative;
    }}
    #bg-canvas {{
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        z-index: 0;
    }}
    .wrap {{
        position: relative;
        z-index: 1;
        max-width: 1420px;
        margin: 0 auto;
    }}

    /* Top Brand Bar */
    .brand-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 22px rgba(0,0,0,{"0.3" if is_dark else "0.04"});
        animation: fadeIn 0.4s ease;
    }}
    .brand-title {{
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .brand-badge {{
        background: linear-gradient(135deg, {accent_hex}, #06B6D4);
        color: #fff;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.8px;
    }}
    .status-badge {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        color: {text_sub};
        font-family: 'JetBrains Mono', monospace;
    }}
    .live-dot {{
        width: 9px; height: 9px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 10px #10B981;
        animation: pulse 1.6s infinite;
    }}

    /* Role Switch Bar */
    .role-container {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 22px;
        animation: fadeIn 0.5s ease;
    }}
    .role-title {{
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 6px;
    }}
    .role-subtitle {{
        font-size: 0.88rem;
        color: {text_sub};
        margin-bottom: 16px;
    }}
    .role-switch-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }}
    .role-btn {{
        background: {input_bg};
        border: 2px solid {border_hex};
        border-radius: 14px;
        padding: 16px 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: all 0.25s ease;
        text-align: left;
    }}
    .role-btn:hover {{
        border-color: {accent_hex};
        transform: translateY(-2px);
    }}
    .role-btn.active {{
        border-color: {accent_hex};
        background: rgba(37,99,235,{"0.12" if is_dark else "0.08"});
        box-shadow: 0 0 20px rgba(37,99,235,0.22);
    }}
    .role-icon {{
        width: 48px; height: 48px;
        border-radius: 12px;
        background: rgba(37,99,235,0.15);
        color: #60A5FA;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        flex-shrink: 0;
    }}
    .role-btn.active .role-icon {{
        background: {accent_hex};
        color: #fff;
    }}
    .role-name {{
        font-size: 1.05rem;
        font-weight: 800;
        color: {text_main};
    }}
    .role-desc {{
        font-size: 0.82rem;
        color: {text_sub};
        margin-top: 3px;
    }}

    /* Card Layouts */
    .view-section {{
        display: none;
        animation: fadeIn 0.4s ease;
    }}
    .view-section.active {{
        display: block;
    }}
    .card {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,{"0.25" if is_dark else "0.04"});
        margin-bottom: 22px;
    }}
    .portal-grid {{
        display: grid;
        grid-template-columns: 1.1fr 1.3fr;
        gap: 22px;
    }}
    @media (max-width: 1024px) {{
        .portal-grid {{ grid-template-columns: 1fr; }}
        .role-switch-grid {{ grid-template-columns: 1fr; }}
    }}

    .section-title {{
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .section-desc {{
        font-size: 0.85rem;
        color: {text_sub};
        margin-bottom: 18px;
    }}

    /* Inputs */
    .form-group {{
        margin-bottom: 16px;
    }}
    .form-label {{
        display: block;
        font-size: 0.82rem;
        font-weight: 700;
        color: {text_sub};
        margin-bottom: 6px;
    }}
    .form-select {{
        width: 100%;
        background: {input_bg};
        border: 1px solid {border_hex};
        border-radius: 10px;
        padding: 12px 14px;
        color: {text_main};
        font-size: 0.92rem;
        outline: none;
        cursor: pointer;
        transition: border 0.2s;
    }}
    .form-select:focus {{
        border-color: {accent_hex};
    }}

    /* Ride Tier Selection */
    .ride-options {{
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 18px;
    }}
    .ride-card {{
        background: {input_bg};
        border: 1px solid {border_hex};
        border-radius: 12px;
        padding: 14px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s;
    }}
    .ride-card:hover {{
        border-color: {accent_hex};
        transform: translateX(4px);
    }}
    .ride-card.selected {{
        border-color: {accent_hex};
        background: rgba(37,99,235,{"0.15" if is_dark else "0.08"});
    }}
    .ride-name {{
        font-size: 0.98rem;
        font-weight: 800;
    }}
    .ride-meta {{
        font-size: 0.8rem;
        color: {text_sub};
        margin-top: 2px;
    }}
    .ride-price {{
        font-size: 1.15rem;
        font-weight: 800;
        color: #38BDF8;
        text-align: right;
    }}
    .ride-eta {{
        font-size: 0.74rem;
        color: {text_dim};
        text-align: right;
    }}

    /* Action Buttons */
    .btn-action {{
        width: 100%;
        background: linear-gradient(135deg, {accent_hex}, #1D4ED8);
        border: none;
        color: #FFFFFF;
        font-size: 0.96rem;
        font-weight: 700;
        padding: 14px;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.25s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        box-shadow: 0 4px 14px rgba(37,99,235,0.35);
    }}
    .btn-action:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37,99,235,0.5);
    }}

    /* Map Containers */
    .map-box {{
        width: 100%;
        height: 380px;
        border-radius: 14px;
        border: 1px solid {border_hex};
        overflow: hidden;
        position: relative;
        margin-bottom: 18px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
    }}
    #map-customer, #map-driver {{
        width: 100%;
        height: 100%;
    }}

    /* Info Tiles */
    .info-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 16px;
    }}
    .info-tile {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }}
    .info-label {{
        font-size: 0.74rem;
        font-weight: 700;
        color: {text_dim};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .info-val {{
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 4px;
        color: {text_main};
    }}

    /* Driver Hotspot Cards */
    .hotspot-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
        gap: 16px;
        margin-top: 18px;
    }}
    .hotspot-card {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 14px;
        padding: 18px;
        transition: all 0.2s ease;
    }}
    .hotspot-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(37,99,235,0.5);
    }}
    .hotspot-card.high {{ border-left: 4px solid #EF4444; }}
    .hotspot-card.moderate {{ border-left: 4px solid #F59E0B; }}
    .hotspot-card.low {{ border-left: 4px solid #10B981; }}

    .badge-high {{ background: rgba(239,68,68,0.18); color: #F87171; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 0.72rem; }}
    .badge-mod {{ background: rgba(245,158,11,0.18); color: #FBBF24; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 0.72rem; }}
    .badge-low {{ background: rgba(16,185,129,0.18); color: #34D399; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 0.72rem; }}

    /* Toast Notification */
    .toast {{
        position: fixed;
        bottom: 24px; right: 24px;
        background: {surface_hex};
        border: 1px solid rgba(37,99,235,0.4);
        padding: 14px 22px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        color: {text_main};
        font-weight: 600;
        font-size: 0.88rem;
        transform: translateY(100px);
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        z-index: 1000;
    }}
    .toast.show {{
        transform: translateY(0);
        opacity: 1;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); opacity: 0.8; }}
        50% {{ transform: scale(1.15); opacity: 1; }}
        100% {{ transform: scale(0.95); opacity: 0.8; }}
    }}
</style>
</head>
<body>

<canvas id="bg-canvas"></canvas>

<div class="wrap">
    <!-- Header -->
    <div class="brand-bar">
        <div class="brand-title">
            <i class="fa-solid fa-route" style="color: #38BDF8;"></i>
            <span>CAB FLOW</span>
            <span class="brand-badge">Delhi NCR</span>
        </div>
        <div class="status-badge">
            <div class="live-dot"></div>
            <span>LIVE INTELLIGENCE • ALL 35 NCR SECTORS</span>
        </div>
    </div>

    <!-- Step 1: Choose Role -->
    <div class="role-container">
        <div class="role-title">Choose How You Want to Use Cab Flow</div>
        <div class="role-subtitle">Select your portal below to see live maps and simple tools built for you:</div>
        <div class="role-switch-grid">
            <div class="role-btn active" id="btn-role-customer" onclick="setRole('customer')">
                <div class="role-icon">
                    <i class="fa-solid fa-user"></i>
                </div>
                <div>
                    <div class="role-name">Customer Portal</div>
                    <div class="role-desc">Book quick rides, see live route on the map, and get fair regional prices with no surprises.</div>
                </div>
            </div>
            <div class="role-btn" id="btn-role-driver" onclick="setRole('driver')">
                <div class="role-icon">
                    <i class="fa-solid fa-car"></i>
                </div>
                <div>
                    <div class="role-name">Driver Partner Hub</div>
                    <div class="role-desc">See the live demand map to know exactly where more riders are waiting so you can earn more per hour.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- PORTAL 1: CUSTOMER VIEW (SIMPLE CAB BOOKING)   -->
    <!-- ============================================== -->
    <div id="view-customer" class="view-section active">
        <div class="portal-grid">
            <!-- Left: Ride Booking Form -->
            <div class="card">
                <div class="section-title">
                    <i class="fa-solid fa-location-crosshairs" style="color: #38BDF8;"></i>
                    <span>Plan Your Trip</span>
                </div>
                <div class="section-desc">Select your pickup and drop location across Delhi NCR:</div>

                <div class="form-group">
                    <label class="form-label">Pickup Point (Where to pick you up?)</label>
                    <select id="cust-pickup" class="form-select" onchange="calcCustomerTrip()"></select>
                </div>

                <div class="form-group">
                    <label class="form-label">Drop Location (Where do you want to go?)</label>
                    <select id="cust-drop" class="form-select" onchange="calcCustomerTrip()"></select>
                </div>

                <div style="font-size: 0.82rem; font-weight: 700; color: {text_sub}; margin-bottom: 8px;">
                    Choose Your Vehicle Type:
                </div>
                <div class="ride-options">
                    <div class="ride-card selected" onclick="selectTier(this, 'Flow Auto', 9.5, 30.0, 'Bajaj Maxima CNG', 'DL 1R B 3302', 'Rajesh Gupta')">
                        <div>
                            <div class="ride-name">Flow Auto</div>
                            <div class="ride-meta">3 Seats • Quick doorstep auto rickshaw</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-auto">Rs. 190</div>
                            <div class="ride-eta">1 min away</div>
                        </div>
                    </div>

                    <div class="ride-card" onclick="selectTier(this, 'Flow Go', 14.0, 45.0, 'Maruti Suzuki Dzire', 'DL 1Y AB 7821', 'Vikram Singh')">
                        <div>
                            <div class="ride-name">Flow Go</div>
                            <div class="ride-meta">4 Seats • Affordable AC sedan</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-go">Rs. 280</div>
                            <div class="ride-eta">2 mins away</div>
                        </div>
                    </div>

                    <div class="ride-card" onclick="selectTier(this, 'Flow Prime', 18.5, 60.0, 'Honda City i-VTEC', 'DL 2C XY 4419', 'Amit Sharma')">
                        <div>
                            <div class="ride-name">Flow Prime</div>
                            <div class="ride-meta">4 Seats • Top-rated drivers, comfortable ride</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-prime">Rs. 370</div>
                            <div class="ride-eta">4 mins away</div>
                        </div>
                    </div>

                    <div class="ride-card" onclick="selectTier(this, 'Flow XL', 25.0, 90.0, 'Toyota Innova Crysta', 'HR 26 DR 9012', 'Gurpreet Singh')">
                        <div>
                            <div class="ride-name">Flow XL</div>
                            <div class="ride-meta">6 Seats • Spacious SUV for families & luggage</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-xl">Rs. 495</div>
                            <div class="ride-eta">6 mins away</div>
                        </div>
                    </div>
                </div>

                <button class="btn-action" onclick="confirmCustomerRide()">
                    <i class="fa-solid fa-check"></i>
                    <span id="cust-btn-text">Book Ride Now • Flow Auto (Rs. 190)</span>
                </button>

                <!-- Booking Confirmation Banner -->
                <div id="cust-dispatch-banner" style="display: none; background: rgba(16,185,129,0.12); border: 1px solid #10B981; border-radius: 14px; padding: 18px; margin-top: 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #10B981; font-weight: 800; font-size: 0.92rem;">CAB BOOKED SUCCESSFULLY</span>
                        <span style="font-size: 0.8rem; color: #38BDF8; font-weight: 700;">ARRIVING IN 2 MINS</span>
                    </div>
                    <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 1.05rem; font-weight: 800;" id="cust-disp-driver">Rajesh Gupta</div>
                            <div style="font-size: 0.82rem; color: {text_sub};" id="cust-disp-car">Bajaj Maxima CNG • DL 1R B 3302</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.72rem; color: {text_dim}; font-weight: 700;">START PIN</div>
                            <div style="font-size: 1.35rem; font-weight: 800; color: #38BDF8; letter-spacing: 2px;">5192</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: Interactive Live Map & Trip Details -->
            <div>
                <div class="card" style="padding: 18px;">
                    <div class="section-title">
                        <i class="fa-solid fa-map-location-dot" style="color: #38BDF8;"></i>
                        <span>Live Route Map</span>
                    </div>
                    <div class="section-desc">Look at your pickup and drop location on the map:</div>
                    
                    <!-- Leaflet Customer Map -->
                    <div class="map-box">
                        <div id="map-customer"></div>
                    </div>

                    <div class="info-grid">
                        <div class="info-tile">
                            <div class="info-label">Trip Distance</div>
                            <div class="info-val" id="cust-metric-dist">26.0 km</div>
                        </div>
                        <div class="info-tile">
                            <div class="info-label">Estimated Time</div>
                            <div class="info-val" id="cust-metric-duration">42 mins</div>
                        </div>
                        <div class="info-tile">
                            <div class="info-label">Estimated Price</div>
                            <div class="info-val" style="color: #38BDF8;" id="cust-metric-fare">Rs. 340</div>
                        </div>
                    </div>

                    <div style="background: {input_bg}; border: 1px solid {border_hex}; border-radius: 12px; padding: 14px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 0.76rem; font-weight: 700; color: {text_dim};">CAB ARRIVAL CONFIDENCE</div>
                            <div style="font-size: 0.98rem; font-weight: 800; color: #10B981; margin-top: 2px;" id="cust-risk-label">
                                Highly Reliable (Very low chance of driver cancellation)
                            </div>
                        </div>
                        <button onclick="pingStandby()" class="btn-action" style="width: auto; padding: 8px 16px; font-size: 0.82rem; background: rgba(37,99,235,0.15); color: #60A5FA; border: 1px solid rgba(37,99,235,0.4); box-shadow: none;">
                            Alert Cabs Nearby
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- PORTAL 2: DRIVER PARTNER DEMAND MAP            -->
    <!-- ============================================== -->
    <div id="view-driver" class="view-section">
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; margin-bottom: 18px;">
                <div>
                    <div class="section-title">
                        <i class="fa-solid fa-map-pin" style="color: #EF4444;"></i>
                        <span>Delhi NCR Live Demand Map for Drivers</span>
                    </div>
                    <div class="section-desc" style="margin-bottom: 0;">
                        See which areas in Delhi NCR have high rider demand right now. Drive towards <span style="color: #EF4444; font-weight: 700;">Red areas</span> to get rides faster and earn more money!
                    </div>
                </div>
                <button onclick="refreshDriverDemand()" class="btn-action" style="width: auto; padding: 10px 20px; font-size: 0.88rem;">
                    <i class="fa-solid fa-rotate-right"></i> Refresh Demand Map
                </button>
            </div>

            <!-- Leaflet Driver Heatmap Map -->
            <div class="map-box" style="height: 420px;">
                <div id="map-driver"></div>
            </div>

            <!-- Demand Summary Legend -->
            <div style="display: flex; gap: 24px; flex-wrap: wrap; padding: 14px 18px; background: {input_bg}; border: 1px solid {border_hex}; border-radius: 12px; margin-bottom: 18px; font-size: 0.86rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 14px; height: 14px; border-radius: 50%; background: #EF4444;"></div>
                    <span><strong>Red Zones:</strong> High Demand (Maximum rides & highest earnings)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 14px; height: 14px; border-radius: 50%; background: #F59E0B;"></div>
                    <span><strong>Orange Zones:</strong> Normal / Steady Demand</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 14px; height: 14px; border-radius: 50%; background: #10B981;"></div>
                    <span><strong>Green Zones:</strong> Low Demand (Plenty of empty cabs, move towards Red zones)</span>
                </div>
            </div>

            <div style="font-size: 1.05rem; font-weight: 800; margin-top: 14px;">Area by Area Details:</div>
            <div class="hotspot-grid" id="driver-hotspots-container">
                <!-- Dynamically populated from API -->
            </div>
        </div>
    </div>
</div>

<div id="toast" class="toast"><span id="toast-text">Update complete!</span></div>

<script>
    // Canvas Background Particles
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {{
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }});

    const particles = [];
    for (let i = 0; i < 30; i++) {{
        particles.push({{
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.35,
            vy: (Math.random() - 0.5) * 0.35,
            radius: Math.random() * 2 + 1
        }});
    }}

    function animateParticles() {{
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = '{'rgba(56, 189, 248, 0.22)' if is_dark else 'rgba(37, 99, 235, 0.12)'}';
        ctx.strokeStyle = '{'rgba(38, 52, 78, 0.2)' if is_dark else 'rgba(226, 232, 240, 0.35)'}';

        for (let i = 0; i < particles.length; i++) {{
            const p = particles[i];
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {{
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 130) {{
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }}
            }}
        }}
        requestAnimationFrame(animateParticles);
    }}
    animateParticles();

    // Map instances & coordinates
    const locationCoords = {json.dumps(NCR_LOCATIONS_MAP)};
    const ncrSectors = Object.keys(locationCoords);

    let customerMap = null;
    let customerRouteLayer = null;
    let driverMap = null;
    let driverCirclesLayer = null;

    // Tile Layer choice (Dark vs Light CartoDB)
    const mapTileUrl = '{'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' if is_dark else 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'}';

    function initCustomerMap() {{
        if (customerMap) return;
        customerMap = L.map('map-customer', {{ zoomControl: true, attributionControl: false }}).setView([28.6139, 77.2090], 11);
        L.tileLayer(mapTileUrl, {{ maxZoom: 18 }}).addTo(customerMap);
        customerRouteLayer = L.layerGroup().addTo(customerMap);
    }}

    function initDriverMap() {{
        if (driverMap) return;
        driverMap = L.map('map-driver', {{ zoomControl: true, attributionControl: false }}).setView([28.5800, 77.1800], 11);
        L.tileLayer(mapTileUrl, {{ maxZoom: 18 }}).addTo(driverMap);
        driverCirclesLayer = L.layerGroup().addTo(driverMap);
    }}

    // Role Switching
    function setRole(role) {{
        document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));

        if (role === 'customer') {{
            document.getElementById('view-customer').classList.add('active');
            document.getElementById('btn-role-customer').classList.add('active');
            setTimeout(() => {{
                if (customerMap) customerMap.invalidateSize();
            }}, 200);
        }} else {{
            document.getElementById('view-driver').classList.add('active');
            document.getElementById('btn-role-driver').classList.add('active');
            setTimeout(() => {{
                initDriverMap();
                if (driverMap) driverMap.invalidateSize();
                refreshDriverDemand();
            }}, 200);
        }}
    }}

    // Populate Select Options
    function populateLocations() {{
        const pSel = document.getElementById('cust-pickup');
        const dSel = document.getElementById('cust-drop');
        pSel.innerHTML = '';
        dSel.innerHTML = '';

        ncrSectors.forEach((loc) => {{
            const opt1 = document.createElement('option');
            opt1.value = loc;
            opt1.innerText = loc;
            if (loc.includes('Barakhamba Road')) opt1.selected = true;
            pSel.appendChild(opt1);

            const opt2 = document.createElement('option');
            opt2.value = loc;
            opt2.innerText = loc;
            if (loc.includes('Cyber City')) opt2.selected = true;
            dSel.appendChild(opt2);
        }});
    }}

    let selectedVehicle = {{
        name: "Flow Auto", rateKm: 9.5, baseFare: 30.0,
        plate: "DL 1R B 3302", model: "Bajaj Maxima CNG", driver: "Rajesh Gupta"
    }};

    function selectTier(el, name, rateKm, baseFare, model, plate, driver) {{
        document.querySelectorAll('.ride-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        selectedVehicle = {{ name, rateKm, baseFare, plate, model, driver }};
        calcCustomerTrip();
    }}

    function calcCustomerTrip() {{
        const p = document.getElementById('cust-pickup').value;
        const d = document.getElementById('cust-drop').value;

        const pCoord = locationCoords[p] || [28.6315, 77.2215];
        const dCoord = locationCoords[d] || [28.4952, 77.0895];

        // Haversine Distance in Kilometers
        const R = 6371; // km
        const dLat = (dCoord[0] - pCoord[0]) * Math.PI / 180;
        const dLon = (dCoord[1] - pCoord[1]) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(pCoord[0] * Math.PI / 180) * Math.cos(dCoord[0] * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        let roadDist = Math.max(2.5, Math.round(R * c * 1.35 * 10) / 10);
        const duration = Math.round((roadDist / 26.0) * 60) + 4;

        // Update Map Markers & Route Line
        if (customerMap && customerRouteLayer) {{
            customerRouteLayer.clearLayers();

            const pMarker = L.circleMarker(pCoord, {{
                radius: 8,
                fillColor: '#10B981',
                color: '#FFFFFF',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.95
            }}).bindPopup('<strong>Pickup:</strong> ' + p).addTo(customerRouteLayer);

            const dMarker = L.circleMarker(dCoord, {{
                radius: 8,
                fillColor: '#EF4444',
                color: '#FFFFFF',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.95
            }}).bindPopup('<strong>Drop:</strong> ' + d).addTo(customerRouteLayer);

            const routeLine = L.polyline([pCoord, dCoord], {{
                color: '#38BDF8',
                weight: 4,
                opacity: 0.85,
                dashArray: '8, 8'
            }}).addTo(customerRouteLayer);

            customerMap.fitBounds(L.latLngBounds([pCoord, dCoord]), {{ padding: [40, 40] }});
        }}

        // Query Live Python REST API
        fetch('http://127.0.0.1:8000/api/predict/fare', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                ride_distance: roadDist,
                vehicle_type: selectedVehicle.name === 'Flow Auto' ? 'Auto' :
                              selectedVehicle.name === 'Flow XL' ? 'Uber XL' :
                              selectedVehicle.name === 'Flow Prime' ? 'Premier Sedan' : 'Go Mini',
                avg_vtat: 8.5
            }})
        }})
        .then(res => res.json())
        .then(data => {{
            if (data && data.estimated_fare_inr) {{
                const fare = Math.round(data.estimated_fare_inr);
                document.getElementById('cust-metric-fare').innerText = "Rs. " + fare;
                document.getElementById('cust-btn-text').innerText = `Book Ride Now • ${{selectedVehicle.name}} (Rs. ${{fare}})`;
            }}
        }})
        .catch(() => {{
            const fallback = Math.round(selectedVehicle.baseFare + (roadDist * selectedVehicle.rateKm) + (duration * 1.5));
            document.getElementById('cust-metric-fare').innerText = "Rs. " + fallback;
            document.getElementById('cust-btn-text').innerText = `Book Ride Now • ${{selectedVehicle.name}} (Rs. ${{fallback}})`;
        }});

        // Query Live Cancellation API
        fetch('http://127.0.0.1:8000/api/predict/cancellation', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                avg_vtat: 8.5,
                vehicle_type: selectedVehicle.name === 'Flow Auto' ? 'Auto' : 'Go Sedan'
            }})
        }})
        .then(res => res.json())
        .then(risk => {{
            if (risk && risk.cancellation_probability !== undefined) {{
                const pct = (risk.cancellation_probability * 100).toFixed(0);
                if (risk.cancellation_risk === 'Low') {{
                    document.getElementById('cust-risk-label').innerText = `Very Reliable (${{pct}}% cancellation risk)`;
                    document.getElementById('cust-risk-label').style.color = '#10B981';
                }} else {{
                    document.getElementById('cust-risk-label').innerText = `Moderate Traffic Waiting Time`;
                    document.getElementById('cust-risk-label').style.color = '#F59E0B';
                }}
            }}
        }})
        .catch(() => {{}});

        document.getElementById('cust-metric-dist').innerText = roadDist + " km";
        document.getElementById('cust-metric-duration').innerText = duration + " mins";

        // Update All Tier Prices
        const rates = [
            {{ id: 'p-auto', base: 30, km: 9.5 }},
            {{ id: 'p-go', base: 45, km: 14.0 }},
            {{ id: 'p-prime', base: 60, km: 18.5 }},
            {{ id: 'p-xl', base: 90, km: 25.0 }}
        ];
        rates.forEach(r => {{
            const pVal = Math.round(r.base + (roadDist * r.km) + (duration * 1.5));
            document.getElementById(r.id).innerText = "Rs. " + pVal;
        }});
    }}

    function confirmCustomerRide() {{
        const b = document.getElementById('cust-dispatch-banner');
        b.style.display = 'block';
        document.getElementById('cust-disp-driver').innerText = selectedVehicle.driver;
        document.getElementById('cust-disp-car').innerText = `${{selectedVehicle.model}} • ${{selectedVehicle.plate}}`;
        showToast(`Driver ${{selectedVehicle.driver}} is on the way!`);
        b.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
    }}

    function pingStandby() {{
        showToast('Looking for 3 nearby cabs right now!');
    }}

    // Driver Demand Feed & Heatmap
    function refreshDriverDemand() {{
        const container = document.getElementById('driver-hotspots-container');
        container.innerHTML = '<div style="color: {text_sub}; padding: 16px;">Loading live demand information from Delhi NCR roads...</div>';

        fetch('http://127.0.0.1:8000/api/driver/demand-map')
            .then(res => res.json())
            .then(data => {{
                if (data && data.zones) {{
                    container.innerHTML = '';
                    if (driverMap && driverCirclesLayer) {{
                        driverCirclesLayer.clearLayers();
                    }}

                    data.zones.forEach(z => {{
                        const badgeClass = z.status === 'high' ? 'badge-high' : (z.status === 'moderate' ? 'badge-mod' : 'badge-low');
                        const statusColor = z.status === 'high' ? '#EF4444' : (z.status === 'moderate' ? '#F59E0B' : '#10B981');

                        // Add Heat Circle on Driver Map
                        if (driverMap && driverCirclesLayer && z.lat && z.lng) {{
                            const circle = L.circle([z.lat, z.lng], {{
                                color: statusColor,
                                fillColor: statusColor,
                                fillOpacity: 0.35,
                                radius: z.status === 'high' ? 3200 : (z.status === 'moderate' ? 2400 : 1800),
                                weight: 2
                            }}).bindPopup(`
                                <div style="font-family: sans-serif; font-size: 0.85rem;">
                                    <strong>${{z.zone}}</strong><br>
                                    Demand: <strong>${{z.demand_level}}</strong><br>
                                    Active Ride Requests: ${{z.active_requests}}<br>
                                    Est. Earnings: ${{z.avg_earnings_per_hr}}
                                </div>
                            `).addTo(driverCirclesLayer);
                        }}

                        // Card for Driver
                        const card = document.createElement('div');
                        card.className = `hotspot-card ${{z.status}}`;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                                <div style="font-weight: 800; font-size: 1.02rem;">${{z.zone}}</div>
                                <span class="${{badgeClass}}">${{z.status.toUpperCase()}} DEMAND</span>
                            </div>
                            <div style="font-size: 0.86rem; color: {text_sub}; margin-bottom: 14px;">${{z.hotspot_advice}}</div>
                            <div style="display: flex; justify-content: space-between; padding-top: 10px; border-top: 1px solid {border_hex}; font-size: 0.85rem;">
                                <div>Waiting Riders: <strong style="color: #38BDF8;">${{z.active_requests}}</strong></div>
                                <div>Average Income: <strong style="color: #10B981;">${{z.avg_earnings_per_hr}}</strong></div>
                            </div>
                        `;
                        container.appendChild(card);
                    }});
                }}
            }})
            .catch(() => {{
                container.innerHTML = '<div style="color: #EF4444; padding: 16px;">Cannot connect to API server. Please check port 8000.</div>';
            }});
    }}

    function showToast(msg) {{
        const t = document.getElementById('toast');
        document.getElementById('toast-text').innerText = msg;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 3500);
    }}

    // Init App
    window.addEventListener('load', () => {{
        initCustomerMap();
        populateLocations();
        calcCustomerTrip();
    }});
    // Fallback if window load already passed
    setTimeout(() => {{
        initCustomerMap();
        populateLocations();
        calcCustomerTrip();
    }}, 400);
</script>
</body>
</html>
"""

components.html(html_application, height=980, scrolling=True)
