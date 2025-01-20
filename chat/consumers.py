import json
from channels.generic.websocket import AsyncWebsocketConsumer
import requests
import logging
import aiohttp  

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connected!")  # 연결 확인용 로그

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")  # 연결 해제 로그
        pass

    async def _is_valid_message(self, message):
        """메시지 유효성 검사"""
        if len(message) > 1000:  # 메시지 최대 길이 제한
            return False
        return True
        # 추가적인 검증 로직 구현
        # 여기에 추가적인 검증 로직 구현 가능
        # 예: 금지어 필터링, 최대 길이 제한 등    

    async def receive(self, text_data):
        try:
            # 클라이언트로부터 메시지 수신
            print(f"Received message: {text_data}")  # 수신 메시지 로그
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            user_id = text_data_json.get('user_id', '')

            # 메시지 적합성 검사 (예: 길이, 내용 등)
            if not await self._is_valid_message(message):
                await self.send_error("부적절한 메시지 입니다.")
                return
            
             # LLM API 서버로 HTTP 요청 (비동기로 수정)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        'http://localhost:8001/api/chat/',
                        json={
                            'message': message,
                            'user_id': user_id,
                            'response_type': 'text',
                            'prescription': 'No'
                        }
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            # 웹소켓으로 결과 전송
                            await self.send(text_data=json.dumps({
                                'type': 'chat.message',
                                'status': 'success',
                                'message': result.get('message', ''),
                                'user_id': user_id
                            }))
                        else:
                            await self.send_error("LLM 서버 처리 실패")

            except aiohttp.ClientError as e:
                logger.error(f"LLM API request failed: {str(e)}")
                await self.send_error("LLM 서버 연결 실패")

        except json.JSONDecodeError:
            await self.send_error("잘못된 메시지 형식")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send_error("서버 처리 중 오류 발생")

    async def send_error(self, message: str):
        await self.send(text_data=json.dumps({
            'type': 'chat.error',
            'status': 'error',
            'message': message
        }))

    
        