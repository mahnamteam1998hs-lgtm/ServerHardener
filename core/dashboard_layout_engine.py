from core.dashboard_card import DashboardCard


class DashboardLayoutEngine:

    def __init__(self):

        self.cards = []

    def add_card(
        self,
        title,
        rules,
    ):

        self.cards.append(
            DashboardCard(
                title=title,
                rules=rules,
            )
        )

    def build(self):

        max_width = 0

        for card in self.cards:

            width = self._estimate_card_width(
                card
            )

            if width > max_width:

                max_width = width

        for card in self.cards:

            card.width = max_width

        return self.cards

    def _estimate_card_width(
            self,
            card,
    ):

        max_setting = len(card.title)

        max_current = len("Current")

        max_recommended = len("Recommended")

        for rule in card.rules:
            max_setting = max(
                max_setting,
                len(rule.name),
            )

            max_current = max(
                max_current,
                len(str(rule.current)),
            )

            max_recommended = max(
                max_recommended,
                len(str(rule.recommended)),
            )

        return (
                max_setting +
                max_current +
                max_recommended +
                20
        )