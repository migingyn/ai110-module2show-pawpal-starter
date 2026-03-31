from typing import Any


class Pet:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self.needs: list[dict] = []  # e.g. {"type": "walk", "duration": 20, "priority": "high", "frequency": "daily"}

    def get_needs(self) -> list[dict]:
        pass

    def add_need(self, need: dict) -> None:
        pass


class Owner:
    def __init__(self, name: str, available_hours: list[tuple[int, int]], preferences: dict[str, Any]):
        self.name = name
        self.available_hours = available_hours  # list of (start, end) in minutes since midnight, e.g. (480, 600) = 8am-10am
        self.preferences = preferences          # e.g. {"prefers_morning": True}
        self.pet: Pet | None = None

    def get_constraints(self) -> dict[str, Any]:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass


class Plan:
    def __init__(self, owner: Owner, pet: Pet, date: str):
        self.owner = owner
        self.pet = pet
        self.date = date    # e.g. "2026-03-30"
        self.tasks: list[dict] = []  # e.g. {"title": "Morning walk", "duration": 20, "priority": "high", "time": 480, "reason": "..."}

    def build(self) -> None:
        pass

    def explain(self) -> str:
        pass


class Calendar:
    def __init__(self):
        self.plans: dict[str, Plan] = {}  # keyed by date string e.g. "2026-03-30"

    def add_plan(self, date: str, plan: Plan) -> None:
        pass

    def get_plan(self, date: str) -> Plan | None:
        pass

    def view_week(self, start_date: str) -> dict[str, Plan]:
        pass
