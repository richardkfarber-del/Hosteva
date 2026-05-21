import React, { useState } from 'react';

const PricingPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubscribe = async (tier) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/subscriptions/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tier }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      if (data.checkout_url) {
        window.location.assign(data.checkout_url);
      } else {
        setError('Failed to initiate checkout.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pricing-page">
      <h1>Upgrade to Premium</h1>
      {error && <p className="error">{error}</p>}
      <div className="pricing-tiers">
        <div className="tier">
          <h2>Basic</h2>
          <p>$10/month</p>
          <button disabled={loading} onClick={() => handleSubscribe('basic')}>
            {loading ? 'Processing...' : 'Subscribe to Basic'}
          </button>
        </div>
        <div className="tier">
          <h2>Pro</h2>
          <p>$20/month</p>
          <button disabled={loading} onClick={() => handleSubscribe('pro')}>
            {loading ? 'Processing...' : 'Subscribe to Pro'}
          </button>
        </div>
        <div className="tier">
          <h2>Premium</h2>
          <p>$30/month</p>
          <button disabled={loading} onClick={() => handleSubscribe('premium')}>
            {loading ? 'Processing...' : 'Subscribe to Premium'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
