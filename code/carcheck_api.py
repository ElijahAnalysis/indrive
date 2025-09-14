from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
from paddleocr import PaddleOCR
import cv2
import numpy as np
import re
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from PIL import Image
import torch
from typing import Dict, List, Any

#### YOLO SETUP
yolo11s_carcheck = YOLO(r"C:\Users\User\Desktop\Github\indrive\models\best.pt")

#### MODEL SETUP
qwen2b_id = "Qwen/Qwen2-VL-2B-Instruct"

# load model + processor
qwen2b = Qwen2VLForConditionalGeneration.from_pretrained(
    qwen2b_id,
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(qwen2b_id)
processor = AutoProcessor.from_pretrained(qwen2b_id)

#### API SETUP
app = FastAPI()

def analyze_with_yolo(img: np.ndarray) -> Dict[str, Any]:
    """
    Analyze image with YOLO and return detection results
    """
    results = yolo11s_carcheck(img, conf = 0.7)
    
    detections = []
    issues_found = False
    
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                # Get class name and confidence
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[class_id]
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detection_info = {
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                }
                detections.append(detection_info)
                
                # Check if this detection indicates an issue
                # Adjust these class names based on your YOLO model's classes
                issue_classes = [
                    'damage', 'scratch', 'dent', 'rust', 'broken_light', 
                    'dirty', 'crack', 'accident_damage', 'paint_damage'
                ]
                
                if class_name.lower() in issue_classes or confidence > 0.7:
                    issues_found = True
    
    return {
        "detections": detections,
        "issues_detected": issues_found,
        "total_detections": len(detections)
    }

@app.post('/analyze_image')
async def analyze_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    # Read and process image
    image_bytes = await file.read()
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    # VLM Analysis
    messages = [
        {
            "role": "system",
            "content": (
                "<image>\nYou are an InDrive car condition reviewer. "
                "Follow this decision order strictly: "
                "1) First, check if the image shows a car. "
                "   - If no car is present, respond: 'Not acceptable (not a car)'. "
                "2) If a car is present, evaluate its condition. "
                "   - If the car is perfectly clean and has no visible damage, respond positively "
                "     and end with 'Good for customers'. "
                "   - If the car is dirty, damaged, rusty, scratched, dented, or has broken lights, "
                "     respond: 'Not acceptable (reason)'. "
                "Responses must be polite, clear, and up to 25 words. Try explain key details of reason"
            )
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "image": img}
            ]
        }
    ]
    
    # Build chat template
    text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # Process inputs
    inputs = processor(
        text=[text_prompt],
        images=[img],
        padding=True,
        return_tensors="pt"
    ).to(qwen2b.device)
    
    # Generate VLM output
    output_ids = qwen2b.generate(**inputs, max_new_tokens=40)
    output_text = processor.batch_decode(output_ids, skip_special_tokens=True)[0]
    
    # Filter VLM response with regex
    pattern = r"assistant\n(.*)"
    vlm_response = "Error processing VLM response"
    
    match = re.search(pattern, output_text, re.DOTALL)
    if match:
        vlm_response = match.group(1).strip()
    
    # YOLO Analysis
    yolo_results = analyze_with_yolo(img)
    
    # Prepare response
    response = {
        "vlm_assessment": vlm_response,
        "analysis_summary": ""
    }
    
    # Determine if we should show YOLO results
    show_yolo = False
    
    # Show YOLO if VLM detected issues
    if "not acceptable" in vlm_response.lower() or yolo_results["issues_detected"]:
        show_yolo = True
        response["yolo_detections"] = yolo_results
        response["analysis_summary"] = f"Issues detected by {'both VLM and YOLO' if 'not acceptable' in vlm_response.lower() and yolo_results['issues_detected'] else 'VLM' if 'not acceptable' in vlm_response.lower() else 'YOLO'}"
    else:
        response["analysis_summary"] = "No issues detected - car appears acceptable"
    
    # Add detection details only when there are issues
    if show_yolo and yolo_results["detections"]:
        detected_issues = [det["class"] for det in yolo_results["detections"]]
        response["detected_issues"] = detected_issues
        response["issue_count"] = len(detected_issues)
    
    return response

@app.get('/health')
async def health_check():
    return {"status": "healthy", "models_loaded": True}

# Optional: Add endpoint to get just YOLO results for debugging
@app.post('/yolo_only')
async def yolo_analysis_only(file: UploadFile = File(...)):
    image_bytes = await file.read()
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    yolo_results = analyze_with_yolo(img)
    return yolo_results




































































