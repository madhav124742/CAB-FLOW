"""
app.py
Cab Flow - Autonomous Delhi NCR Mobility Command & Dual Driver/Customer Portal.
Features role-based entrance (Driver vs Customer), live Delhi NCR demand hotspot intelligence,
regional price estimation, live ML API integration, animated particle mesh, light/dark mode, and zero emojis.
"""

import os
import json
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# Delhi NCR Locations Matrix
NCR_LOCATIONS = [
    "AIIMS, South Delhi",
    "Akshardham, East Delhi",
    "Ambience Mall, Gurugram",
    "Anand Vihar ISBT, East Delhi",
    "Badarpur Border, South East Delhi",
    "Barakhamba Road, Connaught Place",
    "Central Secretariat, Central Delhi",
    "Chanakyapuri (Embassy Zone)",
    "Chandni Chowk, Old Delhi",
    "Cyber City / Cyber Hub, DLF Gurugram",
    "Delhi Gate, Central Delhi",
    "Dilshad Garden, East Delhi",
    "Dwarka Sector 21, South West Delhi",
    "Faridabad Sector 15 / Bata Chowk",
    "Ghaziabad Railway Station / Hub",
    "Greater Kailash (M-Block), South Delhi",
    "Hauz Khas Social, South Delhi",
    "Indira Gandhi International Airport (DEL T3)",
    "Khandsa / Manesar Industrial Corridor",
    "Laxmi Nagar Metro Hub, East Delhi",
    "Malviya Nagar, South Delhi",
    "Mehrauli / Qutub Minar, South Delhi",
    "Nehru Place IT Hub, South Delhi",
    "New Delhi Railway Station (Paharganj)",
    "Noida Electronic City / Sector 62",
    "Noida Sector 18 (Atta Market / Mall of India)",
    "Old Delhi Railway Station (Chandni Chowk)",
    "Palam Vihar, Gurugram",
    "Pragati Maidan / Bharat Mandapam",
    "Rohini Sector 18 / West Delhi Hub",
    "Saket District Centre, South Delhi",
    "Sohna Road / Golf Course Extn, Gurugram",
    "Tilak Nagar / Rajouri Garden, West Delhi",
    "Udyog Vihar Phase 1-5, Gurugram",
    "Vishwavidyalaya (Delhi University North Campus)"
]

