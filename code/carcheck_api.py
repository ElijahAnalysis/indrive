





from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
from paddleocr import PaddleOCR
import cv2
import numpy as np
import re

from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from PIL import Image
import torch


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

@app.post('/analyze_image')
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
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
                "Responses must be polite, clear, and up to 20 words."
            )
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "image": img}
            ]
        }
    ]


    # build chat template
    text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    # process inputs (directly pass images to processor)
    inputs = processor(
        text=[text_prompt],
        images=[img],
        padding=True,
        return_tensors="pt"
    ).to(qwen2b.device)

    # generate output
    output_ids = qwen2b.generate(**inputs, max_new_tokens=40)
    output_text = processor.batch_decode(output_ids, skip_special_tokens=True)[0]

    


    #### FILTER MODEL RESPONSE WITH REGEX

    pattern = r"assistant\n(.*)"

    match = re.search(pattern, output_text, re.DOTALL)
    if match:
        response = match.group(1).strip()
    
    return response


































