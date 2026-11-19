"""
app.py
Cab Flow - Delhi NCR Ride Price Guide & Your driver Partner Portal.
Delhi NCR Ride Price Guide - Predict cab prices by time of day.
"""

import json
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# Delhi NCR Locations Matrix (35 sectors)
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
    page_title="Cab Flow | Delhi NCR Ride Price Guide",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Theme State
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

is_dark = st.session_state.theme_mode == "Dark"

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
bg_hex      = "#06080E" if is_dark else "#F0F4F8"
surface_hex = "#0D121D" if is_dark else "#FFFFFF"
border_hex  = "#1E2A3E" if is_dark else "#DDE3ED"
text_main   = "#F8FAFC" if is_dark else "#0F172A"
text_sub    = "#94A3B8" if is_dark else "#475569"
text_dim    = "#64748B" if is_dark else "#94A3B8"
input_bg    = "#090D15" if is_dark else "#F1F5F9"
accent_hex  = "#2563EB"
card_shadow = "rgba(0,0,0,0.3)" if is_dark else "rgba(0,0,0,0.05)"
particle_fill   = "rgba(56,189,248,0.22)"   if is_dark else "rgba(37,99,235,0.1)"
particle_stroke = "rgba(38,52,78,0.2)"      if is_dark else "rgba(203,213,225,0.5)"

NCR_JSON = json.dumps(NCR_LOCATIONS)

