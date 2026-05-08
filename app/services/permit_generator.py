from typing import Dict, Any, List
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.models.property import Property
from app.services.florida_compliance_engine import FloridaComplianceEngine


class PermitGeneratorService:
    """
    Service for generating automated permit applications based on property compliance data.
    Leverages FloridaComplianceEngine to determine requirements and generate applications.
    """
    
    @staticmethod
    def generate_application(db: Session, property_id: str) -> Dict[str, Any]:
        """
        Generate a permit application for a given property.
        
        Args:
            db: Database session
            property_id: ID of the property to generate permit for
            
        Returns:
            Dictionary containing the generated permit application details
        """
        # Fetch property from database
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        
        if not property_obj:
            raise ValueError(f"Property with id {property_id} not found")
        
        # Extract property details for compliance evaluation
        property_details = {
            "address": property_obj.address,
            "bedrooms": property_obj.bedrooms or 2,
            "max_occupancy": property_obj.max_occupancy or 4,
            "has_pool": property_obj.has_pool or False,
            "parking_spaces": property_obj.parking_spaces or 1,
        }
        
        # Determine county from address (simplified logic)
        county = PermitGeneratorService._extract_county(property_obj.address)
        
        # Evaluate compliance using FloridaComplianceEngine
        compliance_result = FloridaComplianceEngine.evaluate_compliance(
            county=county,
            property_details=property_details
        )
        
        # Generate application ID
        application_id = f"APP-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"
        
        # Determine required documents based on compliance
        required_documents = PermitGeneratorService._get_required_documents(
            county, 
            compliance_result
        )
        
        # Generate next steps
        next_steps = PermitGeneratorService._generate_next_steps(
            compliance_result.get("is_compliant", False)
        )
        
        # Build application response
        application = {
            "application_id": application_id,
            "property_id": property_id,
            "county": county,
            "application_type": "Short-Term Rental Permit",
            "status": "draft",
            "generated_at": datetime.now(),
            "required_documents": required_documents,
            "compliance_summary": {
                "is_compliant": compliance_result.get("is_compliant", False),
                "issues": compliance_result.get("issues", [])
            },
            "estimated_processing_time": PermitGeneratorService._get_processing_time(county),
            "next_steps": next_steps
        }
        
        return application
    
    @staticmethod
    def _extract_county(address: str) -> str:
        """Extract county from address string."""
        address_lower = address.lower()
        if "pasco" in address_lower:
            return "Pasco"
        elif "hillsborough" in address_lower or "tampa" in address_lower:
            return "Hillsborough"
        else:
            # Default to Pasco for demo purposes
            return "Pasco"
    
    @staticmethod
    def _get_required_documents(county: str, compliance_result: Dict) -> List[str]:
        """Determine required documents based on county and compliance status."""
        base_documents = [
            "Form HR-7020 (Florida Short-Term Rental Registration)",
            "Proof of Property Insurance",
            "Fire Safety Inspection Certificate",
            "Smoke Detector Compliance Affidavit"
        ]
        
        if county == "Pasco":
            base_documents.extend([
                "Pasco County Business Tax Receipt",
                "Floor Plan with Emergency Exits Marked"
            ])
        elif county == "Hillsborough":
            base_documents.extend([
                "Hillsborough County Occupational License",
                "Parking Plan Diagram"
            ])
        
        # Add conditional documents based on compliance issues
        issues = compliance_result.get("issues", [])
        for issue in issues:
            if "pool" in issue.get("description", "").lower():
                base_documents.append("Pool Safety Barrier Certification")
            if "parking" in issue.get("description", "").lower():
                base_documents.append("Off-Street Parking Agreement")
        
        return base_documents
    
    @staticmethod
    def _get_processing_time(county: str) -> str:
        """Get estimated processing time by county."""
        processing_times = {
            "Pasco": "14-21 business days",
            "Hillsborough": "10-15 business days"
        }
        return processing_times.get(county, "14-21 business days")
    
    @staticmethod
    def _generate_next_steps(is_compliant: bool) -> List[str]:
        """Generate next steps based on compliance status."""
        if is_compliant:
            return [
                "Review the generated application details",
                "Gather and upload all required documents",
                "Pay applicable permit fees",
                "Submit application to county office",
                "Schedule required inspections"
            ]
        else:
            return [
                "Review compliance issues listed above",
                "Address all non-compliant items",
                "Re-run compliance check",
                "Once compliant, proceed with application submission"
            ]
