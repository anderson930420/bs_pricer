# tests/db/test_models.py
from __future__ import annotations
import dataclasses
from datetime import datetime, timezone
import pytest
from bs_pricer.db.models import PricingInputs, OptionType

def test_pricing_inputs_roundtrip() -> None:
    fixed = datetime(2026, 1, 30, 0, 0, 0, tzinfo=timezone.utc)

    inp = PricingInputs(
        asof_utc=fixed,
        S=100.0,
        K=100.0,
        T=1.0,
        sigma=0.2,
        r=0.01,
        option_type=OptionType.CALL,
        tags=("baseline",),
    )

    rec = inp.to_record()
    inp2 = PricingInputs.from_record(rec)

    assert inp2 == inp


def test_rejects_naive_datetime() -> None:
    naive = datetime(2026, 1, 30, 0, 0, 0)  # 明確 naive

    with pytest.raises(ValueError):
        PricingInputs(
            asof_utc=naive,
            S=100.0,
            K=100.0,
            T=1.0,
            sigma=0.2,
            r=0.01,
        )


def test_pricing_inputs_is_frozen() -> None:
    fixed = datetime(2026, 1, 30, 0, 0, 0, tzinfo=timezone.utc)
    inp = PricingInputs(asof_utc=fixed, S=100, K=100, T=1, sigma=0.2, r=0.01)

    with pytest.raises(dataclasses.FrozenInstanceError):
        inp.S = 200
