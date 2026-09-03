import argparse
import json
from urllib.request import Request, urlopen


class DroneSimulation:
	def __init__(self, base_url: str = "http://127.0.0.1:8000"):
		self.base_url = base_url.rstrip("/")

	def _post(self, path: str, payload: dict) -> dict:
		request = Request(self.base_url + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
		with urlopen(request) as response:
			return json.loads(response.read())

	def report_status(self, mission_id: int, status: str, latitude: float | None = None, longitude: float | None = None) -> dict:
		payload = {"status": status}
		if latitude is not None:
			payload["latitude"] = latitude
		if longitude is not None:
			payload["longitude"] = longitude
		return self._post(f"/missions/{mission_id}/status", payload)

	def find_person(self, incident_id: int, name: str, latitude: float, longitude: float) -> dict:
		return self._post("/persons", {"incident_id": incident_id, "name": name, "status": "found", "latitude": latitude, "longitude": longitude})

	def run_search(self, mission_id: int, incident_id: int, latitude: float, longitude: float) -> dict:
		self.report_status(mission_id, "dispatched")
		self.report_status(mission_id, "searching", latitude, longitude)
		person = self.find_person(incident_id, "Person-01", latitude, longitude)
		complete = self.report_status(mission_id, "search_complete", latitude, longitude)
		return {"person": person, "mission": complete}


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("mission_id", type=int)
	parser.add_argument("incident_id", type=int)
	args = parser.parse_args()
	print(json.dumps(DroneSimulation().run_search(args.mission_id, args.incident_id, 16.267, 73.484)))