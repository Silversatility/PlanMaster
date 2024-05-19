import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer


class CalendarConsumer(WebsocketConsumer):
    def connect(self):
        self.contractor_pk = self.scope['url_route']['kwargs']['contractor_pk']
        self.group_name = 'contractor_{}'.format(self.contractor_pk)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        pass

    def send_reload_calendar(self, event):
        message = 'reload_calendar'
        sender_user_id = event['sender_user_id']

        self.send(text_data=json.dumps({
            'message': message,
            'sender_user_id': sender_user_id
        }))

    @staticmethod
    def reload_calendar(contractor_id, user_id):
        """
        Reload the calendar of all ContractorAdmins under the same contractor
        """
        contractor_id = contractor_id
        sender_user_id = user_id
        channel_layer = get_channel_layer()
        group_name = 'contractor_{}'.format(contractor_id)

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_reload_calendar',
                'sender_user_id': sender_user_id
            }
        )
