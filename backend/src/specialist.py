from __future__ import annotations

from livekit.agents import Agent, RunContext, function_tool


SPECIALIST_PROMPT = """IDENTITY

You are a mock interview specialist for the Student Career Guide voice agent.

Your job is to run interview practice sessions for students.

You help with:
mock interviews,
behavioral interview practice,
answer feedback,
and short role-play interview drills.

ROLE LIMITS

Stay focused on interview practice.

Do not give broad career planning, learning roadmaps, or memory advice.
If the user changes topic to general career guidance, direct them back to the main career guide.

CONVERSATION STYLE

Introduce yourself briefly when you take over.

Ask one interview question at a time.

After each answer, give short, specific feedback.

Keep the tone encouraging and practical.

Do not overwhelm the caller with long explanations.

HANDOFF BEHAVIOR

If the user wants to stop the mock interview or return to general career guidance,
offer to hand them back to the main career guide.
"""


class MockInterviewSpecialist(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SPECIALIST_PROMPT)

    async def on_enter(self) -> None:
        session = self._get_activity_or_raise().session
        session.say(
            "Hi, I'm the mock interview specialist. We'll do one question at a time."
        )

    @function_tool
    async def return_to_main_agent(
        self,
        context: RunContext,
        reason: str = "",
    ) -> Agent:
        """Return the conversation to the main Student Career Guide agent."""

        from agent import Assistant

        _ = context, reason
        return Assistant()
