def estimate_severity(incident: dict) -> str:
	text = f"{incident.get('type', '')} {incident.get('description', '')}".lower()
	if any(word in text for word in ("critical", "trapped", "collapse")):
		return "critical"
	if any(word in text for word in ("fire", "flood", "injured")):
		return "high"
	if text.strip():
		return "medium"
	return "low"


VALID_LEVELS = {"HIGH", "MEDIUM", "LOW"}


def _safe_upper(value) -> str:
	"""Return an upper-cased string for any value, defaulting to empty string."""
	if value is None:
		return ""
	try:
		return str(value).strip().upper()
	except Exception:
		return ""


def _safe_population(value) -> int:
	"""Return a non-negative int for affected_population, defaulting to 0."""
	try:
		population = int(value)
	except (TypeError, ValueError):
		return 0
	return population if population > 0 else 0


def calculate_severity(data: dict) -> str:
	"""
	Determine the severity of an incident using simple, explainable,
	deterministic rules. Returns one of: "CRITICAL", "HIGH", "MEDIUM", "LOW".

	Missing, invalid, or unknown fields are treated safely as low/neutral
	impact instead of causing a crash or an invented assumption.
	"""
	if not isinstance(data, dict):
		return "LOW"

	incident_type = _safe_upper(data.get("type"))
	population = _safe_population(data.get("affected_population"))

	distress = _safe_upper(data.get("people_distress"))
	if distress not in VALID_LEVELS:
		distress = "LOW"

	infrastructure = _safe_upper(data.get("infrastructure_impact"))
	if infrastructure not in VALID_LEVELS:
		infrastructure = "LOW"

	# CRITICAL: very large affected population with high distress,
	# or severe (HIGH) infrastructure impact reported on its own.
	if infrastructure == "HIGH":
		return "CRITICAL"
	if population >= 5000 and distress == "HIGH":
		return "CRITICAL"

	# HIGH: high distress, a large affected population, or a FIRE
	# incident with meaningful (moderate+) impact.
	if distress == "HIGH":
		return "HIGH"
	if population >= 1000:
		return "HIGH"
	if incident_type == "FIRE" and (infrastructure == "MEDIUM" or population >= 100):
		return "HIGH"

	# MEDIUM: moderate distress, moderate infrastructure impact,
	# or a smaller-but-notable affected population.
	if distress == "MEDIUM" or infrastructure == "MEDIUM":
		return "MEDIUM"
	if population >= 100:
		return "MEDIUM"

	# LOW: limited impact, low distress, missing details, or unknown
	# incidents fall back here by default.
	return "LOW"
