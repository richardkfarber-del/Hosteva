import requests
from app.models import db, Listing

class ListingFetcher:
    LISTINGS_API_URL = os.getenv('LISTINGS_API_URL')

    @staticmethod
    def fetch_listings():
        """Fetches listings from the external API and updates the local database."""
        try:
            response = requests.get(ListingFetcher.LISTINGS_API_URL)
            listings_data = response.json()

            for listing in listings_data:
                new_listing = Listing(
                    listing_id=listing['listing_id'],
                    title=listing['title'],
                    description=listing['description'],
                    price=listing['price'],
                    location=listing['location']
                )
                db.session.merge(new_listing)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error fetching listings: {e}")
            return False