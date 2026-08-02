from __future__ import annotations

import csv
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "project_config.json"
OUTPUT_DIR = ROOT / "data" / "generated"

COUNTRIES = ["KW", "AE", "SA", "QA", "BH", "OM", "EG", "GB", "DE", "ES"]
ACCOUNT_STATUSES = ["ACTIVE", "SUSPENDED", "CLOSED", "PENDING"]
VIP_TIERS = ["STANDARD", "SILVER", "GOLD", "PLATINUM"]
RISK_CATEGORIES = ["LOW", "MEDIUM", "HIGH"]
GAME_CATEGORIES = ["SLOTS", "TABLE", "LIVE_CASINO", "SPORTS", "ARCADE"]
PROVIDERS = ["NOVA_GAMES", "ORBIT_PLAY", "VECTOR_STUDIOS", "APEX_LIVE"]
PAYMENT_METHODS = ["VISA", "MASTERCARD", "BANK_TRANSFER", "APPLE_PAY", "WALLET"]
TRANSACTION_STATUSES = ["SUCCESS", "FAILED", "PENDING", "REVERSED"]
TRANSACTION_TYPES = ["DEPOSIT", "WITHDRAWAL"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError(f"No rows supplied for {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate_players(count: int, batch_id: str, now: datetime) -> list[dict]:
    rows = []
    for index in range(1, count + 1):
        registered = now - timedelta(days=random.randint(1, 1200), hours=random.randint(0, 23))
        updated = registered + timedelta(days=random.randint(0, max(1, (now - registered).days)))
        rows.append(
            {
                "player_id": f"PLR-{index:07d}",
                "registration_timestamp": iso(registered),
                "country_code": random.choice(COUNTRIES),
                "account_status": random.choices(
                    ACCOUNT_STATUSES, weights=[88, 5, 4, 3], k=1
                )[0],
                "vip_tier": random.choices(
                    VIP_TIERS, weights=[75, 15, 8, 2], k=1
                )[0],
                "risk_category": random.choices(
                    RISK_CATEGORIES, weights=[82, 14, 4], k=1
                )[0],
                "updated_timestamp": iso(min(updated, now)),
                "source_system": "PLAYER_SERVICE",
                "batch_id": batch_id,
            }
        )
    return rows


def generate_games(count: int, batch_id: str, now: datetime) -> list[dict]:
    rows = []
    for index in range(1, count + 1):
        launch_date = (now - timedelta(days=random.randint(30, 2500))).date()
        rows.append(
            {
                "game_id": f"GME-{index:05d}",
                "game_name": f"Game {index:05d}",
                "provider_name": random.choice(PROVIDERS),
                "game_category": random.choice(GAME_CATEGORIES),
                "launch_date": launch_date.isoformat(),
                "is_active": random.choices([True, False], weights=[94, 6], k=1)[0],
                "updated_timestamp": iso(now - timedelta(hours=random.randint(0, 240))),
                "source_system": "GAME_CATALOGUE",
                "batch_id": batch_id,
            }
        )
    return rows


def generate_payments(
    count: int,
    player_ids: list[str],
    batch_id: str,
    now: datetime,
) -> list[dict]:
    rows = []
    for _ in range(count):
        event_time = now - timedelta(
            days=random.randint(0, 14),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        ingestion_delay = timedelta(minutes=random.randint(0, 180))
        amount = round(random.uniform(5, 1500), 2)
        status = random.choices(
            TRANSACTION_STATUSES, weights=[84, 9, 5, 2], k=1
        )[0]
        rows.append(
            {
                "transaction_id": f"TXN-{uuid.uuid4().hex[:16].upper()}",
                "player_id": random.choice(player_ids),
                "transaction_type": random.choices(
                    TRANSACTION_TYPES, weights=[72, 28], k=1
                )[0],
                "amount": f"{amount:.2f}",
                "currency": "USD",
                "payment_method": random.choice(PAYMENT_METHODS),
                "transaction_status": status,
                "event_timestamp": iso(event_time),
                "ingestion_timestamp": iso(min(event_time + ingestion_delay, now)),
                "source_system": "PAYMENT_SERVICE",
                "batch_id": batch_id,
            }
        )
    return rows


def main() -> None:
    random.seed(42)
    config = load_config()
    now = utc_now()
    batch_id = now.strftime("BATCH-%Y%m%d-%H%M%S")
    date_suffix = now.strftime("%Y%m%d")

    player_count = config["batch_size"]["players"]
    game_count = config["batch_size"]["games"]
    payment_count = config["batch_size"]["payments"]

    players = generate_players(player_count, batch_id, now)
    games = generate_games(game_count, batch_id, now)
    payments = generate_payments(
        payment_count,
        [row["player_id"] for row in players],
        batch_id,
        now,
    )

    write_csv(OUTPUT_DIR / f"players_{date_suffix}.csv", players)
    write_csv(OUTPUT_DIR / f"games_{date_suffix}.csv", games)
    write_csv(
        OUTPUT_DIR / f"payment_transactions_{date_suffix}.csv",
        payments,
    )

    print("Synthetic batch created successfully.")
    print(f"Batch ID: {batch_id}")
    print(f"Players: {len(players):,}")
    print(f"Games: {len(games):,}")
    print(f"Payments: {len(payments):,}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
