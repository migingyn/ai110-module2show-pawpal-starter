from dataclasses import dataclass, field
from typing import Any


@dataclass
class Need:
    type: str           # e.g. "walk", "feeding", "grooming"
    duration: int       # minutes
    priority: str       # "low", "medium", "high"
    frequency: str      # e.g. "daily", "twice_daily"


@dataclass
class Task:
    title: str
    duration: int       # minutes
    priority: str       # "low", "medium", "high"
    time: str = ""      # e.g. "8:00am"
    reason: str = ""    # explanation for why this task was scheduled


class Pet:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self.needs: list[Need] = []

    def get_needs(self) -> list[Need]:
        pass

    def add_need(self, need: Need) -> None:
        pass


class Owner:
    def __init__(self, name: str, available_hours: list[str], preferences: dict[str, Any]):
        self.name = name
        self.available_hours = available_hours  # e.g. ["8am-10am", "5pm-7pm"]
        self.preferences = preferences          # e.g. {"prefers_morning": True}
        self.pet: Pet | None = None

    def get_constraints(self) -> dict[str, Any]:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass


class Plan:
    def __init__(self):
        self.owner: Owner | None = None
        self.pet: Pet | None = None
        self.tasks: list[Task] = []

    def build(self, owner: Owner, pet: Pet) -> None:
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
