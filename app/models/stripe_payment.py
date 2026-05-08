from typing import Optional
from pydantic import BaseModel
import stripe
import os

stripe.api_key = os.environ.get('STRIPE_API_KEY', 'sk_test_mocked_for_testing')

class PaymentIntent(BaseModel):
    amount: int
    currency: str
    payment_method_types: list

    def create(self) -> dict:
        try:
            intent = stripe.PaymentIntent.create(
                amount=self.amount,
                currency=self.currency,
                payment_method_types=self.payment_method_types,
            )
            return intent
        except stripe.error.StripeError as e:
            return {'error': str(e)}

class PaymentGateway:
    def create_payment_intent(self, amount: int, currency: str, payment_method_types: list) -> dict:
        intent = PaymentIntent(amount=amount, currency=currency, payment_method_types=payment_method_types)
        return intent.create()
