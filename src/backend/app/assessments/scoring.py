from typing import List
from src.backend.app.assessments.models import Assessment, AssessmentDomain, AssessmentElementResponse

class ScoringService:
    @staticmethod
    def calculate_element_score(maturity_level: int) -> float:
        """
        Convert maturity level (1-5 or 1-4) to a percentage score.
        Assumption: 1-4 scale.
        1 -> 25.0
        2 -> 50.0
        3 -> 75.0
        4 -> 100.0
        (Or 0, 33, 66, 100 depending on framework. Using linear 25-step for now)
        """
        if not maturity_level or maturity_level < 1:
            return 0.0
        return min(maturity_level * 25.0, 100.0)

    @staticmethod
    def calculate_domain_score(domain: AssessmentDomain) -> float:
        """
        Average of element scores.
        """
        if not domain.elements:
            return 0.0
        
        total = sum(e.score for e in domain.elements if e.score is not None)
        count = len([e for e in domain.elements if e.score is not None])
        
        if count == 0:
            return 0.0
            
        return total / len(domain.elements) # Or count? Usually over total expected elements.

    @staticmethod
    def calculate_overall_score(assessment: Assessment) -> float:
        """
        Weighted average of domain scores.
        """
        if not assessment.domains:
            return 0.0
            
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for domain in assessment.domains:
            weight = domain.weight if domain.weight else 1.0 # Default weight
            score = domain.score if domain.score is not None else 0.0
            total_weighted_score += score * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return total_weighted_score / total_weight
