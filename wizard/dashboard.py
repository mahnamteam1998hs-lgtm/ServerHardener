from core.dashboard_layout_engine import DashboardLayoutEngine
from rich.console import Console
from rich.table import Table

from core.dashboard_rule_engine import (
    DashboardRuleEngine
)


class DashboardRenderer:

    def __init__(self, server_info):

        self.info = server_info

        self.console = Console()

    def render(self):

        rules = (
            DashboardRuleEngine(
                self.info
            ).build()
        )

        layout = DashboardLayoutEngine()

        layout.add_card(
            "🛡 Security Settings",
            rules.security_rules,
        )

        layout.add_card(
            "🔄 Recovery Settings",
            rules.recovery_rules,
        )

        layout.add_card(
            "✔ Validation Settings",
            rules.validation_rules,
        )

        cards = layout.build()

        for index, card in enumerate(cards):

            self._render_card(
                card.title,
                card.rules,
                card.width,
            )

            if index < len(cards) - 1:
                self.console.print()

    def _status_icon(
        self,
        status,
    ):

        if status == "ok":
            return "🟢"

        if status == "warning":
            return "🟡"

        return "🔴"

    def _render_card(
            self,
            title,
            rules,
            width,
    ):

        table = Table()

        table.width = width

        table.add_column(
            title,
            no_wrap=True,
        )

        table.add_column(
            "Current"
        )

        table.add_column(
            "Recommended"
        )

        table.add_column(
            "Status"
        )

        first_group = True

        for rule in rules:

            if getattr(
                    rule,
                    "row_type",
                    "rule",
            ) == "group":

                if not first_group:
                    table.add_section()

                first_group = False

                table.add_row(
                    f"[bold bright_cyan]{rule.name}[/bold bright_cyan]",
                    "",
                    "",
                    "",
                )

                continue

            table.add_row(
                rule.name,
                rule.current,
                rule.recommended,
                self._status_icon(
                    rule.status
                ),
            )

        self.console.print(table)