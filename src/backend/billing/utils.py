import stripe

from django.conf import settings


# TODO: this file was created to explain how stripe works
# TODO: delete it before the PR is merged
def create_stripe_plans():
    """
    Before you can charge clients, you must programmatically create
    product that represents the service and plan stripe objects.
    Since it has to be done only once for one stripe account, we can
    store these objects in django settings by their ids.
    """
    stripe.api_key = settings.STRIPE_SECRET_API_KEY

    product = stripe.Product.create(
        name='Crew Boss',
        type='service',
    )
    contractor_m = stripe.Plan.create(
        product=product.id,
        nickname='Crew Boss Contractor Monthly',
        interval='month',
        currency='usd',
        amount=1999,
    )
    contractor_a = stripe.Plan.create(
        product=product.id,
        nickname='Crew Boss Contractor Annual',
        interval='year',
        currency='usd',
        amount=9900,
    )
    builder_m = stripe.Plan.create(
        product=product.id,
        nickname='Crew Boss Builder Monthly',
        interval='month',
        currency='usd',
        amount=2999,
    )
    builder_a = stripe.Plan.create(
        product=product.id,
        nickname='Crew Boss Builder Annual',
        interval='year',
        currency='usd',
        amount=9900,
    )
    # enterprise_m = stripe.Plan.create(
    #     product=product.id,
    #     nickname='Crew Boss Enterprise Monthly',
    #     interval='month',
    #     currency='usd',
    #     amount=30000,
    # )
    # enterprise_a = stripe.Plan.create(
    #     product=product.id,
    #     nickname='Crew Boss Enterprise Annual',
    #     interval='year',
    #     currency='usd',
    #     amount=300000,
    # )
