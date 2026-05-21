import pytest
from app.db_models import User, Subscription

def test_subscription_model():
    sub = Subscription(stripe_customer_id='cus_123', status='active', plan_details='premium')
    assert sub.stripe_customer_id == 'cus_123'
    assert sub.status == 'active'
    assert sub.plan_details == 'premium'
