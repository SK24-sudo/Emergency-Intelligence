import unittest
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from backend.ai import analyze_incident
from backend.ai.duplicate import correlate_reports, detect_duplicate
from backend.main import app


class AIFlowTests(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app)

	def test_pune_flood(self):
		result = analyze_incident({
			"description": "Water has entered houses and vehicles are stranded",
			"affected_population": 8000,
			"people_distress": "HIGH",
		})

		self.assertEqual(result["type"], "FLOOD")
		self.assertEqual(result["severity"], "CRITICAL")
		self.assertEqual(result["priority"], "P1")
		self.assertEqual(result["priority_score"], 94)
		self.assertEqual(result["risk"]["level"], "CRITICAL")
		self.assertTrue(result["recommendations"]["actions"])
		self.assertTrue(result["recommendations"]["resources"])

	def test_fire_classification(self):
		result = analyze_incident({"description": "Large fire and smoke coming from a building"})
		self.assertEqual(result["type"], "FIRE")

	def test_accident_classification(self):
		result = analyze_incident({"description": "Two vehicles crashed on the highway"})
		self.assertEqual(result["type"], "ACCIDENT")

	def test_unknown_and_safe_recommendations(self):
		result = analyze_incident({"description": "Something happened near the road"})
		self.assertEqual(result["type"], "UNKNOWN")
		self.assertTrue(result["recommendations"]["actions"])
		self.assertEqual(result["recommendations"]["resources"], [])

	def test_edge_cases(self):
		for value in (None, {}, {"description": "   "}, {"description": 123}):
			result = analyze_incident(value)
			self.assertEqual(result["type"], "UNKNOWN")
			self.assertGreaterEqual(result["confidence"], 0.0)
			self.assertLessEqual(result["confidence"], 0.98)

		result = analyze_incident({
			"description": "Water near bridge",
			"location": {"latitude": "invalid", "longitude": None},
		})
		self.assertEqual(result["type"], "FLOOD")
		self.assertIn(result["priority_score"], range(101))
		self.assertIn(result["risk"]["score"], range(101))

	def test_correlation(self):
		reports = [
			{
				"id": "report-a",
				"description": "Flood near bridge",
				"location": {"latitude": 18.5204, "longitude": 73.8567},
				"source": "CITIZEN",
			},
			{
				"id": "report-b",
				"description": "Waterlogging near bridge",
				"location": {"latitude": 18.5205, "longitude": 73.8568},
				"source": "OFFICIAL",
			},
		]
		incoming = {
			"id": "report-c",
			"description": "Vehicles stuck near bridge",
			"location": {"latitude": 18.5206, "longitude": 73.8569},
			"source": "CITIZEN",
		}

		result = detect_duplicate(incoming, reports)
		self.assertTrue(result["same_incident"])
		self.assertEqual(result["related_reports"], 3)
		groups = correlate_reports(reports + [incoming])
		self.assertEqual(len(groups), 1)
		self.assertTrue(groups[0]["multi_source"])

		unrelated = {
			"id": "report-d",
			"description": "Fire reported at market",
			"location": {"latitude": 18.6000, "longitude": 73.9000},
			"source": "CITIZEN",
		}
		self.assertFalse(detect_duplicate(unrelated, reports)["same_incident"])

	def test_api_analyze(self):
		response = self.client.post("/ai/analyze", json={
			"description": "Water has entered houses and vehicles are stranded",
			"affected_population": 8000,
			"people_distress": "HIGH",
		})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["priority_score"], 94)

	def test_api_priority(self):
		response = self.client.post("/ai/priority", json={
			"severity": "CRITICAL",
			"affected_population": 8000,
			"people_distress": "HIGH",
			"confidence": 0.94,
		})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["priority_score"], 94)

	def test_api_recommend(self):
		response = self.client.post("/ai/recommend", json={
			"description": "Water has entered houses and vehicles are stranded",
			"affected_population": 8000,
			"people_distress": "HIGH",
		})
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertIn("risk", body)
		self.assertIn("recommendations", body)
		self.assertIn("actions", body["recommendations"])


if __name__ == "__main__":
	unittest.main()
