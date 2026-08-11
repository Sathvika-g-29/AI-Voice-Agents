from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from html import escape
from urllib import error, parse, request
from typing import Any
from uuid import uuid4

from livekit import api
from livekit.protocol.sip import SIPOutboundConfig


DEFAULT_AGENT_NAME = "my-agent"
DEFAULT_OPT_OUT_PHRASE = "say stop calling"
DEFAULT_CALL_REASON = "your daily practice reminder"


@dataclass(frozen=True)
class OutboundCallPlan:
    phone_number: str
    learner_name: str = ""
    agent_name: str = DEFAULT_AGENT_NAME
    room_name: str = ""
    call_reason: str = DEFAULT_CALL_REASON
    opt_out_phrase: str = DEFAULT_OPT_OUT_PHRASE


def normalize_room_name(room_name: str | None = None) -> str:
    if room_name:
        return room_name.strip()

    return f"day6-outbound-{uuid4().hex[:8]}"


def parse_job_metadata(raw_metadata: str | None) -> dict[str, str]:
    if not raw_metadata:
        return {}

    try:
        parsed = json.loads(raw_metadata)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return {
        str(key): str(value)
        for key, value in parsed.items()
        if value is not None
    }


def build_outbound_opening_instructions(
    learner_name: str = "",
    call_reason: str = DEFAULT_CALL_REASON,
    opt_out_phrase: str = DEFAULT_OPT_OUT_PHRASE,
) -> str:
    learner_clause = f" for {learner_name}" if learner_name else ""

    return (
        "This is an outbound phone call."
        f" In the first two sentences, say that you are calling{learner_clause},"
        f" explain that this is {call_reason}, and tell the person they can"
        f" {opt_out_phrase} to stop future calls and end this call now."
        " Keep the opening brief, natural, and respectful."
    )


def build_dispatch_metadata(plan: OutboundCallPlan) -> str:
    return json.dumps(
        {
            "phone_number": plan.phone_number,
            "learner_name": plan.learner_name,
            "call_reason": plan.call_reason,
            "opt_out_phrase": plan.opt_out_phrase,
        }
    )


def get_livekit_settings() -> tuple[str, str, str]:
    try:
        url = os.environ["LIVEKIT_URL"]
        api_key = os.environ["LIVEKIT_API_KEY"]
        api_secret = os.environ["LIVEKIT_API_SECRET"]
    except KeyError as exc:
        missing = exc.args[0]
        raise RuntimeError(f"Missing required environment variable: {missing}") from exc

    return url, api_key, api_secret


def get_twilio_settings() -> tuple[str, str, str]:
    try:
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        from_number = os.environ["TWILIO_FROM_NUMBER"]
    except KeyError as exc:
        missing = exc.args[0]
        raise RuntimeError(f"Missing required environment variable: {missing}") from exc

    return account_sid, auth_token, from_number


def get_twilio_twiml_url() -> str:
    twiml_url = os.getenv("TWILIO_TWIML_URL")
    if not twiml_url:
        raise RuntimeError(
            "Set TWILIO_TWIML_URL to a public TwiML Bin or Twilio Function URL for "
            "trial calls."
        )

    return twiml_url


def build_agent_dispatch_request(plan: OutboundCallPlan) -> api.CreateAgentDispatchRequest:
    room_name = normalize_room_name(plan.room_name)
    return api.CreateAgentDispatchRequest(
        agent_name=plan.agent_name,
        room=room_name,
        metadata=build_dispatch_metadata(plan),
    )


def build_sip_participant_request(
    plan: OutboundCallPlan,
    *,
    participant_identity: str = "phone_user",
) -> api.CreateSIPParticipantRequest:
    sip_trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID") or os.getenv("LIVEKIT_SIP_TRUNK_ID")
    sip_from_number = os.getenv("SIP_FROM_NUMBER")

    request_kwargs: dict[str, Any] = {
        "sip_call_to": plan.phone_number,
        "room_name": normalize_room_name(plan.room_name),
        "participant_identity": participant_identity,
    }

    if sip_from_number:
        request_kwargs["sip_number"] = sip_from_number

    if sip_trunk_id:
        request_kwargs["sip_trunk_id"] = sip_trunk_id
    else:
        hostname = os.getenv("SIP_TRUNK_HOSTNAME")
        if not hostname:
            raise RuntimeError(
                "Set either SIP_OUTBOUND_TRUNK_ID or SIP_TRUNK_HOSTNAME before making "
                "an outbound call."
            )

        request_kwargs["trunk"] = SIPOutboundConfig(
            hostname=hostname,
            auth_username=os.getenv("SIP_AUTH_USERNAME"),
            auth_password=os.getenv("SIP_AUTH_PASSWORD"),
        )

    return api.CreateSIPParticipantRequest(**request_kwargs)


async def place_outbound_call(plan: OutboundCallPlan) -> dict[str, str]:
    if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
        return await place_twilio_trial_call(plan)

    url, api_key, api_secret = get_livekit_settings()
    dispatch_request = build_agent_dispatch_request(plan)
    sip_request = build_sip_participant_request(plan)

    async with api.LiveKitAPI(url=url, api_key=api_key, api_secret=api_secret) as lk_api:
        await lk_api.agent_dispatch.create_agent_dispatch(dispatch_request)
        await lk_api.sip.create_sip_participant(sip_request)

    return {
        "room_name": normalize_room_name(plan.room_name),
        "phone_number": plan.phone_number,
        "agent_name": plan.agent_name,
    }


def build_twiml_message(plan: OutboundCallPlan) -> str:
    intro = build_outbound_opening_instructions(
        learner_name=plan.learner_name,
        call_reason=plan.call_reason,
        opt_out_phrase=plan.opt_out_phrase,
    )
    return (
        "<Response>"
        f"<Say voice=\"alice\">{escape(intro)}</Say>"
        "<Pause length=\"2\"/>"
        "<Say voice=\"alice\">Thanks for listening. "
        "This was a quick practice call.</Say>"
        "</Response>"
    )


async def place_twilio_trial_call(plan: OutboundCallPlan) -> dict[str, str]:
    account_sid, auth_token, from_number = get_twilio_settings()
    twiml_url = get_twilio_twiml_url()
    to_number = plan.phone_number

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    payload = parse.urlencode(
        {
            "To": to_number,
            "From": from_number,
            "Url": twiml_url,
        }
    ).encode("utf-8")

    auth_bytes = f"{account_sid}:{auth_token}".encode("utf-8")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")

    req = request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Basic {auth_header}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Twilio rejected the call request ({exc.code} {exc.reason}): {error_body}"
        ) from exc

    return {
        "twilio_response": body,
        "to_number": to_number,
        "from_number": from_number,
        "room_name": normalize_room_name(plan.room_name),
        "agent_name": plan.agent_name,
    }
