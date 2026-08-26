```python
# FILE: app/services/oauth_handlers.py
import os
import requests
from flask import request, jsonify, redirect, session, url_for

class OAuthHandler:
    OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
    OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI')
    OAUTH_AUTHORIZE_URL = os.getenv('OAUTH_AUTHORIZE_URL')
    OAUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')
    OAUTH_USERINFO_URL = os.getenv('OAUTH_USERINFO_URL')

    @staticmethod
    def authorize():
        """Redirects the user to the OAuth provider for authorization."""
        params = {
            'response_type': 'code',
            'client_id': OAuthHandler.OAUTH_CLIENT_ID,
            'redirect_uri': OAuthHandler.OAUTH_REDIRECT_URI,
            'scope': 'profile email',
            'state': session['oauth_state']
        }
        return redirect(f"{OAuthHandler.OAUTH_AUTHORIZE_URL}?{urlencode(params)}")

    @staticmethod
    def callback():
        """Handles the callback from the OAuth provider."""
        if 'code' in request.args:
            code = request.args.get('code')
            params = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': OAuthHandler.OAUTH_REDIRECT_URI,
                'client_id': OAuthHandler.OAUTH_CLIENT_ID,
                'client_secret': OAuthHandler.OAUTH_CLIENT_SECRET
            }
            response = requests.post(OAuthHandler.OAUTH_TOKEN_URL, data=params)
            token_data = response.json()
            access_token = token_data.get('access_token')

            # Fetch user info
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            user_info_response = requests.get(OAuthHandler.OAUTH_USERINFO_URL, headers=headers)
            user_info = user_info_response.json()

            session['user_id'] = user_info.get('sub')
            session['user_email'] = user_info.get('email')
            return jsonify(user_info)
        return jsonify({'error': 'Authorization code not found'}), 400
```

```python
# FILE: app/services/listing_fetcher.py
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
```
