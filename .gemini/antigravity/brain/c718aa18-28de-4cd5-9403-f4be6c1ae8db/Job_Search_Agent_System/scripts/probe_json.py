"""
Probe script to inspect JSON structure.
"""
import json
import os

path = r"c:\Users\Lucas\.gemini\antigravity\brain\c718aa18-28de-4cd5-9403-f4be6c1ae8db\Job_Search_Agent_System\resources\base_real.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
    print("--- RAW KEYS ---")
    print(list(data.keys()))
    if "personas_specialises" in data:
        print("\n--- personas_specialises ---")
        print(list(data["personas_specialises"].keys()))
    if "clusters" in data:
        print("\n--- clusters ---")
        print(list(data["clusters"].keys()))
    if "persona_engine" in data:
        print("\n--- persona_engine ---")
        print(data["persona_engine"].get("clusters", []))
