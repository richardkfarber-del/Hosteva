class StripeAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def create_charge(self, amount, currency, source):
        # Implement charge creation logic here
        pass

    def get_customer(self, customer_id):
        # Implement customer retrieval logic here
        pass