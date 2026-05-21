import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PricingPage from './PricingPage';

// Mock the fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ checkout_url: 'https://mock-stripe.com/checkout' }),
  })
);

describe('PricingPage', () => {
  let consoleErrorMock;

  beforeAll(() => {
    consoleErrorMock = jest.spyOn(console, 'error').mockImplementation((msg) => {
      if (msg && msg.message && msg.message.includes('Not implemented: navigation')) {
        return;
      }
    });
  });

  afterAll(() => {
    consoleErrorMock.mockRestore();
  });

  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders pricing tiers', () => {
    render(<PricingPage />);
    expect(screen.getByText('Basic')).toBeTruthy();
    expect(screen.getByText('Pro')).toBeTruthy();
    expect(screen.getByText('Premium')).toBeTruthy();
  });

  it('calls checkout endpoint when subscribe is clicked', async () => {
    render(<PricingPage />);
    const basicButton = screen.getByText('Subscribe to Basic');
    
    fireEvent.click(basicButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/subscriptions/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tier: 'basic' }),
      });
    });
  });
});
