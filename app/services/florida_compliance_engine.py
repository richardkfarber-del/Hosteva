from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

class FloridaComplianceEngine:
    """
    Compliance engine for Florida municipal codes, specifically Pasco and Hillsborough counties.
    Evaluates property compliance against county-specific regulations.
    """
    
    # Pasco County Municipal Codes
    PASCO_CODES = {
        "short_term_rental_permit": {
            "required": True,
            "description": "Pasco County Short-Term Rental Business Tax Receipt",
            "reference": "Pasco County Code Chapter 134"
        },
        "fire_safety": {
            "required": True,
            "description": "Fire extinguisher and smoke alarms required",
            "reference": "Florida Fire Prevention Code"
        },
        "occupancy_limit": {
            "max_guests": 10,
            "description": "Maximum occupancy limit per dwelling unit",
            "reference": "Pasco County Code 134-3"
        },
        "parking_requirement": {
            "spaces_per_bedroom": 1,
            "description": "Off-street parking required",
            "reference": "Pasco County Code 134-4"
        },
        "noise_ordinance": {
            "quiet_hours": "22:00-07:00",
            "description": "Quiet hours enforcement",
            "reference": "Pasco County Code 14-31"
        }
    }
    
    # Hillsborough County Municipal Codes
    HILLSBOROUGH_CODES = {
        "vacation_rental_license": {
            "required": True,
            "description": "Hillsborough County Vacation Rental License",
            "reference": "Hillsborough County Code Chapter 30"
        },
        "state_registration": {
            "required": True,
            "description": "Florida Department of Business and Professional Regulation (DBPR) registration",
            "reference": "Florida Statute 509.242"
        },
        "fire_safety": {
            "required": True,
            "description": "Fire extinguisher, smoke alarms, and carbon monoxide detectors required",
            "reference": "Florida Fire Prevention Code"
        },
        "occupancy_limit": {
            "max_guests": 12,
            "description": "Maximum occupancy limit per dwelling unit",
            "reference": "Hillsborough County Code 30-5"
        },
        "parking_requirement": {
            "spaces_per_bedroom": 2,
            "description": "Two off-street parking spaces per bedroom",
            "reference": "Hillsborough County Code 30-6"
        },
        "inspection_requirement": {
            "frequency": "annual",
            "description": "Annual safety inspection required",
            "reference": "Hillsborough County Code 30-8"
        }
    }
    
    @staticmethod
    def evaluate_pasco_compliance(property_details: Dict) -> Dict:
        """
        Evaluate property compliance against Pasco County codes.
        
        Args:
            property_details: Dictionary containing property information
                - has_permit: bool
                - has_fire_safety: bool
                - num_guests: int
                - num_bedrooms: int
                - parking_spaces: int
                
        Returns:
            Dictionary with compliance status and issues
        """
        issues = []
        is_compliant = True
        
        # Check permit requirement
        if not property_details.get("has_permit", False):
            issues.append({
                "rule": "short_term_rental_permit",
                "status": "non_compliant",
                "message": "Missing Pasco County Short-Term Rental Business Tax Receipt",
                "reference": FloridaComplianceEngine.PASCO_CODES["short_term_rental_permit"]["reference"]
            })
            is_compliant = False
        
        # Check fire safety
        if not property_details.get("has_fire_safety", False):
            issues.append({
                "rule": "fire_safety",
                "status": "non_compliant",
                "message": "Fire safety equipment not verified",
                "reference": FloridaComplianceEngine.PASCO_CODES["fire_safety"]["reference"]
            })
            is_compliant = False
        
        # Check occupancy limit
        num_guests = property_details.get("num_guests", 0)
        max_guests = FloridaComplianceEngine.PASCO_CODES["occupancy_limit"]["max_guests"]
        if num_guests > max_guests:
            issues.append({
                "rule": "occupancy_limit",
                "status": "non_compliant",
                "message": f"Occupancy exceeds limit: {num_guests} guests (max {max_guests})",
                "reference": FloridaComplianceEngine.PASCO_CODES["occupancy_limit"]["reference"]
            })
            is_compliant = False
        
        # Check parking requirement
        num_bedrooms = property_details.get("num_bedrooms", 0)
        parking_spaces = property_details.get("parking_spaces", 0)
        required_parking = num_bedrooms * FloridaComplianceEngine.PASCO_CODES["parking_requirement"]["spaces_per_bedroom"]
        if parking_spaces < required_parking:
            issues.append({
                "rule": "parking_requirement",
                "status": "non_compliant",
                "message": f"Insufficient parking: {parking_spaces} spaces (required {required_parking})",
                "reference": FloridaComplianceEngine.PASCO_CODES["parking_requirement"]["reference"]
            })
            is_compliant = False
        
        return {
            "county": "Pasco",
            "is_compliant": is_compliant,
            "issues": issues,
            "evaluated_at": datetime.utcnow().isoformat(),
            "total_rules_checked": 5,
            "rules_passed": 5 - len(issues)
        }
    
    @staticmethod
    def evaluate_hillsborough_compliance(property_details: Dict) -> Dict:
        """
        Evaluate property compliance against Hillsborough County codes.
        
        Args:
            property_details: Dictionary containing property information
                - has_vacation_license: bool
                - has_state_registration: bool
                - has_fire_safety: bool
                - num_guests: int
                - num_bedrooms: int
                - parking_spaces: int
                - last_inspection_date: str (ISO format)
                
        Returns:
            Dictionary with compliance status and issues
        """
        issues = []
        is_compliant = True
        
        # Check vacation rental license
        if not property_details.get("has_vacation_license", False):
            issues.append({
                "rule": "vacation_rental_license",
                "status": "non_compliant",
                "message": "Missing Hillsborough County Vacation Rental License",
                "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["vacation_rental_license"]["reference"]
            })
            is_compliant = False
        
        # Check state registration
        if not property_details.get("has_state_registration", False):
            issues.append({
                "rule": "state_registration",
                "status": "non_compliant",
                "message": "Missing Florida DBPR registration",
                "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["state_registration"]["reference"]
            })
            is_compliant = False
        
        # Check fire safety
        if not property_details.get("has_fire_safety", False):
            issues.append({
                "rule": "fire_safety",
                "status": "non_compliant",
                "message": "Fire safety equipment not verified (extinguisher, smoke alarms, CO detectors)",
                "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["fire_safety"]["reference"]
            })
            is_compliant = False
        
        # Check occupancy limit
        num_guests = property_details.get("num_guests", 0)
        max_guests = FloridaComplianceEngine.HILLSBOROUGH_CODES["occupancy_limit"]["max_guests"]
        if num_guests > max_guests:
            issues.append({
                "rule": "occupancy_limit",
                "status": "non_compliant",
                "message": f"Occupancy exceeds limit: {num_guests} guests (max {max_guests})",
                "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["occupancy_limit"]["reference"]
            })
            is_compliant = False
        
        # Check parking requirement
        num_bedrooms = property_details.get("num_bedrooms", 0)
        parking_spaces = property_details.get("parking_spaces", 0)
        required_parking = num_bedrooms * FloridaComplianceEngine.HILLSBOROUGH_CODES["parking_requirement"]["spaces_per_bedroom"]
        if parking_spaces < required_parking:
            issues.append({
                "rule": "parking_requirement",
                "status": "non_compliant",
                "message": f"Insufficient parking: {parking_spaces} spaces (required {required_parking})",
                "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["parking_requirement"]["reference"]
            })
            is_compliant = False
        
        # Check inspection requirement
        last_inspection = property_details.get("last_inspection_date")
        if last_inspection:
            try:
                inspection_date = datetime.fromisoformat(last_inspection.replace('Z', '+00:00'))
                days_since_inspection = (datetime.utcnow() - inspection_date.replace(tzinfo=None)).days
                if days_since_inspection > 365:
                    issues.append({
                        "rule": "inspection_requirement",
                        "status": "non_compliant",
                        "message": f"Annual inspection overdue ({days_since_inspection} days since last inspection)",
                        "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["inspection_requirement"]["reference"]
                    })
                    is_compliant = False
            except (ValueError, AttributeError):
                issues.append({
                    "rule": "inspection_requirement",
                    "status": "non_compliant",
                    "message": "No valid inspection date on record",
                    "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["inspection_requirement"]["reference"]
                })
                is_compliant = False
        else:
            issues.append({
                "rule": "inspection_requirement",
                "status": "non_compliant",
                "message": "No inspection date on record",
                "reference": FloridaComplianceEngine.HILLSBOROUGH_CODES["inspection_requirement"]["reference"]
            })
            is_compliant = False
        
        return {
            "county": "Hillsborough",
            "is_compliant": is_compliant,
            "issues": issues,
            "evaluated_at": datetime.utcnow().isoformat(),
            "total_rules_checked": 6,
            "rules_passed": 6 - len(issues)
        }
    
    @staticmethod
    def evaluate_compliance(county: str, property_details: Dict) -> Dict:
        """
        Main entry point for compliance evaluation.
        Routes to appropriate county-specific evaluator.
        
        Args:
            county: "Pasco" or "Hillsborough"
            property_details: Property information dictionary
            
        Returns:
            Compliance evaluation results
        """
        county_lower = county.lower()
        
        if county_lower == "pasco":
            return FloridaComplianceEngine.evaluate_pasco_compliance(property_details)
        elif county_lower == "hillsborough":
            return FloridaComplianceEngine.evaluate_hillsborough_compliance(property_details)
        else:
            return {
                "county": county,
                "is_compliant": False,
                "issues": [{
                    "rule": "unsupported_county",
                    "status": "error",
                    "message": f"County '{county}' is not supported. Only Pasco and Hillsborough counties are currently supported.",
                    "reference": "N/A"
                }],
                "evaluated_at": datetime.utcnow().isoformat(),
                "total_rules_checked": 0,
                "rules_passed": 0
            }
