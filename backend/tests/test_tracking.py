"""Order tracking shows progress without exposing the recipient's phone or address."""

import json

from kapruka_agent.agent.tools import build_tools

TRACK_RESULT = {
    "order_number": "VIMP34456CB2",
    "status": "shipped",
    "status_display": "Out for delivery",
    "order_date": "24 Oct 2026",
    "delivery_date": "25 Oct 2026",
    "recipient": {
        "name": "Kamala Perera",
        "phone": "0771234567",
        "address": "12 Temple Road",
        "city": "Kandy",
    },
    "progress": [
        {"step": "Order received", "timestamp": "24 Oct 10:02"},
        {"step": "Out for delivery", "timestamp": "25 Oct 08:15"},
    ],
    "items": [{"product_id": "CAKE1", "name": "Floral Fantasy Cake", "quantity": 1}],
    "has_delivery_photo": False,
}


def _call(args: dict) -> dict:
    return {"name": "track_order", "args": args, "id": "call_1", "type": "tool_call"}


def _track_tool(kapruka):
    return next(t for t in build_tools(kapruka) if t.name == "track_order")


async def test_tracking_shows_status_and_hides_private_details(fake_kapruka):
    fake_kapruka.answers["kapruka_track_order"] = TRACK_RESULT

    message = await _track_tool(fake_kapruka).ainvoke(_call({"order_number": "VIMP34456CB2"}))

    summary = json.loads(message.content)
    assert summary["status"] == "Out for delivery"
    assert summary["latest_step"] == "Out for delivery"
    shown = json.dumps(message.artifact)
    assert "Kandy" in shown
    assert "0771234567" not in shown and "Temple Road" not in shown


async def test_pre_payment_reference_is_explained_not_looked_up(fake_kapruka):
    message = await _track_tool(fake_kapruka).ainvoke(_call({"order_number": "ORD-20261025-0001"}))

    assert "pre-payment reference" in message.content
    assert fake_kapruka.calls == []
