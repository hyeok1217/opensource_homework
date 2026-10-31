import io
import urllib.request
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
from PIL import Image
import torch
from torchvision import models

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 가벼운 사전 학습 모델 로드 (MobileNet V3)
weights = models.MobileNet_V3_Small_Weights.DEFAULT
model = models.mobilenet_v3_small(weights=weights)
model.eval()
preprocess = weights.transforms()

# ImageNet 클래스(품종 포함) 텍스트 로드
url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
classes = [line.strip() for line in urllib.request.urlopen(url)]

@app.get("/")
def read_root(request: Request):
    # 에러가 나던 부분을 최신 버전에 맞게 수정한 코드입니다.
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    
    # 이미지 전처리 및 추론
    input_tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top_prob, top_catid = torch.topk(probabilities, 1)
        
    predicted_breed = classes[top_catid[0]]
    confidence = top_prob[0].item() * 100
    
    # MLOps 시나리오: 확신도가 50% 미만이면 오분류 가능성이 높아 재학습 파이프라인으로 보낸다고 가정
    needs_retraining = confidence < 50.0

    return {
        "breed": predicted_breed,
        "confidence": f"{confidence:.2f}%",
        "needs_retraining": needs_retraining
    }