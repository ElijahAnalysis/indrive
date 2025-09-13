import streamlit as st
import requests
from PIL import Image
import time
import base64

st.set_page_config(
    page_title="inDrive Car Inspector",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# inDrive brand colors and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }
    
    /* Header styling */
    .header-container {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 30px;
        margin: 20px auto 40px auto;
        max-width: 800px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .indrive-logo {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4CAF50;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    
    .header-subtitle {
        color: #666;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 0;
    }
    
    /* Main content container */
    .main-content {
        max-width: 1000px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Upload section */
    .upload-section {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .upload-area {
        border: 3px dashed #FF6B35;
        border-radius: 15px;
        padding: 60px 20px;
        text-align: center;
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(247, 147, 30, 0.05) 100%);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-area::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #FF6B35, #F7931E, #FF6B35);
        border-radius: 15px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .upload-area:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(255, 107, 53, 0.3);
    }
    
    .upload-area:hover::before {
        opacity: 0.1;
    }
    
    .upload-icon {
        font-size: 4rem;
        color: #FF6B35;
        margin-bottom: 20px;
        display: block;
    }
    
    .upload-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
    }
    
    .upload-subtext {
        color: #888;
        font-size: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B35, #F7931E) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px 40px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 10px 25px rgba(255, 107, 53, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-top: 30px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 35px rgba(255, 107, 53, 0.4) !important;
    }
    
    .stButton > button:disabled {
        background: linear-gradient(45deg, #ccc, #aaa) !important;
        transform: none !important;
        box-shadow: none !important;
        opacity: 0.6 !important;
    }
    
    /* Results section */
    .results-section {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .result-approved {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        box-shadow: 0 10px 25px rgba(76, 175, 80, 0.3);
        animation: slideIn 0.5s ease;
    }
    
    .result-rejected {
        background: linear-gradient(135deg, #F44336, #d32f2f);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        box-shadow: 0 10px 25px rgba(244, 67, 54, 0.3);
        animation: slideIn 0.5s ease;
    }
    
    .result-processing {
        background: linear-gradient(135deg, #2196F3, #1976D2);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        box-shadow: 0 10px 25px rgba(33, 150, 243, 0.3);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Loading animation */
    .loading-container {
        text-align: center;
        padding: 40px;
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(255, 107, 53, 0.3);
        border-top: 4px solid #FF6B35;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        color: #FF6B35;
        font-size: 1.2rem;
        font-weight: 600;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Image preview */
    .image-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        margin: 30px 0;
    }
    
    .image-container img {
        border-radius: 10px;
        width: 100%;
        height: auto;
        max-height: 400px;
        object-fit: contain;
    }
    
    /* Info cards */
    .info-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-top: 40px;
    }
    
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
    }
    
    .info-card-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
        display: block;
    }
    
    .info-card-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
    }
    
    .info-card-text {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Status indicator */
    .status-indicator {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        z-index: 1000;
    }
    
    .status-online {
        color: #4CAF50;
        font-weight: 600;
    }
    
    .status-offline {
        color: #F44336;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False
if 'result' not in st.session_state:
    st.session_state.result = None

# API base URL
base_url = "http://127.0.0.1:8000"

# Check server status
def check_server_status():
    try:
        response = requests.get(f"{base_url}/docs", timeout=3)
        return response.status_code == 200
    except:
        return False

server_online = check_server_status()

# Status indicator
status_class = "status-online" if server_online else "status-offline"
status_text = "🟢 Server Online" if server_online else "🔴 Server Offline"
st.markdown(f'<div class="status-indicator"><span class="{status_class}">{status_text}</span></div>', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div class="indrive-logo">inDrive</div>
    <div class="header-subtitle">AI-Powered Car Condition Inspector</div>
</div>
""", unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Upload Section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("""
<div class="upload-area">
    <span class="upload-icon">📸</span>
    <div class="upload-text">Upload Your Car Photo</div>
    <div class="upload-subtext">Drag & drop or click to select • PNG, JPG, JPEG supported</div>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "", 
    type=['png', 'jpg', 'jpeg'], 
    label_visibility="collapsed",
    key="car_image_uploader"
)

if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    
    # Display image preview
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Analyze button
if st.session_state.uploaded_file is not None and not st.session_state.analyzing:
    if st.button("🔍 ANALYZE VEHICLE CONDITION", disabled=not server_online):
        st.session_state.analyzing = True
        st.session_state.result = None
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Processing state
if st.session_state.analyzing:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    st.markdown("""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">Analyzing vehicle condition...</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Perform analysis
    try:
        st.session_state.uploaded_file.seek(0)
        files = {"file": st.session_state.uploaded_file}
        response = requests.post(f"{base_url}/analyze_image", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.result = result
        else:
            st.session_state.result = f"Server Error: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        st.session_state.result = "Connection Error: Unable to reach analysis server"
    except Exception as e:
        st.session_state.result = f"Analysis Error: {str(e)}"
    
    st.session_state.analyzing = False
    time.sleep(2)  # Show loading for a bit
    st.rerun()

# Results display
if st.session_state.result is not None:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    
    if "Good for customers" in str(st.session_state.result):
        st.markdown(f"""
        <div class="result-approved">
            ✅ VEHICLE APPROVED<br>
            <div style="font-size: 1rem; margin-top: 10px; opacity: 0.9;">{st.session_state.result}</div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        
    elif "Not acceptable" in str(st.session_state.result):
        st.markdown(f"""
        <div class="result-rejected">
            ❌ VEHICLE REJECTED<br>
            <div style="font-size: 1rem; margin-top: 10px; opacity: 0.9;">{st.session_state.result}</div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown(f"""
        <div class="result-processing">
            ⚠️ ANALYSIS COMPLETE<br>
            <div style="font-size: 1rem; margin-top: 10px; opacity: 0.9;">{st.session_state.result}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Reset button
    if st.button("📱 ANALYZE ANOTHER VEHICLE"):
        st.session_state.uploaded_file = None
        st.session_state.result = None
        st.session_state.analyzing = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Info Cards
st.markdown("""
<div class="info-cards">
    <div class="info-card">
        <span class="info-card-icon">🎯</span>
        <div class="info-card-title">AI-Powered Analysis</div>
        <div class="info-card-text">Advanced computer vision technology evaluates vehicle condition with precision</div>
    </div>
    <div class="info-card">
        <span class="info-card-icon">⚡</span>
        <div class="info-card-title">Instant Results</div>
        <div class="info-card-text">Get immediate feedback on vehicle condition and eligibility</div>
    </div>
    <div class="info-card">
        <span class="info-card-icon">🛡️</span>
        <div class="info-card-title">Quality Standards</div>
        <div class="info-card-text">Maintains inDrive's high standards for customer satisfaction</div>
    </div>
    <div class="info-card">
        <span class="info-card-icon">📱</span>
        <div class="info-card-title">Mobile Friendly</div>
        <div class="info-card-text">Works seamlessly on all devices for on-the-go inspections</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 60px; padding: 40px; color: rgba(255,255,255,0.7);">
    <div style="font-size: 0.9rem;">Powered by inDrive Quality Assurance • AI Vehicle Inspection System</div>
</div>
""", unsafe_allow_html=True)