import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connected!")  # 연결 확인용 로그

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")  # 연결 해제 로그
        pass

    async def receive(self, text_data):
        print(f"Received message: {text_data}")  # 수신 메시지 로그
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        response = {
            'message': message,
            'customer_state': '분석 결과',
            'probability': 0.95
        }

        await self.send(text_data=json.dumps(response))