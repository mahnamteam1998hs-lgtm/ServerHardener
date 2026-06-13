from dataclasses import dataclass


@dataclass
class DashboardCard:

    title: str

    rules: list

    width: int = 0