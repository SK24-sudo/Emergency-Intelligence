import argparse
import json
from urllib.request import Request, urlopen


def dispatch_robot(incident_id: int, asset_id: int, base_url: str = "http://127.0.0.1:8000") -> dict:
	request = Request(
		base_url.rstrip("/") + "/dispatch",
		data=json.dumps({"incident_id": incident_id, "asset_id": asset_id}).encode(),
		headers={"Content-Type": "application/json"},
	)
	with urlopen(request) as response:
		return json.loads(response.read())


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("incident_id", type=int)
	parser.add_argument("asset_id", type=int)
	args = parser.parse_args()
	print(json.dumps(dispatch_robot(args.incident_id, args.asset_id)))