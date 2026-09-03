def is_duplicate(first: dict, second: dict) -> bool:
	return (
		first.get("type", "").lower() == second.get("type", "").lower()
		and first.get("latitude") == second.get("latitude")
		and first.get("longitude") == second.get("longitude")
	)
