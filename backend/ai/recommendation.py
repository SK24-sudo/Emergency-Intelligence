def recommend_action(incident: dict) -> str:
	severity = incident.get("severity", "").lower()
	if severity in ("critical", "high"):
		return "Dispatch the nearest available response asset."
	return "Monitor the incident and assess available resources."
