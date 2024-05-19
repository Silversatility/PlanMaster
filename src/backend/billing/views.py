import stripe

from datetime import datetime, timedelta

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import User


stripe.api_key = settings.STRIPE_SECRET_API_KEY


class StripeCustomerCreateView(APIView):
    """
    After we collect user's payment information using Stripe Checkout or Stripe Element on
    frontend we have to make a request to Stripe to create a Stripe Customer object.
    It is not explicitly mentioned in the Stripe documentation, but customer's source can be
    not source object id only, but card token as well.
    """

    def post(self, request):
        user = request.data.get('user', None)
        source = request.data.get('source', None)

        if not user or not source:
            data = {"error": "User and/or source parameters were not provided."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=user)
        customer = stripe.Customer.create(
            email=user.email,
            source=source,
        )
        user.stripe_customer = customer.id
        user.save()

        return Response(status=status.HTTP_200_OK)


class SubscribeCustomerView(APIView):
    """
    Every client who submitted payment information can be subscribed to a plan and charged.
    """

    def post(self, request):
        user = request.data.get('user', None)
        plan = request.data.get('plan', None)

        if not user or not plan:
            data = {"error": "User and/or plan parameters were not provided."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=user)

        subscription = stripe.Subscription.create(
            customer=user.stripe_customer,
            items=[{'plan': settings.STRIPE_PLANS[plan]}]
        )

        if 'annual' in plan:
            expiry_date = datetime.now() + timedelta(days=365)
        elif 'monthly' in plan:
            expiry_date = datetime.now() + timedelta(days=30)

        user.stripe_subscription = subscription.id
        user.active_plan = plan
        user.expiry_date = expiry_date
        user.save()

        return Response(status=status.HTTP_200_OK)


class CancelSubscriptionView(APIView):
    def post(self, request):
        user = request.data.get('user', None)

        if not user:
            data = {"error": "User parameter was not provided."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=user)
        sub = stripe.Subscription.retrieve(user.stripe_subscription)
        sub.delete()
        user.stripe_subscription = None
        user.save()

        return Response(status=status.HTTP_200_OK)


class ChargeFailedView(APIView):
    """
    View for Stripe's charge.failed event. It receives a request after Stripe cant charge a client.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            stripe.Webhook.construct_event(
                request.body, request.META['HTTP_STRIPE_SIGNATURE'], settings.STRIPE_CHARGE_FAILED_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        stripe_customer = request.data['data']['object']['customer']

        if stripe_customer:
            user = User.objects.filter(stripe_customer=stripe_customer).first()

            if user:
                user.has_active_subscription = False
                user.save()

        return Response()


class ChargeSucceededView(APIView):
    """
    View for Stripe's charge.succeed event. It receives a request after Stripe successfully charged a client.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            stripe.Webhook.construct_event(
                request.body, request.META['HTTP_STRIPE_SIGNATURE'], settings.STRIPE_CHARGE_SUCCEEDED_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        stripe_customer = request.data['data']['object']['customer']

        if stripe_customer:
            user = User.objects.filter(stripe_customer=stripe_customer).first()

            if user and not user.has_active_subscription:
                user.has_active_subscription = True

            subscription = stripe.Subscription.retrieve(user.stripe_subscription)
            user.expiry_date = datetime.fromtimestamp(subscription.current_period_end)
            user.save()

        return Response()


class ApplyPromoCodeView(APIView):
    def post(self, request):
        user = request.data.get('user', None)
        code = request.data.get('code', None)

        if not code or not user:
            data = {"error": "User and/or plan parameters were not provided."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=user)

        try:
            subscription = stripe.Subscription.retrieve(user.stripe_subscription)
            subscription.coupon = code
            subscription.save()
        except stripe.error.InvalidRequestError:
            data = {"error": "No such promo code: {}".format(code)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
