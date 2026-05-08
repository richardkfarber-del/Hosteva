from flask import redirect, url_for
import stripe

@app.route('/host-dashboard')
def host_dashboard():
    try:
        # Check if user has active Hosteva Pro subscription
        customer_id = get_customer_id_from_session()
        subscription = stripe.Subscription.retrieve(customer_id)
        if subscription.status == 'active':
            return render_template('dashboard.html')
        else:
            return redirect(url_for('stripe_checkout'))
    except stripe.error.StripeError as e:
        return str(e), 500

def get_customer_id_from_session():
    # Implement logic to retrieve customer ID from session or database
    pass
