import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'Test_Room'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    
    async def receive(self, text_data):
        receive_dict = json.loads(text_data)
        message = receive_dict['message']   # this is a dictionary
        action = receive_dict['action']
        
        if(action=='new-offer' or action=='new-answer'):
            receiver_channel_name = receive_dict['message']['receiver_channel_name']
            
            receive_dict['message']['receiver_channel_name'] = self.channel_name
            
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': 'send.sdp',
                    'receive_dict': receive_dict
                }
            )
            
            return
        
        
        receive_dict['message']['receiver_channel_name'] = self.channel_name
        # Whenever a new peer connects to a consumer, its gonna have a unique channel name and we have to send to all the peers,
        # so that they know where to send the sdp offer 
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send.sdp',
                'receive_dict': receive_dict
            }
        )
        print(message)
        
    async def send_sdp(self, event):
        receive_dict = event['receive_dict']
        
        await self.send(text_data = json.dumps(receive_dict))
        print("success")
    
    async def disconnect(self):
        await self.channel_layer.froup_discard(
            self.room_group_name,
            self.channel_name
        )
        
        print("Disconnected")