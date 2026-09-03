from fastapi import APIRouter

from ai import analyze_incident
from ai.priority import calculate_priority


router = APIRouter()


@router.post("/analyze")
def analyze(data: dict) -> dict:
	return analyze_incident(data)


@router.post("/priority")
def priority(data: dict) -> dict:
	result = calculate_priority(data)
	return {
		"priority": result["priority"],
		"score": result["score"],
		"priority_score": result["score"],
		"reasons": result["reasons"],
	}


@router.post("/recommend")
def recommend(data: dict) -> dict:
	result = analyze_incident(data)
	return {
		"risk": result["risk"],
		"recommendations": result["recommendations"],
	}