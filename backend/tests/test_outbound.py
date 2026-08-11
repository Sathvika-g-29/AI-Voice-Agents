from outbound import (
    OutboundCallPlan,
    build_dispatch_metadata,
    build_outbound_opening_instructions,
    build_twiml_message,
    normalize_room_name,
    parse_job_metadata,
)


def test_parse_job_metadata_ignores_bad_json() -> None:
    assert parse_job_metadata("not json") == {}


def test_parse_job_metadata_returns_strings() -> None:
    assert parse_job_metadata('{"phone_number": 123, "learner_name": "Asha"}') == {
        "phone_number": "123",
        "learner_name": "Asha",
    }


def test_build_outbound_opening_instructions_mentions_opt_out() -> None:
    text = build_outbound_opening_instructions(
        learner_name="Asha",
        call_reason="a daily practice reminder",
        opt_out_phrase="say stop calling",
    )

    assert "Asha" in text
    assert "daily practice reminder" in text
    assert "stop calling" in text


def test_build_dispatch_metadata_includes_phone_number() -> None:
    payload = build_dispatch_metadata(
        OutboundCallPlan(
            phone_number="+919999999999",
            learner_name="Asha",
        )
    )

    assert "+919999999999" in payload
    assert "Asha" in payload


def test_normalize_room_name_generates_value_when_missing() -> None:
    room_name = normalize_room_name("")

    assert room_name.startswith("day6-outbound-")


def test_build_twiml_message_wraps_opening_in_say() -> None:
    payload = build_twiml_message(
        OutboundCallPlan(
            phone_number="+919999999999",
            learner_name="Asha",
        )
    )

    assert payload.startswith("<Response>")
    assert "<Say voice=\"alice\">" in payload
    assert "Asha" in payload
