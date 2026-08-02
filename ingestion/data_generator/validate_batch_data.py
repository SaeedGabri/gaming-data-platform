from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "generated"

ID_PATTERNS = {
    "players": re.compile(r"^PLR-\d{7}$"),
    "games": re.compile(r"^GME-\d{5}$"),
    "payment_transactions": re.compile(r"^TXN-[A-F0-9]{16}$"),
}


def load_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_unique(rows: list[dict], key: str) -> list[str]:
    seen: set[str] = set()
    errors: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        value = row.get(key, "")
        if not value:
            errors.append(f"Row {row_number}: missing {key}")
        elif value in seen:
            errors.append(f"Row {row_number}: duplicate {key}={value}")
        seen.add(value)
    return errors


def validate_payments(rows: list[dict]) -> list[str]:
    errors = validate_unique(rows, "transaction_id")
    approved_statuses = {"SUCCESS", "FAILED", "PENDING", "REVERSED"}
    approved_types = {"DEPOSIT", "WITHDRAWAL"}

    for row_number, row in enumerate(rows, start=2):
        try:
            amount = float(row["amount"])
            if amount <= 0:
                errors.append(f"Row {row_number}: amount must be positive")
        except (TypeError, ValueError):
            errors.append(f"Row {row_number}: invalid amount")

        if row.get("transaction_status") not in approved_statuses:
            errors.append(f"Row {row_number}: invalid transaction_status")

        if row.get("transaction_type") not in approved_types:
            errors.append(f"Row {row_number}: invalid transaction_type")

    return errors


def newest_file(prefix: str) -> Path:
    files = sorted(DATA_DIR.glob(f"{prefix}_*.csv"))
    if not files:
        raise FileNotFoundError(f"No files found for prefix {prefix}")
    return files[-1]


def main() -> None:
    players = load_rows(newest_file("players"))
    games = load_rows(newest_file("games"))
    payments = load_rows(newest_file("payment_transactions"))

    errors: list[str] = []
    errors += validate_unique(players, "player_id")
    errors += validate_unique(games, "game_id")
    errors += validate_payments(payments)

    known_players = {row["player_id"] for row in players}
    for row_number, row in enumerate(payments, start=2):
        if row["player_id"] not in known_players:
            errors.append(
                f"Payment row {row_number}: unknown player_id={row['player_id']}"
            )

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for error in errors[:50]:
            print(f"- {error}")
        raise SystemExit(1)

    print("Validation passed.")
    print(f"Players checked: {len(players):,}")
    print(f"Games checked: {len(games):,}")
    print(f"Payments checked: {len(payments):,}")


if __name__ == "__main__":
    main()
