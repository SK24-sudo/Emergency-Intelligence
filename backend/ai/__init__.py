from .classifier import classify_incident
from .priority import calculate_priority
from .recommendation import assess_risk, generate_recommendations
from .severity import calculate_severity


def analyze_incident(data: dict) -> dict:
	"""Run the pure-Python incident intelligence flow for one report."""
	if not isinstance(data, dict):
		data = {}

	description = data.get("description")
	if not isinstance(description, str) or not description.strip():
		classification = {"type": "UNKNOWN", "confidence": 0.0}
	else:
		classification = classify_incident(description)

	incident_data = {**data, **classification}
	severity = calculate_severity(incident_data)
	decision_data = {**incident_data, "severity": severity}
	priority = calculate_priority(decision_data)
	risk = assess_risk(decision_data)
	recommendations = generate_recommendations(decision_data)

	return {
		**classification,
		"severity": severity,
		**priority,
		"priority_score": priority["score"],
		"risk": risk,
		"recommendations": recommendations,
	}
