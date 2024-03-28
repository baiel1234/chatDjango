import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'public_room'
        self.room_group_name = self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        json_text = json.loads(text_data)
        message = json_text["message"]
        sender = json_text.get("sender", "Anonymous") # Extract sender's name
        
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, 
            {
                "type": "chat_message", 
                "message": message,
                "sender": sender # Pass sender's name to chat_message handler
            }
        )

    def chat_message(self, event):
        message = event['message']
        sender = event['sender'] # Extract sender's name

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "message": message,
            "sender": sender # Include sender's name in the message
        }))