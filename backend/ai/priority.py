def priority_for_severity(severity: str) -> str:
	return {"critical": "P1", "high": "P1", "medium": "P2", "low": "P3"}.get(severity.lower(), "P3")
