from app.api.routes.properties import PropertiesResponseOut
import json

data = {
    "properties": [
        {
            "id": "prop_9a8b7c6d",
            "address": {
                "full_string": "123 Ocean Drive, Unit 4B, Miami Beach, FL 33139",
                "zip_code": "33139"
            },
            "property_type": "Condo",
            "compliance_progress": {
                "completed": 4,
                "total": 7,
                "percentage": 57.1
            },
            "status_badge": "pending_compliance",
            "compliance_id": "123-45-6789"
        }
    ],
    "meta": {
        "total_properties": 1,
        "platform_adoption_metrics": {
            "airbnb_linked": False,
            "vrbo_linked": False
        }
    }
}

try:
    obj = PropertiesResponseOut(**data)
    print(obj.model_dump())
except Exception as e:
    print(e)