st.set_page_config(
    page_title="Cab Flow | Delhi NCR Mobility Command",
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

# Dynamic Theme Colors
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

    /* Header Nav */
    .brand-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 26px;
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 16px;
        margin-bottom: 22px;
        box-shadow: 0 4px 22px rgba(0,0,0,{"0.3" if is_dark else "0.04"});
        animation: fadeIn 0.5s ease;
    }}
    .brand-title {{
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .brand-badge {{
        background: linear-gradient(135deg, {accent_hex}, #06B6D4);
        color: #fff;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 6px;
        letter-spacing: 0.8px;
        box-shadow: 0 0 12px rgba(37,99,235,0.4);
    }}
    .status-badge {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #10B981;
        background: rgba(16,185,129,0.12);
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid rgba(16,185,129,0.3);
    }}
    .status-dot {{
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 10px #10B981;
        animation: blinkDot 2s infinite ease-in-out;
    }}
    @keyframes blinkDot {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.35; }}
    }}

    /* Role Registration Landing Window */
    .role-modal-overlay {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 24px;
        animation: fadeInUp 0.5s ease;
    }}
    .role-switch-container {{
        background: {surface_hex};
        border: 1.5px solid {border_hex};
        border-radius: 18px;
        padding: 24px 28px;
        width: 100%;
        box-shadow: 0 8px 30px rgba(0,0,0,{"0.35" if is_dark else "0.05"});
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
    }}
    @media (max-width: 860px) {{
        .role-switch-container {{ flex-direction: column; align-items: stretch; }}
    }}
    .role-tabs {{
        display: flex;
        background: {input_bg};
        border: 1px solid {border_hex};
        padding: 5px;
        border-radius: 14px;
        gap: 6px;
    }}
    .role-btn {{
        background: transparent;
        border: none;
        color: {text_sub};
        padding: 10px 22px;
        border-radius: 10px;
        font-size: 0.92rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        align-items: center;
        gap: 9px;
    }}
    .role-btn.active {{
        background: linear-gradient(135deg, {accent_hex}, #1D4ED8);
        color: #FFFFFF;
        box-shadow: 0 4px 16px rgba(37,99,235,0.4);
    }}
    .role-btn:hover:not(.active) {{
        color: {text_main};
        background: rgba(255,255,255,0.05);
    }}

    /* Card Panels */
    .view-section {{
        display: none;
        animation: fadeInUp 0.4s ease;
    }}
    .view-section.active {{
        display: block;
    }}

    .grid-2col {{
        display: grid;
        grid-template-columns: 480px 1fr;
        gap: 24px;
    }}
    @media (max-width: 1020px) {{
        .grid-2col {{ grid-template-columns: 1fr; }}
    }}

    .card {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,{"0.3" if is_dark else "0.04"});
        transition: border-color 0.3s ease;
    }}
    .card:hover {{
        border-color: rgba(37,99,235,0.45);
    }}

    .section-title {{
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: -0.4px;
        margin-bottom: 4px;
    }}
    .section-desc {{
        font-size: 0.85rem;
        color: {text_sub};
        margin-bottom: 20px;
    }}

    /* Form Fields */
    .form-group {{ margin-bottom: 16px; }}
    .form-label {{
        display: block;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        color: {text_dim};
        margin-bottom: 7px;
        letter-spacing: 0.7px;
    }}
    .form-select, .form-input {{
        width: 100%;
        background: {input_bg};
        border: 1px solid {border_hex};
        border-radius: 12px;
        padding: 13px 16px;
        color: {text_main};
        font-size: 0.92rem;
        outline: none;
        transition: all 0.2s ease;
    }}
    .form-select:focus, .form-input:focus {{
        border-color: {accent_hex};
        box-shadow: 0 0 0 3px rgba(37,99,235,0.25);
    }}

    /* Telematics Radar */
    .radar-box {{
        background: linear-gradient(135deg, rgba(37,99,235,0.12), rgba(6,182,212,0.08));
        border: 1px solid rgba(56,189,248,0.3);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        overflow: hidden;
    }}
    .radar-box::after {{
        content: '';
        position: absolute;
        top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,{"0.1" if is_dark else "0.3"}), transparent);
        animation: radarSweep 3.5s infinite ease-in-out;
    }}
    @keyframes radarSweep {{
        0% {{ left: -100%; }}
        50%, 100% {{ left: 200%; }}
    }}
    .radar-tag {{
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #38BDF8;
        background: rgba(56,189,248,0.15);
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 5px;
    }}

    /* Vehicles */
    .ride-options {{
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 20px;
    }}
    .ride-card {{
        background: {input_bg};
        border: 1.5px solid {border_hex};
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .ride-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(37,99,235,0.5);
    }}
    .ride-card.selected {{
        border-color: {accent_hex};
        background: rgba(37,99,235,0.16);
        box-shadow: 0 0 20px rgba(37,99,235,0.25);
    }}
    .ride-name {{ font-weight: 700; font-size: 0.98rem; }}
    .ride-meta {{ font-size: 0.78rem; color: {text_sub}; margin-top: 2px; }}
    .ride-price {{ font-size: 1.25rem; font-weight: 800; color: {text_main}; text-align: right; }}
    .ride-eta {{ font-size: 0.74rem; color: #10B981; font-weight: 600; text-align: right; }}

    /* Action Button */
    .btn-action {{
        width: 100%;
        background: linear-gradient(135deg, {accent_hex}, #1D4ED8);
        color: #FFF;
        border: none;
        border-radius: 12px;
        padding: 15px;
        font-size: 1.05rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 18px rgba(37,99,235,0.38);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }}
    .btn-action:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(37,99,235,0.55);
    }}

    /* Route Visualizer Card */
    .route-node-box {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
    }}
    .route-node {{ display: flex; align-items: flex-start; gap: 14px; }}
    .dot-node {{ width: 14px; height: 14px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }}
    .dot-green {{
        background: #10B981;
        box-shadow: 0 0 12px rgba(16,185,129,0.8);
        animation: pulseGreen 2s infinite ease-in-out;
    }}
    @keyframes pulseGreen {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.25); box-shadow: 0 0 18px rgba(16,185,129,0.9); }}
    }}
    .dot-red {{
        background: #EF4444;
        box-shadow: 0 0 12px rgba(239,68,68,0.8);
        animation: pulseRed 2s infinite ease-in-out;
    }}
    @keyframes pulseRed {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.25); box-shadow: 0 0 18px rgba(239,68,68,0.9); }}
    }}
    .route-line {{
        border-left: 2px dashed {border_hex};
        height: 36px;
        margin-left: 6px;
        margin-top: 4px;
        margin-bottom: 4px;
        position: relative;
    }}
    .route-packet {{
        position: absolute;
        width: 4px; height: 10px;
        background: #38BDF8;
        border-radius: 2px;
        left: -3px;
        box-shadow: 0 0 8px #38BDF8;
        animation: travelDown 1.8s infinite linear;
    }}
    @keyframes travelDown {{
        0% {{ top: 0; opacity: 0; }}
        20% {{ opacity: 1; }}
        80% {{ opacity: 1; }}
        100% {{ top: 26px; opacity: 0; }}
    }}

    /* Metrics Grid */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 20px;
    }}
    .metric-tile {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }}
    .metric-label {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: {text_dim};
        letter-spacing: 0.6px;
    }}
    .metric-val {{
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 5px;
        color: {text_main};
    }}

    /* Driver Demand Hotspot Zone Cards */
    .hotspot-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
        gap: 18px;
        margin-top: 18px;
    }}
    .hotspot-card {{
        background: {surface_hex};
        border: 1px solid {border_hex};
        border-radius: 16px;
        padding: 20px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }}
    .hotspot-card:hover {{
        transform: translateY(-3px);
        border-color: rgba(37,99,235,0.45);
    }}
    .hotspot-card.high {{ border-left: 4px solid #EF4444; }}
    .hotspot-card.moderate {{ border-left: 4px solid #F59E0B; }}
    .hotspot-card.low {{ border-left: 4px solid #10B981; }}

    .zone-badge {{
        font-size: 0.72rem;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }}
    .badge-high {{ background: rgba(239,68,68,0.18); color: #F87171; }}
    .badge-mod {{ background: rgba(245,158,11,0.18); color: #FBBF24; }}
    .badge-low {{ background: rgba(16,185,129,0.18); color: #34D399; }}

    .toast {{
        position: fixed;
        bottom: 24px; right: 24px;
        background: {surface_hex};
        border: 1px solid rgba(37,99,235,0.4);
        padding: 14px 22px;
        border-radius: 14px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        transform: translateY(120px);
        transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        z-index: 999;
    }}
    .toast.show {{ transform: translateY(0); }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
</style>
</head>
<body>

<canvas id="bg-canvas"></canvas>

<div class="wrap">
    <!-- Top Bar -->
    <div class="brand-bar">
        <div class="brand-title">
            CAB FLOW <span class="brand-badge">DELHI NCR MOBILITY COMMAND</span>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>LIVE ML INFERENCE ACTIVE</span>
        </div>
    </div>

    <!-- Entrance Registration / Role Selector -->
    <div class="role-modal-overlay">
        <div class="role-switch-container">
            <div>
                <div style="font-size: 1.15rem; font-weight: 800; margin-bottom: 4px;">Choose Platform Entrance</div>
                <div style="font-size: 0.86rem; color: {text_sub};">Access specialized tools tailored for Drivers (Demand Hotspots) or Customers (Regional Fare Engine).</div>
            </div>
            <div class="role-tabs">
                <button class="role-btn active" id="btn-role-customer" onclick="setRole('customer')">
                    <i class="fa-solid fa-user"></i> Customer Portal
                </button>
                <button class="role-btn" id="btn-role-driver" onclick="setRole('driver')">
                    <i class="fa-solid fa-id-card"></i> Driver Partner Hub
                </button>
            </div>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- PORTAL 1: CUSTOMER REGIONAL PRICING & DISPATCH -->
    <!-- ============================================== -->
    <div id="view-customer" class="view-section active">
        <div class="grid-2col">
            <!-- Left: Regional Route Config -->
            <div class="card">
                <div class="section-title">Customer Regional Ride Booking</div>
                <div class="section-desc">Fast, regional pricing calibrated across all sectors in Delhi, Gurugram, Noida, Ghaziabad & Faridabad.</div>

                <div class="form-group">
                    <label class="form-label">Pickup Sector (Delhi NCR)</label>
                    <select id="cust-pickup" class="form-select" onchange="calcCustomerTrip()">
                        <!-- Populated dynamically via NCR Sector list -->
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">Destination Sector (Delhi NCR)</label>
                    <select id="cust-drop" class="form-select" onchange="calcCustomerTrip()">
                        <!-- Populated dynamically via NCR Sector list -->
                    </select>
                </div>

                <!-- Live Environmental Telematics -->
                <div class="radar-box">
                    <div>
                        <span class="radar-tag">Route Telematics</span>
                        <div style="font-weight: 700; font-size: 0.94rem; margin-top: 4px;" id="cust-traffic-text">
                            Traffic: <span style="color: #F59E0B;" id="cust-traffic-val">Peak Window</span>
                        </div>
                        <div style="font-size: 0.82rem; color: {text_sub}; margin-top: 2px;">
                            Atmospheric State: Clear Skies (31 C)
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.7rem; color: {text_dim}; font-weight: 700;">REGIONAL SURGE</div>
                        <div style="font-size: 1.35rem; font-weight: 800; color: #F59E0B;" id="cust-surge-val">1.35x</div>
                    </div>
                </div>

                <!-- Vehicle Options -->
                <div class="form-label">Select Regional Vehicle Class</div>
                <div class="ride-options">
                    <div class="ride-card selected" onclick="selectTier(this, 'Flow Auto', 9.5, 30.0, 'Bajaj Maxima CNG', 'DL 1R B 3302', 'Rajesh Gupta')">
                        <div>
                            <div class="ride-name">Flow Auto</div>
                            <div class="ride-meta">3 Passengers • Doorstep Rapid Rickshaw</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-auto">INR 190</div>
                            <div class="ride-eta">1 min away</div>
                        </div>
                    </div>

                    <div class="ride-card" onclick="selectTier(this, 'Flow Go', 14.0, 45.0, 'Maruti Suzuki Dzire', 'DL 1Y AB 7821', 'Vikram Singh')">
                        <div>
                            <div class="ride-name">Flow Go</div>
                            <div class="ride-meta">4 Passengers • Compact Sedan</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-go">INR 280</div>
                            <div class="ride-eta">2 mins away</div>
                        </div>
                    </div>

                    <div class="ride-card" onclick="selectTier(this, 'Flow Prime', 18.5, 60.0, 'Honda City i-VTEC', 'DL 2C XY 4419', 'Amit Sharma')">
                        <div>
                            <div class="ride-name">Flow Prime</div>
                            <div class="ride-meta">4 Passengers • Executive Sedan</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-prime">INR 370</div>
                            <div class="ride-eta">4 mins away</div>
                        </div>
                    </div>

                    <div class="ride-card" onclick="selectTier(this, 'Flow XL', 25.0, 90.0, 'Toyota Innova Crysta', 'HR 26 DR 9012', 'Gurpreet Singh')">
                        <div>
                            <div class="ride-name">Flow XL</div>
                            <div class="ride-meta">6 Passengers • Premium SUV</div>
                        </div>
                        <div>
                            <div class="ride-price" id="p-xl">INR 495</div>
                            <div class="ride-eta">6 mins away</div>
                        </div>
                    </div>
                </div>

                <button class="btn-action" onclick="confirmCustomerRide()">
                    <i class="fa-solid fa-bolt"></i>
                    <span id="cust-btn-text">Confirm Regional Booking • Flow Auto</span>
                </button>

                <!-- Confirmed Banner -->
                <div id="cust-dispatch-banner" style="display: none; background: {surface_hex}; border: 1px solid rgba(16,185,129,0.5); border-radius: 14px; padding: 20px; margin-top: 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #10B981; font-weight: 800; font-size: 0.92rem;">DRIVER APPOINTED & CONFIRMED</span>
                        <span style="font-size: 0.8rem; color: #38BDF8; font-weight: 700;">ARRIVING IN 2 MINS</span>
                    </div>
                    <div style="margin-top: 12px; display: flex; justify-content: space-between;">
                        <div>
                            <div style="font-size: 1.1rem; font-weight: 800;" id="cust-disp-driver">Rajesh Gupta</div>
                            <div style="font-size: 0.82rem; color: {text_sub};" id="cust-disp-car">Bajaj Maxima CNG • DL 1R B 3302</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.7rem; color: {text_dim}; font-weight: 700;">START PIN</div>
                            <div style="font-size: 1.4rem; font-weight: 800; color: #38BDF8; letter-spacing: 2px;">5192</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: Route & Regional Pricing Telematics -->
            <div>
                <div class="route-node-box">
                    <div class="route-node">
                        <div class="dot-node dot-green"></div>
                        <div>
                            <div style="font-size: 0.72rem; color: {text_dim}; font-weight: 700; text-transform: uppercase;">Origin</div>
                            <div style="font-size: 1.05rem; font-weight: 700;" id="cust-node-pickup">Barakhamba Road, Connaught Place</div>
                        </div>
                    </div>
                    <div class="route-line"><div class="route-packet"></div></div>
                    <div class="route-node">
                        <div class="dot-node dot-red"></div>
                        <div>
                            <div style="font-size: 0.72rem; color: {text_dim}; font-weight: 700; text-transform: uppercase;">Destination</div>
                            <div style="font-size: 1.05rem; font-weight: 700;" id="cust-node-drop">Cyber City / Cyber Hub, DLF Gurugram</div>
                        </div>
                    </div>
                </div>

                <div class="metric-grid">
                    <div class="metric-tile">
                        <div class="metric-label">Estimated Distance</div>
                        <div class="metric-val" id="cust-metric-dist">26.0 km</div>
                    </div>
                    <div class="metric-tile">
                        <div class="metric-label">Estimated Transit</div>
                        <div class="metric-val" id="cust-metric-duration">42 mins</div>
                    </div>
                    <div class="metric-tile">
                        <div class="metric-label">Realized Regional Fare</div>
                        <div class="metric-val" style="color: #38BDF8;" id="cust-metric-fare">INR 340</div>
                    </div>
                </div>

                <!-- API Verification Box -->
                <div class="card" style="padding: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: {text_dim};">Live ML API Cancellation Prediction</div>
                            <div style="font-size: 1.1rem; font-weight: 800; color: #10B981; margin-top: 4px;" id="cust-risk-label">
                                Low Churn Risk (9.9% Probability)
                            </div>
                        </div>
                        <button onclick="pingStandby()" class="btn-action" style="width: auto; padding: 10px 18px; font-size: 0.85rem; background: rgba(37,99,235,0.15); color: #60A5FA; border: 1px solid rgba(37,99,235,0.4); box-shadow: none;">
                            Signal Nearest Cab
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- PORTAL 2: DRIVER PARTNER DEMAND HOTSPOT RADAR  -->
    <!-- ============================================== -->
    <div id="view-driver" class="view-section">
        <div class="card" style="margin-bottom: 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div>
                    <div class="section-title">Delhi NCR Demand Radar & Live Hotspot Telematics</div>
                    <div class="section-desc" style="margin-bottom: 0;">Monitor sectors with high vs. low cab demand in real time. Position your vehicle to maximize hourly earnings.</div>
                </div>
                <button onclick="refreshDriverDemand()" class="btn-action" style="width: auto; padding: 10px 20px; font-size: 0.88rem;">
                    <i class="fa-solid fa-arrows-rotate"></i> Refresh Live Demand Feed
                </button>
            </div>
        </div>

        <!-- Hotspots Loaded from API -->
        <div class="hotspot-grid" id="driver-hotspots-container">
            <!-- Dynamically populated via API /api/driver/demand-map -->
        </div>
    </div>
</div>

<div id="toast" class="toast"><span id="toast-text">Operation completed!</span></div>

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
    for (let i = 0; i < 35; i++) {{
        particles.push({{
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            radius: Math.random() * 2 + 1
        }});
    }}

    function animateParticles() {{
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = '{'rgba(56, 189, 248, 0.25)' if is_dark else 'rgba(37, 99, 235, 0.15)'}';
        ctx.strokeStyle = '{'rgba(38, 52, 78, 0.22)' if is_dark else 'rgba(226, 232, 240, 0.4)'}';

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
                if (dist < 140) {{
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

    // Role Switching Logic
    function setRole(role) {{
        document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));

        if (role === 'customer') {{
            document.getElementById('view-customer').classList.add('active');
            document.getElementById('btn-role-customer').classList.add('active');
        }} else {{
            document.getElementById('view-driver').classList.add('active');
            document.getElementById('btn-role-driver').classList.add('active');
            refreshDriverDemand();
        }}
    }}

    // Delhi NCR Location Matrix
    const ncrSectors = {json.dumps(NCR_LOCATIONS)};

    function populateLocations() {{
        const pSel = document.getElementById('cust-pickup');
        const dSel = document.getElementById('cust-drop');
        pSel.innerHTML = '';
        dSel.innerHTML = '';

        ncrSectors.forEach((loc, idx) => {{
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

        document.getElementById('cust-node-pickup').innerText = p;
        document.getElementById('cust-node-drop').innerText = d;

        // Regional Distance Heuristic
        let dist = 18.5;
        if (p === d) dist = 2.4;
        else if (p.includes('Airport') || d.includes('Airport')) dist = 24.5;
        else if ((p.includes('Gurugram') && d.includes('Noida')) || (p.includes('Noida') && d.includes('Gurugram'))) dist = 38.0;
        else if (p.includes('Connaught') || d.includes('Connaught')) dist = 14.0;
        else if (p.includes('Faridabad') || d.includes('Faridabad')) dist = 32.0;

        let surge = 1.35;
        let trafficName = "Moderate Corridor";
        let trafficColor = "#3B82F6";

        if (p.includes('Gurugram') || d.includes('Gurugram') || p.includes('Connaught')) {{
            surge = 1.55;
            trafficName = "High Congestion Window";
            trafficColor = "#EF4444";
        }}

        const duration = Math.round((dist / 25.0) * 60) + 3;

        document.getElementById('cust-traffic-val').innerText = trafficName;
        document.getElementById('cust-traffic-val').style.color = trafficColor;
        document.getElementById('cust-surge-val').innerText = surge.toFixed(2) + "x";

        // Query Live Python REST API
        fetch('http://127.0.0.1:8000/api/predict/fare', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                ride_distance: dist,
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
                document.getElementById('cust-metric-fare').innerText = "INR " + fare;
                document.getElementById('cust-btn-text').innerText = `Confirm Regional Booking • ${{selectedVehicle.name}} (INR ${{fare}})`;
            }}
        }})
        .catch(() => {{
            const fallback = Math.round((selectedVehicle.baseFare + (dist * selectedVehicle.rateKm) + (duration * 1.5)) * surge);
            document.getElementById('cust-metric-fare').innerText = "INR " + fallback;
            document.getElementById('cust-btn-text').innerText = `Confirm Regional Booking • ${{selectedVehicle.name}} (INR ${{fallback}})`;
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
                const pct = (risk.cancellation_probability * 100).toFixed(1);
                document.getElementById('cust-risk-label').innerText = `${{risk.cancellation_risk}} Churn Risk (${{pct}}% Probability)`;
                document.getElementById('cust-risk-label').style.color = risk.cancellation_risk === 'High' ? '#EF4444' : '#10B981';
            }}
        }})
        .catch(() => {{}});

        document.getElementById('cust-metric-dist').innerText = dist + " km";
        document.getElementById('cust-metric-duration').innerText = duration + " mins";

        // Update Tier Prices
        const rates = [
            {{ id: 'p-auto', base: 30, km: 9.5 }},
            {{ id: 'p-go', base: 45, km: 14.0 }},
            {{ id: 'p-prime', base: 60, km: 18.5 }},
            {{ id: 'p-xl', base: 90, km: 25.0 }}
        ];
        rates.forEach(r => {{
            const pVal = Math.round((r.base + (dist * r.km) + (duration * 1.5)) * surge);
            document.getElementById(r.id).innerText = "INR " + pVal;
        }});
    }}

    function confirmCustomerRide() {{
        const b = document.getElementById('cust-dispatch-banner');
        b.style.display = 'block';
        document.getElementById('cust-disp-driver').innerText = selectedVehicle.driver;
        document.getElementById('cust-disp-car').innerText = `${{selectedVehicle.model}} • ${{selectedVehicle.plate}}`;
        showToast(`Driver ${{selectedVehicle.driver}} has been allocated!`);
        b.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
    }}

    function pingStandby() {{
        showToast('Standby telematics: 3 nearest regional cabs signaled!');
    }}

    // Driver Demand Hotspot Feed from API
    function refreshDriverDemand() {{
        const container = document.getElementById('driver-hotspots-container');
        container.innerHTML = '<div style="color: {text_sub}; padding: 20px;">Fetching live Delhi NCR demand telematics from REST API...</div>';

        fetch('http://127.0.0.1:8000/api/driver/demand-map')
            .then(res => res.json())
            .then(data => {{
                if (data && data.zones) {{
                    container.innerHTML = '';
                    data.zones.forEach(z => {{
                        const badgeClass = z.status === 'high' ? 'badge-high' : (z.status === 'moderate' ? 'badge-mod' : 'badge-low');
                        const card = document.createElement('div');
                        card.className = `hotspot-card ${{z.status}}`;
                        card.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                                <div style="font-weight: 800; font-size: 1.05rem;">${{z.zone}}</div>
                                <span class="zone-badge ${{badgeClass}}">${{z.status.toUpperCase()}} DEMAND</span>
                            </div>
                            <div style="font-size: 0.84rem; color: {text_sub}; margin-bottom: 14px;">${{z.hotspot_advice}}</div>
                            <div style="display: flex; justify-content: space-between; padding-top: 12px; border-top: 1px solid {border_hex}; font-size: 0.84rem;">
                                <div>Active Requests: <strong style="color: #38BDF8;">${{z.active_requests}}</strong></div>
                                <div>Est. Earnings: <strong style="color: #10B981;">${{z.avg_earnings_per_hr}}</strong></div>
                            </div>
                        `;
                        container.appendChild(card);
                    }});
                }}
            }})
            .catch(err => {{
                container.innerHTML = '<div style="color: #EF4444; padding: 20px;">Failed to reach REST API. Verify port 8000 is active.</div>';
            }});
    }}

    function showToast(msg) {{
        const t = document.getElementById('toast');
        document.getElementById('toast-text').innerText = msg;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 3500);
    }}

    // Init
    populateLocations();
    calcCustomerTrip();
</script>
</body>
</html>
"""

components.html(html_application, height=940, scrolling=True)
