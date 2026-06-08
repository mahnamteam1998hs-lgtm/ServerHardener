from rich.console import Console


class ProgressManager:

    def __init__(self):

        self.console = Console()

        self.status = None

    def start(
        self,
        message: str,
    ):

        self.status = self.console.status(
            f"{message}..."
        )

        self.status.start()

    def stop(
        self,
        success_message: str = "",
    ):

        if self.status:

            self.status.stop()

            self.status = None

        if success_message:

            self.console.print(
                f"[green]✓ {success_message}[/green]"
            )