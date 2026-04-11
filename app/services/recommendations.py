from typing import Dict, List, Any
from app.services.listing_optimizer import ListingOptimizerService
from app.schemas.recommendations import Recommendation


class RecommendationEngineService:
    """
    Service for generating actionable recommendations to improve listing performance.
    Analyzes listing metrics and provides prioritized suggestions.
    """
    
    def __init__(self):
        self.optimizer_service = ListingOptimizerService()
    
    def generate_recommendations(self, property_id: str) -> Dict[str, Any]:
        """
        Generate recommendations based on listing metrics.
        
        Args:
            property_id: The property ID to analyze
            
        Returns:
            Dictionary containing recommendations and analysis
        """
        # Mock fetching metrics - in production, this would query the database
        # or call the ListingOptimizerService to get real metrics
        metrics = self._fetch_listing_metrics(property_id)
        
        # Calculate overall health score
        health_score = self._calculate_health_score(metrics)
        
        # Generate recommendations based on metrics
        recommendations = self._analyze_and_recommend(metrics)
        
        # Generate summary
        summary = self._generate_summary(health_score, recommendations)
        
        return {
            "property_id": property_id,
            "overall_health_score": health_score,
            "recommendations": recommendations,
            "summary": summary
        }
    
    def _fetch_listing_metrics(self, property_id: str) -> Dict[str, Any]:
        """
        Fetch listing metrics for analysis.
        In production, this would query the database or call external APIs.
        """
        # Mock data - simulating real listing metrics
        return {
            "occupancy_rate": 0.65,
            "average_rating": 4.2,
            "response_rate": 0.85,
            "response_time_hours": 6,
            "booking_rate": 0.45,
            "cancellation_rate": 0.08,
            "photo_count": 8,
            "description_length": 450,
            "amenities_count": 12,
            "price_competitiveness": 0.72,  # 0-1 scale vs market
            "calendar_availability": 0.80,
            "review_count": 23,
            "instant_book_enabled": False
        }
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall listing health score (0-100)"""
        score = 0.0
        
        # Occupancy rate (25%)
        score += metrics.get("occupancy_rate", 0) * 25
        
        # Rating (20%)
        score += (metrics.get("average_rating", 0) / 5.0) * 20
        
        # Response metrics (15%)
        response_score = metrics.get("response_rate", 0) * 0.7
        response_time_score = max(0, 1 - (metrics.get("response_time_hours", 24) / 24)) * 0.3
        score += (response_score + response_time_score) * 15
        
        # Booking rate (15%)
        score += metrics.get("booking_rate", 0) * 15
        
        # Content quality (10%)
        photo_score = min(1.0, metrics.get("photo_count", 0) / 20)
        desc_score = min(1.0, metrics.get("description_length", 0) / 800)
        score += (photo_score * 0.6 + desc_score * 0.4) * 10
        
        # Calendar availability (10%)
        score += metrics.get("calendar_availability", 0) * 10
        
        # Price competitiveness (5%)
        score += metrics.get("price_competitiveness", 0) * 5
        
        return round(score, 2)
    
    def _analyze_and_recommend(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze metrics and generate prioritized recommendations"""
        recommendations = []
        
        # Response time recommendations
        if metrics.get("response_time_hours", 0) > 2:
            recommendations.append({
                "category": "communication",
                "priority": "high",
                "title": "Improve Response Time",
                "description": f"Your average response time is {metrics['response_time_hours']} hours. Aim to respond within 1 hour to increase booking rates.",
                "impact": "Can increase booking rate by 15-20%"
            })
        
        # Photo recommendations
        if metrics.get("photo_count", 0) < 15:
            recommendations.append({
                "category": "photos",
                "priority": "high",
                "title": "Add More High-Quality Photos",
                "description": f"You have {metrics['photo_count']} photos. Listings with 20+ professional photos get 40% more bookings.",
                "impact": "Can increase booking rate by 25-40%"
            })
        
        # Instant book recommendation
        if not metrics.get("instant_book_enabled", False):
            recommendations.append({
                "category": "booking",
                "priority": "medium",
                "title": "Enable Instant Book",
                "description": "Instant Book listings appear higher in search results and convert 30% better.",
                "impact": "Can increase visibility and bookings by 30%"
            })
        
        # Pricing recommendations
        if metrics.get("price_competitiveness", 0) < 0.6:
            recommendations.append({
                "category": "pricing",
                "priority": "high",
                "title": "Adjust Pricing Strategy",
                "description": "Your pricing is below market average. Consider dynamic pricing to maximize revenue during peak periods.",
                "impact": "Can increase revenue by 20-35%"
            })
        elif metrics.get("price_competitiveness", 0) > 0.9:
            recommendations.append({
                "category": "pricing",
                "priority": "medium",
                "title": "Review Pricing Competitiveness",
                "description": "Your pricing is above market average. This may be limiting bookings. Consider adjusting for better occupancy.",
                "impact": "Can increase occupancy rate by 10-15%"
            })
        
        # Calendar availability
        if metrics.get("calendar_availability", 0) < 0.5:
            recommendations.append({
                "category": "availability",
                "priority": "medium",
                "title": "Increase Calendar Availability",
                "description": f"Only {int(metrics['calendar_availability'] * 100)}% of your calendar is available. Update your calendar to capture more bookings.",
                "impact": "Can increase booking opportunities by 20%"
            })
        
        # Description recommendations
        if metrics.get("description_length", 0) < 500:
            recommendations.append({
                "category": "description",
                "priority": "low",
                "title": "Enhance Listing Description",
                "description": "Add more details about your space, neighborhood, and unique features. Detailed descriptions build trust.",
                "impact": "Can increase conversion rate by 10-15%"
            })
        
        # Rating recommendations
        if metrics.get("average_rating", 0) < 4.5:
            recommendations.append({
                "category": "quality",
                "priority": "high",
                "title": "Improve Guest Experience",
                "description": f"Your rating is {metrics['average_rating']}/5.0. Focus on cleanliness, communication, and amenities to boost ratings.",
                "impact": "Higher ratings lead to 25% more bookings"
            })
        
        # Amenities recommendations
        if metrics.get("amenities_count", 0) < 15:
            recommendations.append({
                "category": "amenities",
                "priority": "low",
                "title": "Add More Amenities",
                "description": "Consider adding WiFi, workspace, or other popular amenities to attract more guests.",
                "impact": "Can increase appeal to business travelers by 20%"
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations
    
    def _generate_summary(self, health_score: float, recommendations: List[Dict]) -> str:
        """Generate a summary of the listing's performance"""
        high_priority_count = sum(1 for r in recommendations if r["priority"] == "high")
        
        if health_score >= 80:
            status = "excellent"
            message = "Your listing is performing very well!"
        elif health_score >= 60:
            status = "good"
            message = "Your listing is performing well with room for improvement."
        elif health_score >= 40:
            status = "fair"
            message = "Your listing needs attention to improve performance."
        else:
            status = "needs improvement"
            message = "Your listing requires significant improvements."
        
        summary = f"Overall health score: {health_score}/100 ({status}). {message}"
        
        if high_priority_count > 0:
            summary += f" Focus on {high_priority_count} high-priority recommendation{'s' if high_priority_count > 1 else ''} first."
        
        return summary
