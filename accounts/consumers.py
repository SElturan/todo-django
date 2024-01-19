# всем остальным пользователям приходит уведомление с помощью сокетов о том, что создан новый юзер.
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "test"
        self.room_group_name = "test_group"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print("connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnected")
 
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)
   
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]
        print(message)
      
        await self.send(text_data=json.dumps({"message": message}))