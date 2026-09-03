INCIDENT_KEYWORDS = {
	"FLOOD": {
		"flood": 0.30,
		"flooded": 0.25,
		"waterlogging": 0.30,
		"water": 0.13,
		"entered houses": 0.14,
		"stranded": 0.12,
		"submerged": 0.20,
	},
	"FIRE": {
		"fire": 0.30,
		"smoke": 0.20,
		"burning": 0.25,
		"flames": 0.25,
		"blaze": 0.30,
	},
	"ACCIDENT": {
		"accident": 0.30,
		"crash": 0.30,
		"collision": 0.30,
		"vehicle collision": 0.35,
		"road accident": 0.35,
	},
}


def classify_incident(incident_type: str, description: str = None):
	if description is not None:
		text = f"{incident_type} {description}".lower()
		for keyword, category in (("fire", "fire"), ("flood", "flood"), ("medical", "medical"), ("collapse", "structural")):
			if keyword in text:
				return category
		return "general"

	description = incident_type
	if not isinstance(description, str) or not description.strip():
		return {"type": "UNKNOWN", "confidence": 0.0}

	text = description.lower()
	best_type = "UNKNOWN"
	best_score = 0.0

	for incident_type, keywords in INCIDENT_KEYWORDS.items():
		score = sum(weight for keyword, weight in keywords.items() if keyword in text)

		if score > best_score:
			best_type = incident_type
			best_score = score

	if best_score == 0:
		return {"type": "UNKNOWN", "confidence": 0.30}

	confidence = round(min(0.55 + best_score, 0.98), 2)

	return {
		"type": best_type,
		"confidence": confidence,
	}
