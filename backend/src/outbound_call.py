from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from outbound import (
    DEFAULT_AGENT_NAME,
    OutboundCallPlan,
    place_outbound_call,
)


logger = logging.getLogger("outbound-call")

BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / ".env.local")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Place an outbound practice call.")
    parser.add_argument("--phone-number", required=True, help="Number to dial.")
    parser.add_argument(
        "--learner-name",
        default="",
        help="Optional learner name to use in the opening.",
    )
    parser.add_argument(
        "--room-name",
        default="",
        help="Optional LiveKit room name. A unique one is generated if omitted.",
    )
    parser.add_argument(
        "--agent-name",
        default=DEFAULT_AGENT_NAME,
        help="LiveKit agent name to dispatch.",
    )
    parser.add_argument(
        "--call-reason",
        default="your daily practice reminder",
        help="Why the call is happening.",
    )
    parser.add_argument(
        "--opt-out-phrase",
        default="say stop calling",
        help="How the person can opt out.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    plan = OutboundCallPlan(
        phone_number=args.phone_number,
        learner_name=args.learner_name,
        agent_name=args.agent_name,
        room_name=args.room_name,
        call_reason=args.call_reason,
        opt_out_phrase=args.opt_out_phrase,
    )

    result = await place_outbound_call(plan)
    logger.info(
        "Placed outbound call: room=%s phone=%s agent=%s",
        result.get("room_name", ""),
        result.get("to_number", result.get("phone_number", "")),
        result.get("agent_name", ""),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
