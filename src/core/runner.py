from __future__ import annotations

import time
from typing import Callable, Optional

from src.ai.generator import generate_email_content
from src.config.settings import Settings
from src.mail.gmail_smtp import send_email


class Runner:
    """Orchestriert den Versand von N KI-generierten E-Mails im festen Intervall."""

    def __init__(
        self,
        *,
        settings: Settings,
        to_email: str,
        count: int,
        interval_seconds: int,
        on_log: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.settings = settings
        self.to_email = to_email
        self.count = count
        self.interval_seconds = interval_seconds
        self.on_log = on_log
        self._stop_requested = False

    def stop(self) -> None:
        """Fordert einen sauberen Abbruch nach der aktuellen Iteration an."""
        self._stop_requested = True
        self._log("Stop angefordert …")

    def run(self) -> None:
        """Startet den Versand-Loop."""
        self._log(f"Start: {self.count} Mails an {self.to_email}, Intervall {self.interval_seconds}s")

        for i in range(1, self.count + 1):
            if self._stop_requested:
                self._log("Abbruch: Stop-Flag gesetzt.")
                break

            try:
                self._log(f"[{i}/{self.count}] Generiere E-Mail …")
                content = generate_email_content(
                    self.settings,
                    iteration=i,
                )

                self._log(f"[{i}/{self.count}] Sende E-Mail (Subject: {content.subject})")
                send_email(
                    self.settings,
                    to_email=self.to_email,
                    content=content,
                )

                self._log(f"[{i}/{self.count}] Versand erfolgreich.")

            except Exception as e:
                self._log(f"[{i}/{self.count}] FEHLER: {e}")

            # Sleep nur, wenn noch eine weitere Iteration folgt
            if i < self.count and not self._stop_requested:
                self._log(f"Warte {self.interval_seconds}s …")
                time.sleep(self.interval_seconds)

        self._log("Runner beendet.")

    def _log(self, message: str) -> None:
        if self.on_log:
            try:
                self.on_log(message)
            except Exception:
                pass
        else:
            print(message)
