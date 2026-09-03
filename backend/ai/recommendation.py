def recommend_action(incident: dict) -> str:
	severity = incident.get("severity", "").lower()
	if severity in ("critical", "high"):
		return "Dispatch the nearest available response asset."
	return "Monitor the incident and assess available resources."


def assess_risk(data: dict) -> dict:
	"""Calculate an explainable prototype risk level and score."""
	if not isinstance(data, dict):
		data = {}

	score = 0
	reasons = []

	severity = data.get("severity")
	severity = severity.upper() if isinstance(severity, str) else ""
	severity_points = {"CRITICAL": 55, "HIGH": 35, "MEDIUM": 15, "LOW": 5}
	if severity in severity_points:
		score += severity_points[severity]
		reasons.append(f"{severity.title()} incident severity")

	distress = data.get("people_distress")
	distress = distress.upper() if isinstance(distress, str) else ""
	distress_points = {"HIGH": 20, "MEDIUM": 10, "LOW": 2}
	if distress in distress_points:
		score += distress_points[distress]
		reasons.append(f"{distress.title()} distress reported")

	population = data.get("affected_population")
	if isinstance(population, bool):
		population = None
	if isinstance(population, (int, float)):
		if population >= 5000:
			score += 15
			reasons.append("Large affected population")
		elif population >= 1000:
			score += 8
			reasons.append("Moderate affected population")
		elif population >= 100:
			score += 3
			reasons.append("Affected population")

	score = min(max(int(score), 0), 100)
	if score >= 75:
		level = "CRITICAL"
	elif score >= 50:
		level = "HIGH"
	elif score >= 25:
		level = "MEDIUM"
	else:
		level = "LOW"

	return {"level": level, "score": score, "reasons": reasons}


def generate_recommendations(data: dict) -> dict:
	"""Return deterministic actions and resources for an incident."""
	if not isinstance(data, dict):
		data = {}

	incident_type = data.get("type")
	incident_type = incident_type.upper() if isinstance(incident_type, str) else "UNKNOWN"
	severity = data.get("severity")
	severity = severity.upper() if isinstance(severity, str) else "LOW"

	if incident_type == "FLOOD" and severity == "CRITICAL":
		actions = [
			"Deploy aerial search",
			"Alert medical team",
			"Divert traffic",
			"Consider shelter coordination",
		]
		resources = ["Drone", "Medical team", "Rescue team", "Shelter support"]
	elif incident_type == "FIRE" and severity in {"HIGH", "CRITICAL"}:
		actions = ["Coordinate fire response", "Establish an exclusion zone", "Alert medical team"]
		resources = ["Fire response", "Medical team", "Ground rescue"]
	elif incident_type == "ACCIDENT" and severity in {"HIGH", "CRITICAL"}:
		actions = ["Coordinate medical response", "Secure the area", "Divert traffic"]
		resources = ["Ambulance/medical response", "Ground rescue", "Traffic control"]
	else:
		actions = ["Verify the report", "Monitor for updates"]
		resources = []

	return {"actions": actions, "resources": resources}
