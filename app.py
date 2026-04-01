import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from PIL import Image
import time
import textwrap

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="Jarvis: Smart Waste Intelligence", page_icon="🤖", layout="wide")

# Initialize Session State Variables
if "total_co2_saved_g" not in st.session_state:
    st.session_state.total_co2_saved_g = 0.0

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Online. How can I assist you with waste management or SWM 2026 compliance today?"}
    ]

if "last_scan_context" not in st.session_state:
    st.session_state.last_scan_context = ""

# Helper function
def clean_text(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace("</div>", "").replace("<div>", "").replace("<br/>", "").replace("<br>", "")

# Custom CSS for refined Jarvis aesthetic
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');

/* Main application styling */
.stApp {
    background-color: #0e1117 !important;
    font-family: 'JetBrains Mono', monospace;
    color: #ffffff !important;
}

/* Explicitly target text elements */
h1, h2, h3, h4, p, label, .dimmed-text, .section-title, .metric-title, .metric-category, .metric-directive, .metric-confidence, .treasure-title, .treasure-tip, .stMarkdown, [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDeltaIcon-Up"] > svg {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Typography & Visual Hierarchy */
h1 {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    letter-spacing: 2px !important;
    margin-bottom: 2rem !important;
    color: #ffffff !important;
}

.dimmed-text {
    font-size: 1rem;
    color: #888888 !important;
    margin-bottom: 2.5rem !important;
    display: block;
}

.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 1.5rem !important;
    color: #ffffff;
}

[data-testid="stMetricValue"] {
    color: #39ff14 !important;
    font-size: 3rem !important;
}

/* Inputs / Glassmorphism */
[data-testid="stFileUploader"], [data-testid="stCameraInput"] {
    background: linear-gradient(135deg, #1a1c24 0%, #0e1117 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

[data-testid="stFileUploader"] section {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stFileUploader"] svg {
    width: 32px !important;
    height: 32px !important;
    opacity: 0.8;
}

/* Sidebar Refinements */
section[data-testid="stSidebar"] {
    background-color: #0e1117 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] {
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Chat Glassmorphism Support */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 10px 15px !important;
    margin-bottom: 10px !important;
    backdrop-filter: blur(10px) !important;
    color: #dddddd !important;
}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
    font-size: 0.85rem !important;
}

/* Glassmorphism metric cards with fade-in animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.metric-card {
    background: rgba(26, 28, 36, 0.4);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    color: #ffffff;
    transition: all 0.3s ease;
    animation: fadeIn 0.6s ease-out forwards;
}

/* Card Top Borders */
.card-wet, .card-compost { border-top: 2px solid #39ff14; }
.card-dry, .card-recycle { border-top: 2px solid #00d1ff; }
.card-sanitary { border-top: 2px solid #ff003c; }
.card-hazardous, .card-ewaste { border-top: 2px solid #ffae00; }
.card-landfill { border-top: 2px solid #888888; }

.metric-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 4px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #ffffff;
}
.metric-category {
    font-size: 0.85rem;
    color: #00d1ff;
    margin-bottom: 15px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}
.card-wet .metric-category, .card-compost .metric-category { color: #39ff14; }
.card-sanitary .metric-category { color: #ff003c; }
.card-hazardous .metric-category, .card-ewaste .metric-category { color: #ffae00; }
.card-landfill .metric-category { color: #888888; }

.metric-confidence {
    font-size: 0.8rem;
    font-style: italic;
    color: #888888;
    margin-top: 10px;
}

/* Jarvis HUD Panel Logic (Directive & Treasure Block) */
.metric-directive, .treasure-block {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 15px;
    border-radius: 8px;
    backdrop-filter: blur(5px);
    margin-bottom: 10px;
}
.metric-directive {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #dddddd;
}
.treasure-title {
    font-size: 0.95rem;
    color: #00d1ff;
    margin-bottom: 8px;
    font-weight: 700;
}
.treasure-tip {
    font-size: 0.85rem;
    color: #dddddd;
    line-height: 1.5;
}

/* Breathing System Status dot */
@keyframes breathe {
    0% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 5px #00d1ff; }
    50% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 12px #00d1ff; }
    100% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 5px #00d1ff; }
}

.system-status {
    position: fixed;
    top: 60px;
    right: 30px;
    z-index: 999;
    font-size: 0.75rem;
    color: #888888;
    display: flex;
    align-items: center;
    background: rgba(14, 17, 23, 0.8);
    backdrop-filter: blur(5px);
    padding: 6px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.blink-dot {
    width: 6px;
    height: 6px;
    background-color: #00d1ff;
    border-radius: 50%;
    margin-right: 8px;
    animation: breathe 3s ease-in-out infinite;
}
</style>

<div class="system-status">
    <div class="blink-dot"></div>
    SYSTEM STATUS: ONLINE
</div>
""", unsafe_allow_html=True)

# Setup Gemini API key globally
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    st.warning("⚠️ Please provide a valid GEMINI_API_KEY in your .env file to use this application.")
    st.stop()

genai.configure(api_key=api_key)

# Application Header & Sidebar Control
st.sidebar.markdown("<div class='section-title' style='margin-bottom:0px !important;'>⚙️ Control Panel</div>", unsafe_allow_html=True)
app_mode = st.sidebar.radio("Operating Mode", ["Standard Mode", "Jarvis Pro (2026 Compliance)"], label_visibility="collapsed")
st.sidebar.markdown("<p style='font-size:0.85rem; color:#888;'>Toggle modes to unlock advanced regulatory analysis and circular economy frameworks.</p>", unsafe_allow_html=True)

st.sidebar.markdown("<br><div class='section-title' style='margin-bottom:10px !important;'>💬 Jarvis Assistant</div>", unsafe_allow_html=True)

# Render Sidebar Chat History
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.sidebar.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# Chat Input & Logic
if chat_prompt := st.sidebar.chat_input("Ask Jarvis..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": chat_prompt})
    with st.sidebar.chat_message("user", avatar="👤"):
        st.markdown(chat_prompt)
        
    # Prepare chat model
    chat_system_prompt = "You are Jarvis, a high-tech waste intelligence assistant. Provide expert advice on recycling, upcycling, and India's 2026 waste regulations. Be concise and use a helpful, tech-savvy tone."
    
    # Inject scan context if available
    context_prefix = ""
    if st.session_state.last_scan_context:
        context_prefix = f"[SYSTEM LOG - RECENT SCAN CONTEXT: {st.session_state.last_scan_context}]\n\n"
        
    chat_model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=chat_system_prompt)
    
    # Format history for Gemini
    gemini_history = []
    for m in st.session_state.messages[:-1]: # exclude the latest prompt
        if m["role"] == "system": continue
        role = "model" if m["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [m["content"]]})
        
    chat_session = chat_model.start_chat(history=gemini_history)
    
    # Generate Assistant Response
    with st.sidebar.chat_message("assistant", avatar="🤖"):
        with st.spinner("Processing..."):
            try:
                response = chat_session.send_message(context_prefix + chat_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                error_msg = "Connection to analytical databanks lost. Try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.title("🤖 Jarvis")

# Total Environmental Impact Metric
st.markdown("<div class='section-title'>🌍 Environmental Impact Dashboard</div>", unsafe_allow_html=True)
env_metric = st.empty()
env_metric.metric(label="Cumulative CO₂ Eq. Avoided", value=f"{st.session_state.total_co2_saved_g:.1f} g")
st.markdown("<br>", unsafe_allow_html=True)

if app_mode == "Standard Mode":
    st.markdown("<span class='dimmed-text'>Upload an image or take a picture of a bunch of trash, and I will strictly identify and base-sort it for you.</span>", unsafe_allow_html=True)
else:
    st.markdown("<span class='dimmed-text'>Upload an image or take a picture of a bunch of trash. I will thoroughly audit its compliance with 2026 SWM Rules and provide Circular Economy suggestions.</span>", unsafe_allow_html=True)

# Configure model and prompt based on mode
if app_mode == "Standard Mode":
    system_prompt = """You are Jarvis, a highly intelligent waste management AI. Analyze the image containing a bunch of trash and scan for all distinct waste items.
Return ONLY a JSON object with a single key "items", containing a list of every waste object detected.
For each item, provide exactly these keys: 'name', 'category', 'directive', 'confidence', 'material_type', and 'estimated_weight_g'.
Category must be exactly one of: ♻️ Recycle, 🍎 Compost, 🗑️ Landfill, 🔋 E-Waste. 
Directive must be a short, 1-sentence actionable instruction.
'material_type' must be one of: Plastic, Paper, Metal, Glass, or Other.
'estimated_weight_g' must be a reasonable integer estimating the item's weight in grams.

STRICT RULE: You are a data-only API. Do not include any HTML tags or markdown formatting in your JSON values. If I see a <div> or a <br> in your response, the system will fail. Output raw text only."""
else:
    system_prompt = """You are Jarvis, a highly intelligent Compliance Auditor for the 2026 India Solid Waste Management (SWM) Rules and a creative engineer. Analyze the image containing a bunch of trash and scan for all distinct waste items.
Return ONLY a JSON object with two keys:
1. 'compliance_score': An integer from 0-100 indicating how well the SWM segregation rules are followed. If the image shows mixed waste streams (e.g. food waste touching electronics or plastics), the score MUST be low.
2. 'items': A list of every waste object detected.

For each item in the list, provide exactly these keys: 'name', 'category', 'directive', 'confidence', 'treasure_tip', 'material_type', and 'estimated_weight_g'.
Category MUST be exactly one of the following four legal streams:
- 🟢 Wet Waste
- 🔵 Dry Waste
- 🔴 Sanitary Waste
- 🟡 Domestic Hazardous

Directive must be a short, 1-sentence actionable storage/disposal instruction based on the 2026 mandate.
For the 'treasure_tip', think like a creative engineer. If the item can be reused or upcycled, provide a clever, one-sentence idea for repurposing the object.
CRITICAL LOGIC RULE: If the item is "🔴 Sanitary Waste" or "🟡 Domestic Hazardous", the 'treasure_tip' MUST strictly be "NONE - Dispose of immediately for safety."
'material_type' must be one of: Plastic, Paper, Metal, Glass, or Other.
'estimated_weight_g' must be a reasonable integer estimating the item's weight in grams.

STRICT RULE: You are a data-only API. Do not include any HTML tags or markdown formatting in your JSON values. If I see a <div> or a <br> in your response, the system will fail. Output raw text only."""

# Initialize main vision model
vision_model = genai.GenerativeModel(
    "gemini-2.5-flash", 
    system_instruction=system_prompt,
    generation_config=genai.GenerationConfig(response_mime_type="application/json")
)

# User Inputs
st.markdown("<div class='section-title'>📷 Input Data</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

image_file = None
with col1:
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

with col2:
    camera_file = st.camera_input("Take Picture", label_visibility="collapsed")

if uploaded_file is not None:
    image_file = uploaded_file
elif camera_file is not None:
    image_file = camera_file

if image_file is not None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔍 Analysis Panel</div>", unsafe_allow_html=True)
    
    col_img, col_res = st.columns([1, 2])
    
    with col_img:
        image = Image.open(image_file)
        st.image(image, caption="Target Acquired", use_container_width=True)

    with col_res:
        scan_btn_text = "Start Basic Scan" if app_mode == "Standard Mode" else "Start Compliance Scan"
        if st.button(scan_btn_text, type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Smooth scanning visual
            for i in range(100):
                time.sleep(0.015)
                progress_bar.progress(i + 1)
                scan_msg = "Scanning target composition" if app_mode == "Standard Mode" else "Auditing target composition"
                status_text.markdown(f"<span style='color:#00d1ff;font-size:0.9rem;'>{scan_msg}... {i+1}%</span>", unsafe_allow_html=True)
            
            connect_msg = "Processing visual data with Gemini 2.5 Flash..." if app_mode == "Standard Mode" else "Connecting to SWM Database via Gemini 2.5 Flash..."
            status_text.markdown(f"<span style='color:#00d1ff;font-size:0.9rem;'>{connect_msg}</span>", unsafe_allow_html=True)
            
            try:
                # Call Gemini API
                response = vision_model.generate_content([image])
            except Exception as api_err:
                st.error(f"API Error - Failed to generate content: {api_err}")
                st.stop()
                
            progress_bar.empty()
            status_text.empty()
            
            # Parse JSON Response
            try:
                result = json.loads(response.text)
                items = result.get("items", [])
                
                # Update Chat Context Memory
                if items:
                    context_memory = [{"name": i.get("name"), "category": i.get("category"), "material": i.get("material_type"), "treasure_tip": i.get("treasure_tip")} for i in items]
                    st.session_state.last_scan_context = json.dumps(context_memory)
                
                # Render Pro specific blocks
                if app_mode == "Jarvis Pro (2026 Compliance)":
                    compliance_score = result.get("compliance_score", 0)
                    st.markdown("<div class='section-title'>📋 Jarvis Compliance Audit</div>", unsafe_allow_html=True)
                    st.progress(int(compliance_score))
                    st.markdown(f"**Compliance Score: {compliance_score}/100**")
                    
                    if compliance_score < 70:
                        st.error("🚨 SWM Rules Violation Warning: Improper waste segregation detected.")
                    else:
                        st.success("✅ Solid Waste Management compliance looks good.")
                    st.markdown("<br>", unsafe_allow_html=True)
                
                if not items:
                    st.warning("No distinct waste items found in the image.")
                else:
                    success_msg = "Scan complete." if app_mode == "Standard Mode" else "Audit complete."
                    st.success(f"{success_msg} {len(items)} items identified.")
                    
                    session_co2_savings = 0.0
                    
                    # Responsive grid formulation
                    cols_per_row = 2
                    for i in range(0, len(items), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, col_obj in enumerate(cols):
                            if i + j < len(items):
                                item = items[i + j]
                                item_name = clean_text(item.get("name", "Unknown Item"))
                                category = clean_text(item.get("category", "Unknown"))
                                directive = clean_text(item.get("directive", "No directive provided."))
                                confidence = clean_text(item.get("confidence", "N/A"))
                                material_type = clean_text(item.get("material_type", "Other"))
                                
                                try:
                                    weight_g = float(item.get("estimated_weight_g", 0))
                                except:
                                    weight_g = 0
                                    
                                # CO2 Calculations
                                co2_ratio = 0.0
                                if material_type == "Plastic":
                                    co2_ratio = 1.5
                                elif material_type == "Paper":
                                    co2_ratio = 0.9
                                elif material_type == "Metal":
                                    co2_ratio = 4.0
                                elif material_type == "Glass":
                                    co2_ratio = 0.3
                                    
                                co2_saved = weight_g * co2_ratio
                                
                                # Evaluate CSS class and logic branching
                                if app_mode == "Standard Mode":
                                    card_class = "card-landfill"
                                    if "Recycle" in category:
                                        card_class = "card-recycle"
                                        session_co2_savings += co2_saved
                                    elif "Compost" in category:
                                        card_class = "card-compost"
                                    elif "E-Waste" in category:
                                        card_class = "card-ewaste"
                                    else:
                                        card_class = "card-landfill"
                                        
                                    treasure_html = ""
                                else:
                                    # Jarvis Pro Mode
                                    card_class = "card-wet" # default
                                    if "Wet Waste" in category or "🟢" in category:
                                        card_class = "card-wet"
                                    elif "Dry Waste" in category or "🔵" in category:
                                        card_class = "card-dry"
                                        session_co2_savings += co2_saved
                                    elif "Sanitary Waste" in category or "🔴" in category:
                                        card_class = "card-sanitary"
                                    elif "Domestic" in category or "Hazardous" in category or "🟡" in category:
                                        card_class = "card-hazardous"

                                    treasure_tip = clean_text(item.get("treasure_tip", "No upcycling tip available."))
                                    treasure_html = f'''<div class="treasure-block"><div class="treasure-title">💡 Jarvis Suggests:</div><div class="treasure-tip">{treasure_tip}</div></div>'''

                                # Construct weight/material title string
                                weight_info = f"<span style='font-size:0.8rem; color:#888; font-weight:normal;'>({weight_g}g {clean_text(material_type)})</span>"
                                co2_info = f"<span style='color:#00d1ff; font-weight:bold;'>CO₂ Saved: {co2_saved:.1f}g</span>" if ("Recycle" in category or "Dry" in category) else ""

                                # Single-block rendering with NO empty newlines!
                                card_html = f'''<div class="metric-card {card_class}"><div class="metric-title">{item_name} {weight_info}</div><div class="metric-category"><span>{category}</span>{co2_info}</div><div class="metric-directive">{directive}</div><div class="metric-confidence">Confidence: {confidence}</div>{treasure_html}</div>'''
                                
                                col_obj.markdown(card_html, unsafe_allow_html=True)
                                
                    # Update global CO2 cumulative score and push securely to UI element dynamically
                    st.session_state.total_co2_saved_g += session_co2_savings
                    env_metric.metric(label="Cumulative CO₂ Eq. Avoided", value=f"{st.session_state.total_co2_saved_g:.1f} g", delta=f"+{session_co2_savings:.1f} g this scan")
                                
            except json.JSONDecodeError:
                st.error("Failed to parse the response from the model. Please try again.")
                st.write("Raw Response:", response.text)
            except Exception as e:
                st.error(f"An unexpected error occurred during parsing: {e}")
