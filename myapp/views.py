from django.shortcuts import render
from django.http import JsonResponse, FileResponse
import os
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences  # 이 import만 사용
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from urllib.parse import unquote


def hello(request):
    return JsonResponse({"message" : "hello"})

def bye(request):
    return JsonResponse({"message" : "bye"})

def whoami(request):
    return JsonResponse({"name" : "ari"})

def greeting(request, input_string):
    return JsonResponse({"greeting" : 
f"{input_string} hello"})

def picture(request):
    image_path = os.path.join('media', '2.jpg')
    return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')

def video(request):
    return JsonResponse({
        "videos": [
            {
                "id": "ardxNUVTi2s",
                "title": "Video Title Here"
            }
            # 필요한 경우 더 많은 비디오 추가
        ]
    })
   
def video_page(request):
    return render(request, 'video.html')


@csrf_exempt
def machine(request, input_string):
    if request.method == 'GET':
        try:
            print(f"Received input: {input_string}")
            decoded_string = unquote(input_string)
            print(f"Decoded input: {decoded_string}")

            # 모델 파일 경로 설정
            model_path = os.path.join(settings.BASE_DIR, 'myapp', 'ml_models', 'best_model.h5')
            tokenizer_path = os.path.join(settings.BASE_DIR, 'myapp', 'ml_models', 'tokenizer.pickle')
            print(f"Model path: {model_path}")
            print(f"Tokenizer path: {tokenizer_path}")

            try:
                # 토크나이저 로드 시도
                print("토크나이저 로드 시작")
                with open(tokenizer_path, 'rb') as handle:
                    tokenizer = pickle.load(handle)
                print("토크나이저 로드 성공")

                # 모델 로드 시도
                print("모델 로드 시작")
                model = load_model(model_path)
                print("모델 로드 성공")

                # 텍스트 전처리 시도
                print("텍스트 전처리 시작")
                sequences = tokenizer.texts_to_sequences([decoded_string])
                print(f"시퀀스 변환 결과: {sequences}")
                padded = pad_sequences(sequences, maxlen=30)
                print(f"패딩 결과: {padded}")

                # 예측
                prediction = model.predict(padded)
                predicted_class = np.argmax(prediction[0])

                # 상태 매핑
                status_mapping = {0: "낮음", 1: "중간", 2: "높음"}
                
                result = {
                    "status": "success",
                    "input_text": decoded_string,
                    "customer_state": status_mapping[predicted_class],
                    "probability": float(prediction[0][predicted_class])
                }
                
                return JsonResponse(result)

            except Exception as specific_error:
                print(f"구체적인 에러 발생: {str(specific_error)}")
                print(f"에러 타입: {type(specific_error)}")
                return JsonResponse({
                    "status": "error",
                    "message": f"ML 처리 중 오류: {str(specific_error)}"
                }, status=400)

        except Exception as e:
            print(f"일반 에러 발생: {str(e)}")
            print(f"에러 타입: {type(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"처리 중 오류 발생: {str(e)}"
            }, status=400)


# Create your views here.
