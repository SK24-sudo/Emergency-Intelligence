def classify_incident(incident_type: str, description: str = "") -> str:
	text = f"{incident_type} {description}".lower()
	for keyword, category in (("fire", "fire"), ("flood", "flood"), ("medical", "medical"), ("collapse", "structural")):
		if keyword in text:
			return category
	return "general"
