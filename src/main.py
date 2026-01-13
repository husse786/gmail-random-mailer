from __future__ import annotations

import argparse

from src.config.settings import load_settings
from src.core.runner import Runner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gmail SMTP Random Mailer (CLI)")

    parser.add_argument(
        "--to",
        dest="to_email",
        required=True,
        help="Empfänger-E-Mail-Adresse",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Anzahl zu sendender E-Mails",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Intervall zwischen E-Mails in Sekunden (Default aus ENV)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    settings = load_settings()

    interval = args.interval or settings.default_interval_seconds

    runner = Runner(
        settings=settings,
        to_email=args.to_email,
        count=args.count,
        interval_seconds=interval,
    )

    try:
        runner.run()
    except KeyboardInterrupt:
        runner.stop()


if __name__ == "__main__":
    main()
