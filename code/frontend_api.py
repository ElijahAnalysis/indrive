import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Car Inspector", page_icon="🚗", layout="wide")

# Simple styling
st.markdown("""
<style>
.main { padding: 20px; }
.result-box { padding: 20px; border-radius: 10px; margin: 10px 0; }
.approved { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
.rejected { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
.detection-card { 
    background: white; 
    padding: 15px; 
    border-radius: 8px; 
    border: 1px solid #ddd; 
    margin: 10px 0; 
}
.bbox-box { background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 0.9em; }
footer {visibility: hidden;} /* remove footer */
.block-container {padding-bottom: 0px;} /* tighten bottom space */
.title-container {display: flex; align-items: center; gap: 10px;}
</style>
""", unsafe_allow_html=True)


def draw_bounding_boxes(image, detections):
    """Draw bounding boxes on image"""
    image_with_boxes = image.copy()
    draw = ImageDraw.Draw(image_with_boxes)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    img_width, img_height = image.size
    
    for detection in detections:
        class_name = detection.get('class', 'unknown')
        confidence = detection.get('confidence', 0)
        bbox = detection.get('bbox', [0, 0, 0, 0])
        
        # Convert coordinates
        x1, y1, x2, y2 = bbox
        if max(bbox) <= 1.0:  # normalized coordinates
            x1 = int(x1 * img_width)
            y1 = int(y1 * img_height)
            x2 = int(x2 * img_width)
            y2 = int(y2 * img_height)
        
        # Draw box
        draw.rectangle([x1, y1, x2, y2], outline='#FF6B35', width=3)
        
        # Draw label
        label = f"{class_name}: {int(confidence * 100)}%"
        
        if font:
            bbox_text = draw.textbbox((0, 0), label, font=font)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
        else:
            text_width = len(label) * 7
            text_height = 12
        
        label_y = max(0, y1 - text_height - 5)
        draw.rectangle([x1, label_y, x1 + text_width + 8, label_y + text_height + 4], fill='#FF6B35')
        draw.text((x1 + 4, label_y + 2), label, fill='white', font=font)
    
    return image_with_boxes


# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None

# Title (removed inspector gadget icon)
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("C:/Users/User/Desktop/Github/indrive/content/indriveicon.jpg", width=45)
with col2:
    st.title("inDrive Car Inspector 🚗")

# File upload
uploaded_file = st.file_uploader("Upload car image", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)

    if st.button("🔍 Analyze", type="primary"):
        with st.spinner("Analyzing..."):
            try:
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                
                response = requests.post("http://127.0.0.1:8000/analyze_image", files=files, timeout=60)
                
                if response.status_code == 200:
                    st.session_state.result = response.json()
                else:
                    st.error(f"HTTP Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Can't reach server at http://127.0.0.1:8000")
            except requests.exceptions.Timeout:
                st.error("Timeout Error: Server took too long to respond")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display results
    if st.session_state.result:
        result = st.session_state.result
        
        # Main result
        vlm_response = result.get('vlm_assessment', '')
        if "Good for customers" in vlm_response:
            st.markdown(f'<div class="result-box approved">✅ APPROVED: {vlm_response}</div>', unsafe_allow_html=True)
            st.balloons()
        elif "Not acceptable" in vlm_response:
            st.markdown(f'<div class="result-box rejected">❌ REJECTED: {vlm_response}</div>', unsafe_allow_html=True)
        else:
            st.info(vlm_response)
        
        # Always show YOLO detections if available
        if 'yolo_detections' in result:
            detections = result['yolo_detections'].get('detections', [])
            if detections:
                annotated_image = draw_bounding_boxes(image, detections)
                st.image(annotated_image, caption="Detected Issues", use_column_width=True)
            else:
                st.image(image, caption="No issues detected", use_column_width=True)