html_application = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    *{{box-sizing:border-box;margin:0;padding:0;font-family:'Plus Jakarta Sans',sans-serif;}}
    body{{background:{bg_hex};color:{text_main};padding:10px 16px 60px;overflow-x:hidden;min-height:100vh;position:relative;}}
    #bg-canvas{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;}}
    .wrap{{position:relative;z-index:1;max-width:1440px;margin:0 auto;}}

    /* ---- Brand Bar ---- */
    .brand-bar{{display:flex;justify-content:space-between;align-items:center;padding:14px 22px;background:{surface_hex};border:1px solid {border_hex};border-radius:16px;margin-bottom:18px;box-shadow:0 4px 22px {card_shadow};animation:fadeIn 0.4s ease;}}
    .brand-title{{font-size:1.4rem;font-weight:800;letter-spacing:-0.5px;display:flex;align-items:center;gap:12px;}}
    .brand-badge{{background:linear-gradient(135deg,{accent_hex},#06B6D4);color:#fff;font-size:0.7rem;font-weight:800;text-transform:uppercase;padding:4px 10px;border-radius:6px;letter-spacing:0.8px;}}
    .status-badge{{display:flex;align-items:center;gap:14px;font-size:0.82rem;color:{text_sub};font-family:'JetBrains Mono',monospace;}}
    .live-dot{{width:9px;height:9px;border-radius:50%;background:#10B981;box-shadow:0 0 10px #10B981;animation:pulse 1.6s infinite;}}

    /* ---- Role Selector ---- */
    .role-container{{background:{surface_hex};border:1px solid {border_hex};border-radius:16px;padding:20px;margin-bottom:18px;animation:fadeIn 0.5s ease;}}
    .role-title{{font-size:1.1rem;font-weight:800;margin-bottom:5px;}}
    .role-subtitle{{font-size:0.86rem;color:{text_sub};margin-bottom:14px;}}
    .role-switch-grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;}}
    @media(max-width:800px){{.role-switch-grid{{grid-template-columns:1fr;}}}}
    .role-btn{{background:{input_bg};border:2px solid {border_hex};border-radius:14px;padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:14px;transition:all 0.22s ease;text-align:left;}}
    .role-btn:hover{{border-color:{accent_hex};transform:translateY(-2px);}}
    .role-btn.active{{border-color:{accent_hex};background:rgba(37,99,235,{"0.12" if is_dark else "0.07"});box-shadow:0 0 20px rgba(37,99,235,0.2);}}
    .role-icon{{width:46px;height:46px;border-radius:12px;background:rgba(37,99,235,0.14);color:#60A5FA;display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0;}}
    .role-btn.active .role-icon{{background:{accent_hex};color:#fff;}}
    .role-name{{font-size:1.0rem;font-weight:800;color:{text_main};}}
    .role-desc{{font-size:0.8rem;color:{text_sub};margin-top:3px;}}

    /* ---- Views ---- */
    .view-section{{display:none;animation:fadeIn 0.4s ease;}}
    .view-section.active{{display:block;}}
    .card{{background:{surface_hex};border:1px solid {border_hex};border-radius:16px;padding:22px;box-shadow:0 4px 20px {card_shadow};margin-bottom:20px;}}
    .portal-grid{{display:grid;grid-template-columns:1.05fr 1.3fr;gap:20px;}}
    @media(max-width:1050px){{.portal-grid{{grid-template-columns:1fr;}}}}

    .section-title{{font-size:1.1rem;font-weight:800;margin-bottom:5px;display:flex;align-items:center;gap:10px;}}
    .section-desc{{font-size:0.84rem;color:{text_sub};margin-bottom:16px;}}

    /* ---- Inputs ---- */
    .form-group{{margin-bottom:14px;}}
    .form-label{{display:block;font-size:0.8rem;font-weight:700;color:{text_sub};margin-bottom:5px;text-transform:uppercase;letter-spacing:0.4px;}}
    .form-select{{width:100%;background:{input_bg};border:1px solid {border_hex};border-radius:10px;padding:11px 13px;color:{text_main};font-size:0.9rem;outline:none;cursor:pointer;transition:border 0.2s;}}
    .form-select:focus{{border-color:{accent_hex};}}

    /* ---- Time Slot Selector ---- */
    .timeslot-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px;}}
    .ts-btn{{background:{input_bg};border:2px solid {border_hex};border-radius:12px;padding:12px 14px;cursor:pointer;text-align:left;transition:all 0.2s;}}
    .ts-btn:hover{{border-color:{accent_hex};transform:translateY(-1px);}}
    .ts-btn.active{{border-color:{accent_hex};background:rgba(37,99,235,{"0.14" if is_dark else "0.08"});}}
    .ts-label{{font-size:0.78rem;font-weight:800;color:{text_sub};text-transform:uppercase;letter-spacing:0.5px;}}
    .ts-name{{font-size:0.95rem;font-weight:800;color:{text_main};margin-top:2px;}}
    .ts-hour{{font-size:0.78rem;color:{text_dim};margin-top:1px;font-family:'JetBrains Mono',monospace;}}
    .ts-surge{{display:inline-block;margin-top:4px;font-size:0.74rem;font-weight:800;padding:2px 8px;border-radius:5px;}}
    .surge-low{{background:rgba(16,185,129,0.15);color:#34D399;}}
    .surge-mid{{background:rgba(245,158,11,0.15);color:#FBBF24;}}
    .surge-high{{background:rgba(239,68,68,0.15);color:#F87171;}}

    /* ---- Vehicle Tiers ---- */
    .ride-options{{display:flex;flex-direction:column;gap:9px;margin-bottom:16px;}}
    .ride-card{{background:{input_bg};border:1px solid {border_hex};border-radius:12px;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:all 0.2s;}}
    .ride-card:hover{{border-color:{accent_hex};transform:translateX(3px);}}
    .ride-card.selected{{border-color:{accent_hex};background:rgba(37,99,235,{"0.14" if is_dark else "0.08"});}}
    .ride-name{{font-size:0.95rem;font-weight:800;}}
    .ride-meta{{font-size:0.78rem;color:{text_sub};margin-top:2px;}}
    .ride-price{{font-size:1.1rem;font-weight:800;color:#38BDF8;text-align:right;}}
    .ride-eta{{font-size:0.72rem;color:{text_dim};text-align:right;}}

    /* ---- Buttons ---- */
    .btn-action{{width:100%;background:linear-gradient(135deg,{accent_hex},#1D4ED8);border:none;color:#fff;font-size:0.94rem;font-weight:700;padding:13px;border-radius:12px;cursor:pointer;transition:all 0.22s;display:flex;align-items:center;justify-content:center;gap:9px;box-shadow:0 4px 14px rgba(37,99,235,0.3);}}
    .btn-action:hover{{transform:translateY(-2px);box-shadow:0 6px 20px rgba(37,99,235,0.45);}}

    /* ---- Price Forecast Card ---- */
    .forecast-card{{background:{input_bg};border:1px solid {border_hex};border-radius:14px;padding:18px;margin-bottom:16px;}}
    .forecast-title{{font-size:0.78rem;font-weight:800;text-transform:uppercase;letter-spacing:0.5px;color:{text_dim};margin-bottom:14px;display:flex;align-items:center;gap:8px;}}
    .forecast-row{{display:flex;justify-content:space-between;align-items:center;padding:9px 12px;border-radius:10px;margin-bottom:6px;border:1px solid transparent;transition:all 0.2s;}}
    .forecast-row.cheapest{{border-color:#10B981;background:rgba(16,185,129,0.09);}}
    .forecast-row:last-child{{margin-bottom:0;}}
    .forecast-slot-name{{font-size:0.88rem;font-weight:700;}}
    .forecast-slot-time{{font-size:0.75rem;color:{text_dim};font-family:'JetBrains Mono',monospace;margin-top:2px;}}
    .forecast-price{{font-size:1.1rem;font-weight:800;color:#38BDF8;}}
    .forecast-price.cheapest-price{{color:#10B981;}}
    .cheapest-tag{{font-size:0.68rem;font-weight:800;background:rgba(16,185,129,0.15);color:#34D399;padding:2px 7px;border-radius:4px;margin-left:6px;}}

    /* ---- Route Visualizer ---- */
    .route-node-box{{background:{surface_hex};border:1px solid {border_hex};border-radius:16px;padding:20px;margin-bottom:18px;}}
    .route-node{{display:flex;align-items:flex-start;gap:13px;}}
    .dot-node{{width:13px;height:13px;border-radius:50%;margin-top:4px;flex-shrink:0;}}
    .dot-green{{background:#10B981;box-shadow:0 0 12px rgba(16,185,129,0.8);animation:pulseGreen 2s infinite ease-in-out;}}
    .dot-red{{background:#EF4444;box-shadow:0 0 12px rgba(239,68,68,0.6);}}
    .route-line{{width:2px;height:44px;background:{border_hex};margin-left:5px;margin-top:4px;margin-bottom:4px;position:relative;}}
    .route-packet{{position:absolute;width:4px;height:10px;background:#38BDF8;border-radius:2px;left:-1px;box-shadow:0 0 8px #38BDF8;animation:travelDown 1.8s infinite linear;}}
    @keyframes travelDown{{0%{{top:0;opacity:0;}}20%{{opacity:1;}}80%{{opacity:1;}}100%{{top:34px;opacity:0;}}}}
    @keyframes pulseGreen{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.25);}}}}

    /* ---- Info Tiles ---- */
    .info-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin-bottom:14px;}}
    .info-tile{{background:{surface_hex};border:1px solid {border_hex};border-radius:12px;padding:13px;text-align:center;}}
    .info-label{{font-size:0.72rem;font-weight:700;color:{text_dim};text-transform:uppercase;letter-spacing:0.4px;}}
    .info-val{{font-size:1.2rem;font-weight:800;margin-top:4px;}}

    /* ---- Surge Banner ---- */
    .surge-banner{{border-radius:12px;padding:14px 16px;margin-bottom:14px;font-size:0.88rem;font-weight:600;display:flex;align-items:center;gap:10px;}}
    .surge-low-banner{{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);color:#34D399;}}
    .surge-high-banner{{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#F87171;}}
    .surge-mid-banner{{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);color:#FBBF24;}}

    /* ---- Your driver Ride Request ---- */
    .driver-ride-box{{background:{input_bg};border:2px solid {border_hex};border-radius:16px;padding:19px;margin-bottom:20px;position:relative;overflow:hidden;}}
    .driver-ride-box.pulsing{{border-color:#38BDF8;box-shadow:0 0 25px rgba(56,189,248,0.22);}}
    .driver-ride-badge{{display:inline-flex;align-items:center;gap:6px;font-size:0.72rem;font-weight:800;padding:4px 10px;border-radius:6px;background:rgba(56,189,248,0.14);color:#38BDF8;text-transform:uppercase;margin-bottom:11px;}}
    .btn-driver-accept{{background:#10B981;color:#fff;border:none;padding:11px 18px;font-weight:800;font-size:0.93rem;border-radius:10px;cursor:pointer;display:flex;align-items:center;gap:7px;transition:all 0.2s;}}
    .btn-driver-accept:hover{{background:#059669;transform:scale(1.02);}}
    .btn-driver-pass{{background:transparent;color:{text_sub};border:1px solid {border_hex};padding:11px 16px;font-weight:700;font-size:0.9rem;border-radius:10px;cursor:pointer;transition:all 0.2s;}}
    .btn-driver-pass:hover{{background:rgba(239,68,68,0.09);color:#EF4444;border-color:#EF4444;}}

    /* ---- Demand Hotspots ---- */
    .hotspot-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px;margin-top:16px;}}
    .hotspot-card{{background:{surface_hex};border:1px solid {border_hex};border-radius:14px;padding:16px;transition:all 0.2s ease;}}
    .hotspot-card:hover{{transform:translateY(-2px);border-color:rgba(37,99,235,0.45);}}
    .hotspot-card.high{{border-left:4px solid #EF4444;}}
    .hotspot-card.moderate{{border-left:4px solid #F59E0B;}}
    .hotspot-card.low{{border-left:4px solid #10B981;}}
    .badge-high{{background:rgba(239,68,68,0.16);color:#F87171;padding:3px 8px;border-radius:5px;font-weight:800;font-size:0.7rem;}}
    .badge-mod{{background:rgba(245,158,11,0.16);color:#FBBF24;padding:3px 8px;border-radius:5px;font-weight:800;font-size:0.7rem;}}
    .badge-low{{background:rgba(16,185,129,0.16);color:#34D399;padding:3px 8px;border-radius:5px;font-weight:800;font-size:0.7rem;}}

    /* ---- Your driver Hour Plan ---- */
    .hour-plan-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-top:14px;}}
    .hour-zone-card{{background:{input_bg};border:1px solid {border_hex};border-radius:12px;padding:14px;}}
    .hz-rank{{font-size:0.72rem;font-weight:800;color:{text_dim};text-transform:uppercase;margin-bottom:4px;}}
    .hz-zone{{font-size:0.96rem;font-weight:800;}}
    .hz-advice{{font-size:0.8rem;color:{text_sub};margin-top:4px;}}
    .hz-earn{{font-size:0.85rem;font-weight:800;color:#10B981;margin-top:6px;}}

    /* ---- Toast ---- */
    .toast{{position:fixed;bottom:22px;right:22px;background:{surface_hex};border:1px solid rgba(37,99,235,0.4);padding:13px 20px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.5);color:{text_main};font-weight:600;font-size:0.86rem;transform:translateY(100px);opacity:0;transition:all 0.3s cubic-bezier(0.16,1,0.3,1);z-index:1000;}}
    .toast.show{{transform:translateY(0);opacity:1;}}

    @keyframes fadeIn{{from{{opacity:0;transform:translateY(8px);}}to{{opacity:1;transform:translateY(0);}}}}
    @keyframes pulse{{0%{{transform:scale(0.95);opacity:0.8;}}50%{{transform:scale(1.15);opacity:1;}}100%{{transform:scale(0.95);opacity:0.8;}}}}
</style>
</head>
<body>

<canvas id="bg-canvas"></canvas>

<div class="wrap">

    <!-- === HEADER === -->
    <div class="brand-bar">
        <div class="brand-title">
            <i class="fa-solid fa-route" style="color:#38BDF8;"></i>
            <span>CAB FLOW</span>
            <span class="brand-badge">Delhi NCR</span>
        </div>
        <div class="status-badge">
            <div style="display:flex;align-items:center;gap:8px;">
                <div class="live-dot" id="api-status-dot"></div>
                <span id="api-status-text">Connecting...</span>
            </div>
            
        </div>
    </div>

    <!-- === ROLE SELECTOR === -->
    <div class="role-container">
        <div class="role-title"><i class="fa-solid fa-hand-pointer" style="color:#60A5FA;margin-right:8px;"></i>Who Are You?</div>
        <div class="role-subtitle">Are you a rider or a driver? Pick one below.</div>
        <div class="role-switch-grid">
            <div class="role-btn active" id="btn-role-customer" onclick="setRole('customer')">
                <div class="role-icon"><i class="fa-solid fa-user"></i></div>
                <div>
                    <div class="role-name">I Want a Ride</div>
                    <div class="role-desc">See prices, compare times, and book a cab anywhere in Delhi NCR.</div>
                </div>
            </div>
            <div class="role-btn" id="btn-role-driver" onclick="setRole('driver')">
                <div class="role-icon"><i class="fa-solid fa-car"></i></div>
                <div>
                    <div class="role-name">I Am a Driver</div>
                    <div class="role-desc">Get ride requests and see where riders need cabs right now.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- ==================================================== -->
    <!-- PORTAL 1: CUSTOMER                                   -->
    <!-- ==================================================== -->
    <div id="view-customer" class="view-section active">
        <div class="portal-grid">

            <!-- LEFT: Booking Form + Time Forecast -->
            <div>
                <div class="card">
                    <div class="section-title">
                        <i class="fa-solid fa-location-crosshairs" style="color:#38BDF8;"></i>
                        Plan Your Ride
                    </div>
                    <div class="section-desc">Tell us where you want to go and when — we will show you the price.</div>

                    <div class="form-group">
                        <label class="form-label"><i class="fa-solid fa-circle-dot" style="color:#10B981;margin-right:5px;"></i>Pickup Place</label>
                        <select id="cust-pickup" class="form-select" onchange="onTripChange()"></select>
                    </div>

                    <div class="form-group">
                        <label class="form-label"><i class="fa-solid fa-location-pin" style="color:#EF4444;margin-right:5px;"></i>Where To?</label>
                        <select id="cust-drop" class="form-select" onchange="onTripChange()"></select>
                    </div>

                    <!-- TIME SLOT SELECTOR (Core SML Feature) -->
                    <div class="form-group">
                        <label class="form-label"><i class="fa-solid fa-clock" style="color:#F59E0B;margin-right:5px;"></i>What time do you want to go?</label>
                        <div class="timeslot-grid">
                            <div class="ts-btn active" id="ts-morning" onclick="selectSlot(this,'morning',9)">
                                <div class="ts-label"><i class="fa-solid fa-sun"></i> Morning</div>
                                <div class="ts-name">8 AM to 11 AM</div>
                                <div class="ts-hour">Hour: 9</div>
                                <span class="ts-surge surge-mid">Slightly Busy</span>
                            </div>
                            <div class="ts-btn" id="ts-day" onclick="selectSlot(this,'day',13)">
                                <div class="ts-label"><i class="fa-solid fa-cloud-sun"></i> Daytime</div>
                                <div class="ts-name">11 AM to 5 PM</div>
                                <div class="ts-hour">Hour: 1 PM</div>
                                <span class="ts-surge surge-low">Normal</span>
                            </div>
                            <div class="ts-btn" id="ts-evening" onclick="selectSlot(this,'evening',18)">
                                <div class="ts-label"><i class="fa-solid fa-moon"></i> Evening Rush</div>
                                <div class="ts-name">5 PM to 9 PM</div>
                                <div class="ts-hour">Hour: 6 PM</div>
                                <span class="ts-surge surge-high">Very Busy</span>
                            </div>
                            <div class="ts-btn" id="ts-night" onclick="selectSlot(this,'night',1)">
                                <div class="ts-label"><i class="fa-solid fa-star-and-crescent"></i> Late Night</div>
                                <div class="ts-name">11 PM to 5 AM</div>
                                <div class="ts-hour">Hour: 1 AM</div>
                                <span class="ts-surge surge-mid">Night Rates</span>
                            </div>
                        </div>
                    </div>

                    <!-- Vehicle Tiers -->
                    <div style="font-size:0.8rem;font-weight:700;color:{text_sub};margin-bottom:8px;text-transform:uppercase;letter-spacing:0.4px;">Pick Your Cab:</div>
                    <div class="ride-options">
                        <div class="ride-card selected" onclick="selectTier(this,'Flow Auto','Auto',9.5,30,'Bajaj Maxima CNG','DL 1R B 3302','Rajesh Gupta')">
                            <div>
                                <div class="ride-name"><i class="fa-solid fa-motorcycle" style="color:#60A5FA;margin-right:7px;"></i>Flow Auto</div>
                                <div class="ride-meta">3 Seats &bull; Auto, quick in traffic</div>
                            </div>
                            <div>
                                <div class="ride-price" id="p-auto">Rs. 190</div>
                                <div class="ride-eta">1 min away</div>
                            </div>
                        </div>
                        <div class="ride-card" onclick="selectTier(this,'Flow Go','Go Sedan',14,45,'Maruti Suzuki Dzire','DL 1Y AB 7821','Vikram Singh')">
                            <div>
                                <div class="ride-name"><i class="fa-solid fa-car" style="color:#60A5FA;margin-right:7px;"></i>Flow Go</div>
                                <div class="ride-meta">4 Seats &bull; AC car, good price</div>
                            </div>
                            <div>
                                <div class="ride-price" id="p-go">Rs. 270</div>
                                <div class="ride-eta">2 mins away</div>
                            </div>
                        </div>
                        <div class="ride-card" onclick="selectTier(this,'Flow Prime','Premier Sedan',18.5,60,'Honda City i-VTEC','DL 2C XY 4419','Amit Sharma')">
                            <div>
                                <div class="ride-name"><i class="fa-solid fa-star" style="color:#F59E0B;margin-right:7px;"></i>Flow Prime</div>
                                <div class="ride-meta">4 Seats &bull; Comfy car, best drivers</div>
                            </div>
                            <div>
                                <div class="ride-price" id="p-prime">Rs. 360</div>
                                <div class="ride-eta">4 mins away</div>
                            </div>
                        </div>
                        <div class="ride-card" onclick="selectTier(this,'Flow XL','Uber XL',25,90,'Toyota Innova Crysta','HR 26 DR 9012','Gurpreet Singh')">
                            <div>
                                <div class="ride-name"><i class="fa-solid fa-van-shuttle" style="color:#60A5FA;margin-right:7px;"></i>Flow XL</div>
                                <div class="ride-meta">6 Seats &bull; Big car for groups</div>
                            </div>
                            <div>
                                <div class="ride-price" id="p-xl">Rs. 490</div>
                                <div class="ride-eta">6 mins away</div>
                            </div>
                        </div>
                    </div>

                    <!-- Book Button -->
                    <button class="btn-action" onclick="confirmCustomerRide()">
                        <i class="fa-solid fa-check"></i>
                        <span id="cust-btn-text">Book Ride Now &bull; Flow Auto (Rs. 190)</span>
                    </button>

                    <!-- Booking Confirmation -->
                    <div id="cust-dispatch-banner" style="display:none;background:rgba(16,185,129,0.1);border:1px solid #10B981;border-radius:14px;padding:16px;margin-top:16px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#10B981;font-weight:800;font-size:0.9rem;"><i class="fa-solid fa-circle-check" style="margin-right:7px;"></i>YOUR RIDE IS BOOKED!</span>
                            <span style="font-size:0.78rem;color:#38BDF8;font-weight:700;">DRIVER IS COMING</span>
                        </div>
                        <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <div style="font-size:1.02rem;font-weight:800;" id="cust-disp-driver">Rajesh Gupta</div>
                                <div style="font-size:0.8rem;color:{text_sub};" id="cust-disp-car">Bajaj Maxima CNG &bull; DL 1R B 3302</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:0.7rem;color:{text_dim};font-weight:700;">YOUR PIN</div>
                                <div style="font-size:1.3rem;font-weight:800;color:#38BDF8;letter-spacing:3px;">5192</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- RIGHT: Route + Price Forecast Panel -->
            <div>
                <!-- Route Visualizer -->
                <div class="route-node-box">
                    <div style="font-size:0.76rem;font-weight:700;color:{text_dim};text-transform:uppercase;letter-spacing:0.4px;margin-bottom:12px;">Your Route</div>
                    <div class="route-node">
                        <div class="dot-node dot-green"></div>
                        <div>
                            <div style="font-size:0.7rem;color:{text_dim};font-weight:700;text-transform:uppercase;">Pickup</div>
                            <div style="font-size:1.0rem;font-weight:700;" id="cust-node-pickup">Barakhamba Road, Connaught Place</div>
                        </div>
                    </div>
                    <div class="route-line"><div class="route-packet"></div></div>
                    <div class="route-node">
                        <div class="dot-node dot-red"></div>
                        <div>
                            <div style="font-size:0.7rem;color:{text_dim};font-weight:700;text-transform:uppercase;">Drop</div>
                            <div style="font-size:1.0rem;font-weight:700;" id="cust-node-drop">Cyber City / Cyber Hub, DLF Gurugram</div>
                        </div>
                    </div>
                </div>

                <!-- Trip Metrics -->
                <div class="info-grid">
                    <div class="info-tile">
                        <div class="info-label"><i class="fa-solid fa-road"></i> Distance</div>
                        <div class="info-val" id="cust-metric-dist">26.0 km</div>
                    </div>
                    <div class="info-tile">
                        <div class="info-label"><i class="fa-solid fa-clock"></i> Time</div>
                        <div class="info-val" id="cust-metric-duration">42 mins</div>
                    </div>
                    <div class="info-tile">
                        <div class="info-label"><i class="fa-solid fa-indian-rupee-sign"></i> Fare</div>
                        <div class="info-val" id="cust-metric-fare" style="color:#38BDF8;">Rs. 340</div>
                    </div>
                </div>

                <!-- Surge Banner -->
                <div id="surge-banner" class="surge-banner surge-mid-banner">
                    <i class="fa-solid fa-bolt"></i>
                    <span id="surge-banner-text">Morning: 1.30x surge — prices are slightly higher than usual.</span>
                </div>

                <!-- === CORE SML FEATURE: Price Forecast Across All Time Slots === -->
                <div class="forecast-card">
                    <div class="forecast-title">
                        <i class="fa-solid fa-chart-line" style="color:#38BDF8;"></i>
                        Compare Prices for Each Time
                    </div>
                    <div style="font-size:0.82rem;color:{text_sub};margin-bottom:14px;">
                        See how much the ride costs at different times. Travel when it is cheapest!
                    </div>

                    <div id="forecast-morning" class="forecast-row">
                        <div>
                            <div class="forecast-slot-name"><i class="fa-solid fa-sun" style="color:#F59E0B;margin-right:6px;"></i>Morning</div>
                            <div class="forecast-slot-time">8 AM – 11 AM • Slightly busy</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="forecast-price" id="fc-morning">Rs. --</div>
                        </div>
                    </div>

                    <div id="forecast-day" class="forecast-row">
                        <div>
                            <div class="forecast-slot-name"><i class="fa-solid fa-cloud-sun" style="color:#60A5FA;margin-right:6px;"></i>Daytime</div>
                            <div class="forecast-slot-time">11 AM – 5 PM • Normal</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="forecast-price" id="fc-day">Rs. --</div>
                        </div>
                    </div>

                    <div id="forecast-evening" class="forecast-row">
                        <div>
                            <div class="forecast-slot-name"><i class="fa-solid fa-moon" style="color:#818CF8;margin-right:6px;"></i>Evening Rush</div>
                            <div class="forecast-slot-time">5 PM – 9 PM • Very busy</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="forecast-price" id="fc-evening">Rs. --</div>
                        </div>
                    </div>

                    <div id="forecast-night" class="forecast-row">
                        <div>
                            <div class="forecast-slot-name"><i class="fa-solid fa-star-and-crescent" style="color:#94A3B8;margin-right:6px;"></i>Late Night</div>
                            <div class="forecast-slot-time">11 PM – 5 AM • Night rates</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="forecast-price" id="fc-night">Rs. --</div>
                        </div>
                    </div>

                    <div id="cheapest-advice" style="margin-top:14px;background:rgba(16,185,129,0.09);border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:12px 14px;font-size:0.86rem;">
                        <i class="fa-solid fa-lightbulb" style="color:#34D399;margin-right:7px;"></i>
                        <span id="cheapest-advice-text" style="color:{text_main};">Finding the cheapest time for you...</span>
                    </div>
                </div>

                <!-- ML Reliability -->
                <div class="card" style="padding:16px;margin-bottom:0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                        <div>
                            <div style="font-size:0.72rem;font-weight:700;color:{text_dim};text-transform:uppercase;">Will my driver come?</div>
                            <div style="font-size:0.95rem;font-weight:800;color:#10B981;margin-top:3px;" id="cust-risk-label">Yes! Drivers almost never cancel this ride</div>
                        </div>
                        <button onclick="pingStandby()" class="btn-action" style="width:auto;padding:9px 16px;font-size:0.82rem;background:rgba(37,99,235,0.14);color:#60A5FA;border:1px solid rgba(37,99,235,0.35);box-shadow:none;">
                            <i class="fa-solid fa-bell"></i> Call More Drivers
                        </button>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- ==================================================== -->
    <!-- PORTAL 2: DRIVER HUB                                 -->
    <!-- ==================================================== -->
    <div id="view-driver" class="view-section">

        <!-- Your driver Status Bar -->
        <div class="card" style="margin-bottom:18px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:50px;height:50px;border-radius:50%;background:rgba(16,185,129,0.14);display:flex;align-items:center;justify-content:center;font-size:1.4rem;color:#10B981;">
                        <i class="fa-solid fa-id-card"></i>
                    </div>
                    <div>
                        <div style="font-size:1.15rem;font-weight:800;">Welcome, Rajesh Gupta</div>
                        <div style="font-size:0.83rem;color:{text_sub};">Bajaj Maxima CNG &bull; <strong>DL 1R B 3302</strong> &bull; Rating: <strong>4.92</strong></div>
                    </div>
                </div>
                <div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap;">
                    <div style="text-align:right;">
                        <div style="font-size:0.72rem;font-weight:700;color:{text_dim};text-transform:uppercase;">Money Earned Today</div>
                        <div style="font-size:1.35rem;font-weight:800;color:#10B981;" id="driver-wallet-val">Rs. 1,840</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.72rem;font-weight:700;color:{text_dim};text-transform:uppercase;">Rides Done</div>
                        <div style="font-size:1.35rem;font-weight:800;color:#38BDF8;" id="driver-trips-val">6 Trips</div>
                    </div>
                    <button id="driver-toggle-online" onclick="toggleDriverOnline()" class="btn-action" style="width:auto;padding:11px 18px;background:#10B981;box-shadow:none;">
                        <i class="fa-solid fa-power-off"></i> <span id="driver-status-text">I Am Ready</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Incoming Ride Request -->
        <div class="driver-ride-box pulsing" id="driver-incoming-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                <div>
                    <span class="driver-ride-badge"><i class="fa-solid fa-bell"></i> NEW RIDE!</span>
                    <div style="font-size:1.25rem;font-weight:800;margin-top:2px;" id="driver-req-rider">Aarav Mehta</div>
                    <div style="font-size:0.84rem;color:{text_sub};">Pays by Cash or UPI • Good rider</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.73rem;color:{text_dim};font-weight:700;">YOU WILL EARN</div>
                    <div style="font-size:1.55rem;font-weight:800;color:#10B981;" id="driver-req-fare">Rs. 320</div>
                    <div style="font-size:0.74rem;color:#38BDF8;font-weight:700;" id="driver-req-dist">19.4 km &bull; 35 mins</div>
                </div>
            </div>

            <div style="margin:14px 0;padding:13px;background:{surface_hex};border:1px solid {border_hex};border-radius:12px;display:grid;grid-template-columns:1fr 1fr;gap:13px;">
                <div>
                    <div style="font-size:0.7rem;color:{text_dim};font-weight:700;text-transform:uppercase;">Pickup</div>
                    <div style="font-size:0.92rem;font-weight:800;color:#10B981;margin-top:2px;" id="driver-req-pickup">Barakhamba Road, Connaught Place</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:{text_dim};font-weight:700;text-transform:uppercase;">Drop</div>
                    <div style="font-size:0.92rem;font-weight:800;color:#EF4444;margin-top:2px;" id="driver-req-drop">Cyber City / Cyber Hub, DLF Gurugram</div>
                </div>
            </div>

            <div style="display:flex;gap:13px;align-items:center;">
                <button class="btn-driver-accept" onclick="acceptDriverRide()"><i class="fa-solid fa-check"></i> Accept Ride</button>
                <button class="btn-driver-pass" onclick="passDriverRide()"><i class="fa-solid fa-xmark"></i> Skip / Next</button>
                <div style="margin-left:auto;font-size:0.82rem;color:{text_dim};font-family:'JetBrains Mono',monospace;">
                    Skipping in: <strong style="color:#F59E0B;" id="driver-timer-val">22s</strong>
                </div>
            </div>
        </div>

        <!-- Active Trip Box -->
        <div id="driver-active-trip" style="display:none;background:rgba(37,99,235,0.1);border:2px solid #2563EB;border-radius:16px;padding:20px;margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:13px;">
                <div>
                    <span style="background:#2563EB;color:#fff;font-size:0.73rem;font-weight:800;padding:4px 10px;border-radius:6px;text-transform:uppercase;">RIDE IN PROGRESS</span>
                    <div style="font-size:1.2rem;font-weight:800;margin-top:7px;" id="driver-act-rider">Aarav Mehta</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.73rem;color:{text_dim};font-weight:700;">YOU EARN</div>
                    <div style="font-size:1.45rem;font-weight:800;color:#10B981;" id="driver-act-fare">Rs. 320</div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:13px;margin-bottom:14px;">
                <div style="background:{surface_hex};padding:11px;border-radius:10px;border:1px solid {border_hex};">
                    <div style="font-size:0.7rem;color:{text_dim};font-weight:700;">ROUTE</div>
                    <div style="font-size:0.88rem;font-weight:700;margin-top:3px;" id="driver-act-route">Connaught Place to Cyber City</div>
                </div>
                <div style="background:{surface_hex};padding:11px;border-radius:10px;border:1px solid {border_hex};">
                    <div style="font-size:0.7rem;color:{text_dim};font-weight:700;">RIDER PIN</div>
                    <div style="font-size:1.1rem;font-weight:800;color:#38BDF8;letter-spacing:3px;">5192</div>
                </div>
            </div>
            <div style="display:flex;gap:13px;">
                <button class="btn-action" onclick="completeDriverTrip()" style="background:#10B981;width:auto;padding:11px 22px;">
                    <i class="fa-solid fa-flag-checkered"></i> Finish Ride & Get Paid
                </button>
                <button class="btn-action" onclick="cancelDriverTrip()" style="background:transparent;border:1px solid #EF4444;color:#EF4444;width:auto;padding:11px 18px;box-shadow:none;">
                    Cancel This Ride
                </button>
            </div>
        </div>

        <!-- Hour-Based Demand Planner (SML Your driver Feature) -->
        <div class="card" style="margin-bottom:18px;">
            <div class="section-title">
                <i class="fa-solid fa-calendar-clock" style="color:#F59E0B;"></i>
                Best Times to Drive Today
            </div>
            <div class="section-desc">
                Here is when and where you will get the most rides today.
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
                <button class="btn-action" onclick="showHourPlan('morning')" id="hpbtn-morning" style="width:auto;padding:9px 18px;font-size:0.86rem;background:rgba(37,99,235,0.6);">
                    <i class="fa-solid fa-sun"></i> Morning (8–11 AM)
                </button>
                <button class="btn-action" onclick="showHourPlan('day')" id="hpbtn-day" style="width:auto;padding:9px 18px;font-size:0.86rem;background:rgba(37,99,235,0.3);">
                    <i class="fa-solid fa-cloud-sun"></i> Daytime (11–5 PM)
                </button>
                <button class="btn-action" onclick="showHourPlan('evening')" id="hpbtn-evening" style="width:auto;padding:9px 18px;font-size:0.86rem;background:rgba(37,99,235,0.3);">
                    <i class="fa-solid fa-moon"></i> Evening (5–9 PM)
                </button>
                <button class="btn-action" onclick="showHourPlan('night')" id="hpbtn-night" style="width:auto;padding:9px 18px;font-size:0.86rem;background:rgba(37,99,235,0.3);">
                    <i class="fa-solid fa-star-and-crescent"></i> Late Night
                </button>
            </div>
            <div class="hour-plan-grid" id="hour-plan-container">
                <!-- filled by JS -->
            </div>
        </div>

        <!-- Live Demand Radar -->
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:13px;margin-bottom:16px;">
                <div>
                    <div class="section-title">
                        <i class="fa-solid fa-tower-broadcast" style="color:#38BDF8;"></i>
                        Where Are Riders Right Now?
                    </div>
                    <div class="section-desc" style="margin-bottom:0;">
                        Go to <strong style="color:#EF4444;">busy areas</strong> to earn more money.
                    </div>
                </div>
                <button onclick="refreshDriverDemand()" class="btn-action" style="width:auto;padding:9px 18px;font-size:0.86rem;">
                    <i class="fa-solid fa-rotate-right"></i> Refresh
                </button>
            </div>
            <div class="hotspot-grid" id="driver-hotspots-container">
                <div style="color:{text_sub};padding:14px;">Finding busy areas...</div>
            </div>
        </div>

    </div>

</div>

<div id="toast" class="toast"><span id="toast-text">Done!</span></div>

<script>
// ===== CANVAS PARTICLES =====
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let W = canvas.width = window.innerWidth;
let H = canvas.height = window.innerHeight;
window.addEventListener('resize', () => {{ W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }});
const particles = [];
for (let i = 0; i < 35; i++) {{
    particles.push({{ x: Math.random()*W, y: Math.random()*H, vx: (Math.random()-0.5)*0.32, vy: (Math.random()-0.5)*0.32, r: Math.random()*2.2+0.8 }});
}}
function animateParticles() {{
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle = '{particle_fill}';
    ctx.strokeStyle = '{particle_stroke}';
    particles.forEach((p,i) => {{
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI*2); ctx.fill();
        for (let j = i+1; j < particles.length; j++) {{
            const q = particles[j];
            const d = Math.hypot(p.x-q.x, p.y-q.y);
            if (d < 140) {{ ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y); ctx.stroke(); }}
        }}
    }});
    requestAnimationFrame(animateParticles);
}}
animateParticles();

// ===== API =====
let API_BASE = 'http://127.0.0.1:8000';

function checkApiHealth() {{
    const dot = document.getElementById('api-status-dot');
    const txt = document.getElementById('api-status-text');
    fetch(API_BASE + '/api/health')
        .then(r => r.json())
        .then(d => {{
            if (d && d.status === 'healthy') {{
                dot.style.background = '#10B981'; dot.style.boxShadow = '0 0 10px #10B981';
                txt.innerText = 'Connected — Ready to use'; txt.style.color = '#10B981';
            }}
        }})
        .catch(() => {{
            const alt = API_BASE.includes('localhost') ? 'http://127.0.0.1:8000' : 'http://localhost:8000';
            fetch(alt + '/api/health').then(r => r.json()).then(d => {{
                if (d && d.status === 'healthy') {{
                    API_BASE = alt;
                    dot.style.background = '#10B981'; dot.style.boxShadow = '0 0 10px #10B981';
                    txt.innerText = 'Connected — Ready to use'; txt.style.color = '#10B981';
                }}
            }}).catch(() => {{
                dot.style.background = '#EF4444'; dot.style.boxShadow = '0 0 10px #EF4444';
                txt.innerText = 'Not connected. Please restart the app.'; txt.style.color = '#EF4444';
            }});
        }});
}}
checkApiHealth();
setInterval(checkApiHealth, 12000);

// ===== NCR LOCATIONS =====
const ncrSectors = {NCR_JSON};

// ===== ROLE SWITCH =====
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
        showHourPlan('morning');
    }}
}}

// ===== POPULATE LOCATION SELECTS =====
function populateLocations() {{
    ['cust-pickup','cust-drop'].forEach((id, idx) => {{
        const sel = document.getElementById(id);
        sel.innerHTML = '';
        ncrSectors.forEach(loc => {{
            const opt = document.createElement('option');
            opt.value = opt.innerText = loc;
            if (idx === 0 && loc.includes('Barakhamba')) opt.selected = true;
            if (idx === 1 && loc.includes('Cyber City')) opt.selected = true;
            sel.appendChild(opt);
        }});
    }});
}}

// ===== SELECTED VEHICLE & SLOT =====
let selectedVehicle = {{ name:'Flow Auto', apiType:'Auto', rateKm:9.5, baseFare:30, model:'Bajaj Maxima CNG', plate:'DL 1R B 3302', driver:'Rajesh Gupta' }};
let selectedHour = 9;  // morning default

function selectTier(el, name, apiType, rateKm, baseFare, model, plate, driver) {{
    document.querySelectorAll('.ride-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    selectedVehicle = {{ name, apiType, rateKm, baseFare, model, plate, driver }};
    fetchPrediction(selectedHour);
}}

function selectSlot(el, slot, hour) {{
    document.querySelectorAll('.ts-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    selectedHour = hour;
    fetchPrediction(hour);
    fetchAllSlotForecast();
}}

// ===== TRIP CHANGE =====
function onTripChange() {{
    const p = document.getElementById('cust-pickup').value;
    const d = document.getElementById('cust-drop').value;
    document.getElementById('cust-node-pickup').innerText = p;
    document.getElementById('cust-node-drop').innerText = d;
    const dist = estimateDist(p, d);
    const dur = Math.round((dist / 26.0) * 60) + 4;
    document.getElementById('cust-metric-dist').innerText = dist + ' km';
    document.getElementById('cust-metric-duration').innerText = dur + ' mins';
    fetchPrediction(selectedHour);
    fetchAllSlotForecast();
    updateTierPrices(dist, dur);
}}

function estimateDist(p, d) {{
    if (p === d) return 2.4;
    if (p.includes('Airport') || d.includes('Airport')) return 24.5;
    if ((p.includes('Gurugram') && d.includes('Noida')) || (p.includes('Noida') && d.includes('Gurugram'))) return 38.0;
    if ((p.includes('Gurugram') && d.includes('Faridabad')) || (p.includes('Faridabad') && d.includes('Gurugram'))) return 42.0;
    if (p.includes('Faridabad') || d.includes('Faridabad')) return 32.0;
    if (p.includes('Ghaziabad') || d.includes('Ghaziabad')) return 28.0;
    if (p.includes('Connaught') || d.includes('Connaught')) return 14.0;
    return 18.5;
}}

function updateTierPrices(dist, dur) {{
    const tiers = [
        {{ id:'p-auto',  base:30, km:9.5 }},
        {{ id:'p-go',    base:45, km:14.0 }},
        {{ id:'p-prime', base:60, km:18.5 }},
        {{ id:'p-xl',    base:90, km:25.0 }}
    ];
    tiers.forEach(t => {{
        document.getElementById(t.id).innerText = 'Rs. ' + Math.round(t.base + dist*t.km + dur*1.5);
    }});
}}

// ===== CORE ML PREDICTION =====
function fetchPrediction(hour) {{
    const p  = document.getElementById('cust-pickup').value;
    const d  = document.getElementById('cust-drop').value;
    const dist = estimateDist(p, d);

    fetch(API_BASE + '/api/predict/fare', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{ ride_distance: dist, vehicle_type: selectedVehicle.apiType, hour: hour, avg_vtat: 8.5 }})
    }})
    .then(r => r.json())
    .then(data => {{
        if (data && data.estimated_fare_inr) {{
            const fare = Math.round(data.estimated_fare_inr);
            document.getElementById('cust-metric-fare').innerText = 'Rs. ' + fare;
            document.getElementById('cust-btn-text').innerText = 'Book Ride — ' + selectedVehicle.name + ' (Rs. ' + fare + ')';

            // Surge banner update
            const surge = data.time_surge_multiplier || 1.0;
            const slotName = data.time_slot_name || '';
            const banner = document.getElementById('surge-banner');
            const bannerText = document.getElementById('surge-banner-text');
            banner.className = 'surge-banner ' + (surge >= 1.4 ? 'surge-high-banner' : surge >= 1.2 ? 'surge-mid-banner' : 'surge-low-banner');
            bannerText.innerText = slotName + ': ' + surge + 'x surge — ' + (surge >= 1.4 ? 'prices are high now. Try a different time to save money.' : surge >= 1.2 ? 'prices are a bit higher than normal.' : 'prices are normal. Good time to book!');
        }}
    }})
    .catch(() => {{
        const dist2 = estimateDist(document.getElementById('cust-pickup').value, document.getElementById('cust-drop').value);
        const dur = Math.round((dist2 / 26.0) * 60) + 4;
        const surge = hour >= 17 && hour <= 21 ? 1.45 : hour >= 8 && hour <= 11 ? 1.30 : hour >= 23 || hour <= 5 ? 1.25 : 1.05;
        const fare = Math.round((selectedVehicle.baseFare + dist2*selectedVehicle.rateKm + dur*1.5) * surge);
        document.getElementById('cust-metric-fare').innerText = 'Rs. ' + fare;
        document.getElementById('cust-btn-text').innerText = 'Book Ride — ' + selectedVehicle.name + ' (Rs. ' + fare + ')';
    }});

    // Cancellation risk
    fetch(API_BASE + '/api/predict/cancellation', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{ avg_vtat: 8.5, vehicle_type: selectedVehicle.apiType === 'Auto' ? 'Auto' : 'Go Sedan' }})
    }})
    .then(r => r.json())
    .then(risk => {{
        if (risk && risk.cancellation_probability !== undefined) {{
            const pct = (risk.cancellation_probability * 100).toFixed(0);
            const lbl = document.getElementById('cust-risk-label');
            if (risk.cancellation_risk === 'Low') {{
                lbl.innerText = 'Very reliable — Only ' + pct + '% chance of cancellation';
                lbl.style.color = '#10B981';
            }} else {{
                lbl.innerText = 'May cancel — ' + pct + '% chance of cancelling. We will find another driver.';
                lbl.style.color = '#F59E0B';
            }}
        }}
    }}).catch(() => {{}});
}}

// ===== ALL-SLOT PRICE FORECAST (Core SML Feature) =====
function fetchAllSlotForecast() {{
    const p    = document.getElementById('cust-pickup').value;
    const d    = document.getElementById('cust-drop').value;
    const dist = estimateDist(p, d);
    const vt   = selectedVehicle.apiType;

    const slots = [
        {{ key:'morning', hour:9,  id:'fc-morning', rowId:'forecast-morning' }},
        {{ key:'day',     hour:13, id:'fc-day',     rowId:'forecast-day'     }},
        {{ key:'evening', hour:18, id:'fc-evening', rowId:'forecast-evening' }},
        {{ key:'night',   hour:1,  id:'fc-night',   rowId:'forecast-night'   }}
    ];

    const prices = {{}};
    let done = 0;

    slots.forEach(sl => {{
        document.getElementById(sl.id).innerText = 'Loading...';
        fetch(API_BASE + '/api/predict/fare', {{
            method:'POST',
            headers:{{'Content-Type':'application/json'}},
            body: JSON.stringify({{ ride_distance: dist, vehicle_type: vt, hour: sl.hour, avg_vtat: 8.5 }})
        }})
        .then(r => r.json())
        .then(data => {{
            const fare = Math.round(data.estimated_fare_inr || 0);
            prices[sl.key] = fare;
            document.getElementById(sl.id).innerText = 'Rs. ' + fare;
            done++;
            if (done === slots.length) highlightCheapest(prices, slots);
        }})
        .catch(() => {{
            // offline fallback
            const surges = {{ morning:1.30, day:1.05, evening:1.45, night:1.25 }};
            const dur = Math.round((dist/26.0)*60)+4;
            const fare = Math.round((selectedVehicle.baseFare + dist*selectedVehicle.rateKm + dur*1.5) * surges[sl.key]);
            prices[sl.key] = fare;
            document.getElementById(sl.id).innerText = 'Rs. ' + fare;
            done++;
            if (done === slots.length) highlightCheapest(prices, slots);
        }});
    }});
}}

function highlightCheapest(prices, slots) {{
    // reset
    slots.forEach(sl => {{
        document.getElementById(sl.rowId).classList.remove('cheapest');
        document.getElementById(sl.id).classList.remove('cheapest-price');
        // remove any old cheapest tag
        const existing = document.getElementById(sl.id + '-tag');
        if (existing) existing.remove();
    }});

    const names = {{ morning:'Morning (8–11 AM)', day:'Daytime (11 AM–5 PM)', evening:'Evening Rush (5–9 PM)', night:'Late Night (11 PM–5 AM)' }};
    let minKey = slots[0].key;
    slots.forEach(sl => {{ if (prices[sl.key] < prices[minKey]) minKey = sl.key; }});
    let maxKey = slots[0].key;
    slots.forEach(sl => {{ if (prices[sl.key] > prices[maxKey]) maxKey = sl.key; }});

    const minSlot = slots.find(s => s.key === minKey);
    document.getElementById(minSlot.rowId).classList.add('cheapest');
    document.getElementById(minSlot.id).classList.add('cheapest-price');

    const tag = document.createElement('span');
    tag.id = minSlot.id + '-tag';
    tag.className = 'cheapest-tag';
    tag.innerText = 'CHEAPEST';
    document.getElementById(minSlot.id).after(tag);

    const saving = prices[maxKey] - prices[minKey];
    document.getElementById('cheapest-advice-text').innerHTML =
        '<strong>Best time to travel:</strong> ' + names[minKey] +
        ' — Predicted fare is <strong>Rs. ' + prices[minKey] + '</strong>. ' +
        'You save Rs. ' + saving + ' compared to ' + names[maxKey] + ' which costs Rs. ' + prices[maxKey] + '.';
}}

function confirmCustomerRide() {{
    document.getElementById('cust-dispatch-banner').style.display = 'block';
    document.getElementById('cust-disp-driver').innerText = selectedVehicle.driver;
    document.getElementById('cust-disp-car').innerText = selectedVehicle.model + ' — ' + selectedVehicle.plate;
    showToast('Your driver ' + selectedVehicle.driver + ' is coming!');
    document.getElementById('cust-dispatch-banner').scrollIntoView({{ behavior:'smooth', block:'nearest' }});
}}

function pingStandby() {{ showToast('Calling more drivers near you!'); }}

// ===== DRIVER SYSTEM =====
let isDriverOnline = true;
let driverEarnings = 1840;
let driverTrips = 6;
let driverCountdown = 22;
let currentTrip = null;

const sampleRiders = [
    {{ name:'Aarav Mehta', pickup:'Barakhamba Road, Connaught Place', drop:'Cyber City / Cyber Hub, DLF Gurugram', fare:320, dist:'19.4 km — 35 mins' }},
    {{ name:'Pooja Sharma', pickup:'Noida Sector 18 (Atta Market / Mall of India)', drop:'Indira Gandhi International Airport (DEL T3)', fare:460, dist:'28.5 km — 48 mins' }},
    {{ name:'Rohan Kapoor', pickup:'Hauz Khas Social, South Delhi', drop:'Saket District Centre, South Delhi', fare:145, dist:'4.8 km — 12 mins' }},
    {{ name:'Ananya Verma', pickup:'Anand Vihar ISBT, East Delhi', drop:'New Delhi Railway Station (Paharganj)', fare:210, dist:'11.2 km — 24 mins' }},
    {{ name:'Kunal Singhal', pickup:'Ambience Mall, Gurugram', drop:'Dwarka Sector 21, South West Delhi', fare:290, dist:'16.1 km — 28 mins' }},
    {{ name:'Meera Kapoor', pickup:'Rohini Sector 18 / West Delhi Hub', drop:'Connaught Place', fare:245, dist:'14.0 km — 27 mins' }}
];

function toggleDriverOnline() {{
    isDriverOnline = !isDriverOnline;
    const btn = document.getElementById('driver-toggle-online');
    const txt = document.getElementById('driver-status-text');
    const card = document.getElementById('driver-incoming-card');
    if (isDriverOnline) {{
        btn.style.background = '#10B981'; txt.innerText = 'I Am Ready';
        card.style.display = 'block';
        showToast('You are online! You will get ride requests now.');
        loadNextRideRequest();
    }} else {{
        btn.style.background = '#475569'; txt.innerText = 'Taking a Break';
        card.style.display = 'none';
        showToast('You are taking a break. No rides for now.');
    }}
}}

function loadNextRideRequest() {{
    if (!isDriverOnline) return;
    currentTrip = sampleRiders[Math.floor(Math.random() * sampleRiders.length)];
    document.getElementById('driver-req-rider').innerText = currentTrip.name;
    document.getElementById('driver-req-pickup').innerText = currentTrip.pickup;
    document.getElementById('driver-req-drop').innerText = currentTrip.drop;
    document.getElementById('driver-req-fare').innerText = 'Rs. ' + currentTrip.fare;
    document.getElementById('driver-req-dist').innerText = currentTrip.dist;
    driverCountdown = 25;
    document.getElementById('driver-timer-val').innerText = driverCountdown + 's';
}}

setInterval(() => {{
    if (isDriverOnline && currentTrip && document.getElementById('driver-incoming-card').style.display !== 'none') {{
        driverCountdown--;
        if (driverCountdown <= 0) loadNextRideRequest();
        else document.getElementById('driver-timer-val').innerText = driverCountdown + 's';
    }}
}}, 1000);

function acceptDriverRide() {{
    if (!currentTrip) return;
    document.getElementById('driver-incoming-card').style.display = 'none';
    const box = document.getElementById('driver-active-trip');
    box.style.display = 'block';
    document.getElementById('driver-act-rider').innerText = 'Rider: ' + currentTrip.name;
    document.getElementById('driver-act-fare').innerText = 'Rs. ' + currentTrip.fare;
    document.getElementById('driver-act-route').innerText = currentTrip.pickup + ' to ' + currentTrip.drop;
    showToast('Ride accepted! Go pick up ' + currentTrip.name);
    box.scrollIntoView({{ behavior:'smooth', block:'nearest' }});
}}

function passDriverRide() {{ showToast('Skipped. Getting next ride...'); loadNextRideRequest(); }}

function completeDriverTrip() {{
    if (!currentTrip) return;
    driverEarnings += currentTrip.fare;
    driverTrips += 1;
    document.getElementById('driver-wallet-val').innerText = 'Rs. ' + driverEarnings.toLocaleString();
    document.getElementById('driver-trips-val').innerText = driverTrips + ' Trips';
    document.getElementById('driver-active-trip').style.display = 'none';
    document.getElementById('driver-incoming-card').style.display = 'block';
    showToast('Ride done! Rs. ' + currentTrip.fare + ' earned!');
    loadNextRideRequest();
}}

function cancelDriverTrip() {{
    document.getElementById('driver-active-trip').style.display = 'none';
    document.getElementById('driver-incoming-card').style.display = 'block';
    showToast('Ride cancelled. Getting next request.');
    loadNextRideRequest();
}}

// ===== DEMAND RADAR =====
function refreshDriverDemand() {{
    const container = document.getElementById('driver-hotspots-container');
    container.innerHTML = '<div style="color:{text_sub};padding:14px;">Finding busy areas...</div>';
    fetch(API_BASE + '/api/driver/demand-map')
        .then(r => r.json())
        .then(data => {{
            if (data && data.zones) {{
                container.innerHTML = '';
                data.zones.forEach(z => {{
                    const bc = z.status === 'high' ? 'badge-high' : z.status === 'moderate' ? 'badge-mod' : 'badge-low';
                    const card = document.createElement('div');
                    card.className = 'hotspot-card ' + z.status;
                    card.innerHTML = `
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:9px;">
                            <div style="font-weight:800;font-size:1.0rem;">${{z.zone}}</div>
                            <span class="${{bc}}">${{z.status.toUpperCase()}} DEMAND</span>
                        </div>
                        <div style="font-size:0.84rem;color:{text_sub};margin-bottom:12px;">${{z.hotspot_advice}}</div>
                        <div style="display:flex;justify-content:space-between;padding-top:9px;border-top:1px solid {border_hex};font-size:0.83rem;">
                            <div>Riders waiting: <strong style="color:#38BDF8;">${{z.active_requests}}</strong></div>
                            <div>You can earn: <strong style="color:#10B981;">${{z.avg_earnings_per_hr}}</strong></div>
                        </div>
                    `;
                    container.appendChild(card);
                }});
            }}
        }})
        .catch(() => {{
            container.innerHTML = '<div style="color:#EF4444;padding:14px;">Could not load data. Please restart the app.</div>';
        }});
}}

// ===== HOUR PLAN FOR DRIVERS =====
const hourPlans = {{
    morning: [
        {{ rank:'#1 Best Zone', zone:'Barakhamba Road / Connaught Place', advice:'Office workers rushing to work. Very high demand from metro exits and bus stops.', earn:'Rs. 580 / hour' }},
        {{ rank:'#2 Strong Zone', zone:'Kashmere Gate Bus & Metro Terminal', advice:'Early buses arriving from UP/Haryana. Workers heading to central Delhi.', earn:'Rs. 520 / hour' }},
        {{ rank:'#3 Good Zone', zone:'Cyber City / DLF Gurugram', advice:'Tech office entry time. Workers coming from Gurgaon housing.', earn:'Rs. 490 / hour' }},
        {{ rank:'Avoid Now', zone:'Rohini & Pitampura', advice:'Too many cabs here, fewer rides. Better to position closer to central Delhi.', earn:'Rs. 240 / hour' }}
    ],
    day: [
        {{ rank:'#1 Best Zone', zone:'Delhi Airport (IGI T3 & Aerocity)', advice:'Non-stop flight arrivals all day. High chance of long and profitable trips.', earn:'Rs. 640 / hour' }},
        {{ rank:'#2 Strong Zone', zone:'Saket Mall & Hauz Khas', advice:'Shoppers, college students, and restaurant visitors. Steady short trips.', earn:'Rs. 420 / hour' }},
        {{ rank:'#3 Good Zone', zone:'Nehru Place IT Hub', advice:'Lunch-hour office trips and meetings in South Delhi.', earn:'Rs. 390 / hour' }},
        {{ rank:'Moderate Zone', zone:'Noida Sector 18 / Mall of India', advice:'Mall visitors and IT workers. Good mix of local and cross-city rides.', earn:'Rs. 380 / hour' }}
    ],
    evening: [
        {{ rank:'#1 Best Zone', zone:'Cyber City & DLF Gurugram', advice:'Thousands of office workers leaving at 6–8 PM. Highest surge in Delhi NCR.', earn:'Rs. 680 / hour' }},
        {{ rank:'#2 Best Zone', zone:'Delhi Airport (IGI Aerocity)', advice:'Evening international departures and arrivals. Long trips to South Delhi.', earn:'Rs. 640 / hour' }},
        {{ rank:'#3 Strong Zone', zone:'Ambience Mall & NH-48, Gurugram', advice:'Mall closing time creates sudden ride surge. Great for multi-trips.', earn:'Rs. 580 / hour' }},
        {{ rank:'#4 Good Zone', zone:'Rohini Sector 18 / West Delhi', advice:'Evening market shoppers and return commuters from west Delhi.', earn:'Rs. 420 / hour' }}
    ],
    night: [
        {{ rank:'#1 Best Zone', zone:'Delhi Airport (IGI T3)', advice:'Late-night international flights. Rides to Noida, Gurugram, and Greater Noida earn Rs.800+.', earn:'Rs. 720 / hour' }},
        {{ rank:'#2 Strong Zone', zone:'New Delhi Railway Station (Paharganj)', advice:'Overnight trains arriving. Passengers need rides to all Delhi NCR zones.', earn:'Rs. 540 / hour' }},
        {{ rank:'#3 Good Zone', zone:'Hauz Khas & Connaught Place', advice:'Late-night dining and parties. Short trips with 1.25x late-night surge.', earn:'Rs. 480 / hour' }},
        {{ rank:'Avoid Now', zone:'Noida Sector 62 / IT Hub', advice:'Offices are closed. Very few rides available in this area late night.', earn:'Rs. 180 / hour' }}
    ]
}};

function showHourPlan(slot) {{
    ['morning','day','evening','night'].forEach(s => {{
        document.getElementById('hpbtn-' + s).style.background = 'rgba(37,99,235,0.3)';
    }});
    document.getElementById('hpbtn-' + slot).style.background = 'rgba(37,99,235,0.7)';

    const container = document.getElementById('hour-plan-container');
    container.innerHTML = '';
    hourPlans[slot].forEach(z => {{
        const card = document.createElement('div');
        card.className = 'hour-zone-card';
        card.innerHTML = `
            <div class="hz-rank">${{z.rank}}</div>
            <div class="hz-zone"><i class="fa-solid fa-location-dot" style="color:#38BDF8;margin-right:6px;"></i>${{z.zone}}</div>
            <div class="hz-advice">${{z.advice}}</div>
            <div class="hz-earn"><i class="fa-solid fa-sack-dollar" style="margin-right:6px;"></i>${{z.earn}}</div>
        `;
        container.appendChild(card);
    }});
}}

// ===== TOAST =====
function showToast(msg) {{
    const t = document.getElementById('toast');
    document.getElementById('toast-text').innerText = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3500);
}}

// ===== INIT =====
window.addEventListener('load', () => {{
    populateLocations();
    onTripChange();
    fetchAllSlotForecast();
    loadNextRideRequest();
    showHourPlan('morning');
}});
setTimeout(() => {{
    populateLocations();
    onTripChange();
    fetchAllSlotForecast();
    loadNextRideRequest();
}}, 400);
</script>
</body>
</html>
"""

components.html(html_application, height=1050, scrolling=True)
