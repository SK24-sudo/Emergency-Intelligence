def is_duplicate(first: dict, second: dict) -> bool:
	return (
		first.get("type", "").lower() == second.get("type", "").lower()
		and first.get("latitude") == second.get("latitude")
		and first.get("longitude") == second.get("longitude")
	)


INCIDENT_KEYWORDS = {
	"flood": {"flood", "flooded", "waterlogging", "water", "submerged", "stranded", "vehicles stuck"},
	"fire": {"fire", "smoke", "burning", "flames", "blaze"},
	"accident": {"accident", "crash", "collision"},
}

LOCATION_KEYWORDS = {"bridge", "market", "station", "highway"}


def _text(value):
	return value.lower() if isinstance(value, str) else ""


def _matched_keywords(description, keywords):
	text = _text(description)
	return {keyword for keyword in keywords if keyword in text}


def _coordinates(report):
	if not isinstance(report, dict):
		return None

	location = report.get("location")
	if not isinstance(location, dict):
		return None

	latitude = location.get("latitude")
	longitude = location.get("longitude")
	if isinstance(latitude, bool) or isinstance(longitude, bool):
		return None
	if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
		return None
	return latitude, longitude


def _matching_details(report, existing_report):
	report_text = report.get("description") if isinstance(report, dict) else None
	existing_text = existing_report.get("description") if isinstance(existing_report, dict) else None
	report_categories = {
		category for category, keywords in INCIDENT_KEYWORDS.items()
		if _matched_keywords(report_text, keywords)
	}
	existing_categories = {
		category for category, keywords in INCIDENT_KEYWORDS.items()
		if _matched_keywords(existing_text, keywords)
	}
	shared_categories = report_categories & existing_categories
	if not shared_categories:
		return False, set(), False

	report_locations = _matched_keywords(report_text, LOCATION_KEYWORDS)
	existing_locations = _matched_keywords(existing_text, LOCATION_KEYWORDS)
	shared_locations = report_locations & existing_locations

	report_coordinates = _coordinates(report)
	existing_coordinates = _coordinates(existing_report)
	geographically_close = False
	if report_coordinates and existing_coordinates:
		geographically_close = (
			abs(report_coordinates[0] - existing_coordinates[0]) <= 0.01
			and abs(report_coordinates[1] - existing_coordinates[1]) <= 0.01
		)

	return bool(shared_locations or geographically_close), shared_locations, geographically_close


def detect_duplicate(report: dict, existing_reports: list[dict]) -> dict:
	"""Find related reports using explainable text and coordinate matching."""
	if not isinstance(report, dict):
		report = {}
	if not isinstance(existing_reports, list):
		existing_reports = []

	matched_reports = []
	shared_locations = set()
	close_report_count = 0
	for existing_report in existing_reports:
		if not isinstance(existing_report, dict):
			continue
		is_match, locations, geographically_close = _matching_details(report, existing_report)
		if is_match:
			matched_reports.append(existing_report)
			shared_locations.update(locations)
			if geographically_close:
				close_report_count += 1

	reasons = []
	for location in sorted(shared_locations):
		reasons.append(f"Shared location term: {location}")

	report_text = report.get("description")
	matched_categories = [
		category for category, keywords in INCIDENT_KEYWORDS.items()
		if _matched_keywords(report_text, keywords)
	]
	for category in matched_categories:
		reasons.append(f"Related {category} keywords")
	if close_report_count:
		reasons.append("Reports are geographically close")

	matched_ids = [existing.get("id") for existing in matched_reports if existing.get("id") is not None]
	match_count = len(matched_reports)
	if not match_count:
		return {
			"same_incident": False,
			"related_reports": 1,
			"matched_report_ids": [],
			"confidence": 0.0,
			"reasons": [],
		}

	confidence = 0.55
	if shared_locations:
		confidence += 0.15
	if close_report_count:
		confidence += 0.10
	if matched_categories:
		confidence += 0.10

	return {
		"same_incident": True,
		"related_reports": match_count + 1,
		"matched_report_ids": matched_ids,
		"confidence": min(round(confidence, 2), 0.98),
		"reasons": reasons,
	}


def correlate_reports(reports: list[dict]) -> list[dict]:
	"""Group related report copies into incident summaries without mutation."""
	if not isinstance(reports, list):
		return []

	groups = []
	for report in reports:
		report_copy = dict(report) if isinstance(report, dict) else {}
		matching_groups = []
		for index, group in enumerate(groups):
			if any(_matching_details(report_copy, member)[0] for member in group["reports"]):
				matching_groups.append(index)

		if not matching_groups:
			groups.append({"reports": [report_copy]})
			continue

		first_group = groups[matching_groups[0]]
		first_group["reports"].append(report_copy)
		for index in reversed(matching_groups[1:]):
			first_group["reports"].extend(groups.pop(index)["reports"])

	result = []
	for index, group in enumerate(groups, start=1):
		group_reports = group["reports"]
		report_ids = [report.get("id") for report in group_reports if report.get("id") is not None]
		sources = []
		for report in group_reports:
			source = report.get("source")
			if source is not None and source not in sources:
				sources.append(source)
		result.append({
			"incident_id": f"incident-{index}",
			"related_reports": len(group_reports),
			"report_ids": report_ids,
			"sources": sources,
			"multi_source": len(sources) >= 2,
		})

	return result
