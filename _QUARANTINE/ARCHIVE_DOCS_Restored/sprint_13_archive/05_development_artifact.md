# Iron Man
```json
{"name": "write_file", "arguments": {"filepath": "/home/rdogen/OpenClaw_Factory/projects/Hosteva/api/app/routers/host_dashboard.py", "content": "from fastapi import Depends, HTTPException, status\nfrom fastapi.responses import RedirectResponse\nimport stripe\nfrom app.dependencies import get_current_user, current_active_user\n\nasync def check_subscription(user: str = Depends(current_active_user)):\n    try:\n        subscription = stripe.Subscription.retrieve(\n            user.stripe_subscription_id,\n            api_key='your_stripe_api_key'\n        )\n        if subscription.status != 'active':\n            return False\n        return True\n    except stripe.error.StripeError as e:\n        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))\n\n@router.get(\"/host-dashboard\")\nasync def host_dashboard(user: str = Depends(current_active_user), is_subscribed: bool = Depends(check_subscription)):\n    if not is_subscribed:\n        return RedirectResponse(url='/subscription-page')\n    # Logic for the host dashboard route"}}
```

Tool Results:
Tool write_file executed:
Successfully wrote to /home/rdogen/OpenClaw_Factory/projects/Hosteva/api/app/routers/host_dashboard.py

# Wasp
```json
{
  "name": "write_file",
  "arguments": {
    "filepath": "/home/rdogen/OpenClaw_Factory/projects/Hosteva/frontend/src/components/ProtectedRoute.js",
    "content": "import React from 'react';\nimport { useEffect, useState } from 'react';\nimport { useNavigate } from 'react-router-dom';\n\nconst ProtectedRoute = ({ children }) => {\n  const navigate = useNavigate();\n  const [isSubscribed, setIsSubscribed] = useState(null);\n  const [isLoading, setIsLoading] = useState(true);\n  const [error, setError] = useState(false);\n\n  useEffect(() => {\n    const fetchSubscriptionStatus = async () => {\n      try {\n        // Assuming there's an API endpoint to check subscription status\n        const response = await fetch('/api/host-dashboard/check-subscription');\n        if (response.ok) {\n          setIsSubscribed(true);\n        } else {\n          navigate('/subscription-page');\n        }\n      } catch (err) {\n        setError(true);\n      } finally {\n        setIsLoading(false);\n      }\n    };\n\n    fetchSubscriptionStatus();\n  }, []);\n\n  if (isLoading) return <div>Loading...</div>;\n  if (error) return <div>Error: Unable to check subscription status.</div>;\n\n  return isSubscribed ? children : null;\n};\n\nexport default ProtectedRoute;"
  }
}
```

Tool Results:
Tool write_file executed:
Successfully wrote to /home/rdogen/OpenClaw_Factory/projects/Hosteva/frontend/src/components/ProtectedRoute.js

# Black Widow
```json
{
  "name": "write_file",
  "arguments": {
    "filepath": "/home/rdogen/OpenClaw_Factory/projects/Hosteva/tests/backend/test_host_dashboard.py",
    "content": "import pytest\nfrom fastapi.testclient import TestClient\nfrom app.main import app\nfrom unittest.mock import patch, MagicMock\n\n@pytest.fixture(scope='module')\ndef client():\n    with TestClient(app) as c:\n        yield c\n\n@patch('app.routers.host_dashboard.stripe.Subscription.retrieve')\ndef test_host_dashboard_subscribed(mock_retrieve):\n    mock_user = {'stripe_subscription_id': 'sub_1234567890'}\n    mock_retrieve.return_value = MagicMock(status='active')\n\n    client = TestClient(app)\n    response = client.get('/host-dashboard', headers={'Authorization': 'Bearer sub_1234567890'})\n    assert response.status_code == 200\n\n@patch('app.routers.host_dashboard.stripe.Subscription.retrieve')\ndef test_host_dashboard_unsubscribed(mock_retrieve):\n    mock_user = {'stripe_subscription_id': 'sub_1234567890'}\n    mock_retrieve.return_value = MagicMock(status='canceled')\n\n    client = TestClient(app)\n    response = client.get('/host-dashboard', headers={'Authorization': 'Bearer sub_1234567890'})\n    assert response.status_code == 302\n    assert response.headers['Location'] == '/subscription-page'\n\n@patch('app.routers.host_dashboard.stripe.Subscription.retrieve')\ndef test_host_dashboard_api_error(mock_retrieve):\n    mock_user = {'stripe_subscription_id': 'sub_1234567890'}\n    mock_retrieve.side_effect = stripe.error.StripeError('Stripe error message')\n\n    client = TestClient(app)\n    response = client.get('/host-dashboard', headers={'Authorization': 'Bearer sub_1234567890'})\n    assert response.status_code == 500\n    assert response.json() == {'detail': 'Stripe error message'}"
  }
}
```

Tool Results:
Tool write_file executed:
Successfully wrote to /home/rdogen/OpenClaw_Factory/projects/Hosteva/tests/backend/test_host_dashboard.py

