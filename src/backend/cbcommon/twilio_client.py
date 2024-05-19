from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class TwilioClientException(Exception):
    pass


class TwilioClient:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def send_sms(self, recipient, body):

        if recipient == settings.TWILIO_FROM_NUMBER:
            print('Fake sending SMS to {}: \n{}'.format(recipient, body))
            return

        print('Sending SMS to {}: \n{}'.format(recipient, body))
        try:
            self.client.messages.create(to=recipient, from_=settings.TWILIO_FROM_NUMBER, body=body)
        except TwilioRestException as exc:
            message = 'Sending to {} has failed'.format(recipient)
            raise TwilioClientException(message) from exc


twilio_client = TwilioClient()
