import aiohttp

class MessageSender:
    def __init__(self, url: str):
        self.url = url  # URL을 직접 받도록 수정

    async def send_message(self, message: str):
        async with aiohttp.ClientSession() as session:
            payload = {"message": message}  # 메시지 데이터 (필요에 맞게 수정)
            async with session.post(self.url, json=payload) as response:
                if response.status == 200:
                    print("Message sent successfully!")
                else:
                    print(f"Failed to send message: {response.status}")
