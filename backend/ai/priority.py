def priority_for_severity(severity: str) -> str:
	return {"critical": "P1", "high": "P1", "medium": "P2", "low": "P3"}.get(severity.lower(), "P3")


def calculate_priority(data: dict) -> dict:
	"""Calculate an explainable prototype priority for one incident."""
	if not isinstance(data, dict):
		data = {}

	score = 0
	reasons = []

	severity_points = {
		"CRITICAL": 55,
		"HIGH": 35,
		"MEDIUM": 15,
		"LOW": 5,
	}
	severity = data.get("severity")
	if isinstance(severity, str):
		severity = severity.upper()
	points = severity_points.get(severity, 0)
	if points:
		score += points
		reasons.append(f"{severity.title()} severity")

	population = data.get("affected_population")
	if isinstance(population, bool):
		population = None
	if isinstance(population, (int, float)):
		if population >= 5000:
			score += 20
			reasons.append("Large affected population")
		elif population >= 1000:
			score += 12
			reasons.append("Moderate affected population")
		elif population >= 100:
			score += 5
			reasons.append("Affected population")

	distress_points = {
		"HIGH": 15,
		"MEDIUM": 8,
		"LOW": 2,
	}
	distress = data.get("people_distress")
	if isinstance(distress, str):
		distress = distress.upper()
	points = distress_points.get(distress, 0)
	if points:
		score += points
		reasons.append(f"{distress.title()} distress")

	confidence = data.get("confidence")
	if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
		if confidence >= 0.90:
			score += 4
			reasons.append("High confidence")
		elif confidence >= 0.70:
			score += 2
			reasons.append("Moderate confidence")

	score = min(max(int(score), 0), 100)
	if score >= 70:
		priority = "P1"
	elif score >= 40:
		priority = "P2"
	else:
		priority = "P3"

	return {
		"priority": priority,
		"score": score,
		"reasons": reasons,
	}


def rank_incidents(incidents: list[dict]) -> list[dict]:
	"""Return incident copies ordered by calculated score, highest first."""
	if not isinstance(incidents, list):
		return []

	ranked = []
	for incident in incidents:
		incident_copy = dict(incident) if isinstance(incident, dict) else {}
		incident_copy.update(calculate_priority(incident_copy))
		ranked.append(incident_copy)

	return sorted(
		ranked,
		key=lambda incident: incident["score"],
		reverse=True,
	)
