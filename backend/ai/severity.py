def estimate_severity(incident: dict) -> str:
	text = f"{incident.get('type', '')} {incident.get('description', '')}".lower()
	if any(word in text for word in ("critical", "trapped", "collapse")):
		return "critical"
	if any(word in text for word in ("fire", "flood", "injured")):
		return "high"
	if text.strip():
		return "medium"
	return "low"
