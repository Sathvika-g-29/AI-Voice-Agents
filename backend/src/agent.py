import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    room_io,
    tokenize,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from learning_data import get_learning_path
from call_analytics import init_db as init_call_analytics_db, start_call
from human_help import create_human_help_request, init_db as init_human_help_db
from outbound import build_outbound_opening_instructions, parse_job_metadata
from memory import init_db, lookup_user, save_user


logger = logging.getLogger("agent")

BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Load backend/.env.local regardless of the current working directory.
load_dotenv(BACKEND_ROOT / ".env.local")

# Initialize SQLite database
init_db()
init_human_help_db()
init_call_analytics_db()


def get_call_tracker(context: RunContext):
    try:
        userdata = context.userdata
    except ValueError:
        return None

    if isinstance(userdata, dict):
        return userdata.get("call_tracker")

    return None


SYSTEM_PROMPT = """IDENTITY

You are a friendly and supportive Student Career Guide voice agent.

You help students with:
career choices,
internships,
learning paths,
projects,
resumes,
and interview preparation.


OBJECTIVES

1. Help students understand suitable career and learning directions.
2. Suggest practical next steps for improving skills.
3. Help students create simple and realistic action plans.


MEMORY

You have access to caller memory tools.

At the beginning of a conversation, use the lookup_caller tool when you have a reliable user ID.

If the caller is already known, greet them naturally by name and use relevant saved information to make the conversation more useful.

Do not reveal private stored information unnecessarily.

When you learn new information that would be useful in future conversations, ask the caller for permission before saving it.

For example:

"Would you like me to remember that you are currently learning Python?"

Only call save_caller after the caller clearly gives permission.

If the caller says no, do not save the information.

Never claim that information was saved unless the save_caller tool successfully confirms it.


LEARNING RECOMMENDATIONS

You have access to a learning recommendation tool called get_learning_recommendation.

Use this tool when the student asks what they should learn next, asks for a learning path, or asks what skills they should study based on their current skill and career goal.

For example, if the student says:

"I know Python and I want to become an AI Engineer. What should I learn next?"

Use the get_learning_recommendation tool.

Do not invent a learning path when the tool says that the requested combination is unavailable.

If the tool cannot find a recommendation, clearly tell the student that the current learning dataset does not contain that combination.

Do not pretend that the tool returned information that it did not return.


HUMAN HELP

Some requests need a human helper instead of a pure agent answer.

Use the human-help tool when the learner is upset, overwhelmed, or asks for a teacher
or person, or when a learning-path lookup is unavailable and the caller needs follow-up.

Before sharing anything, explain that you want to send a short summary to a human helper
and ask for permission.

Only create a human-help request after the caller clearly says yes.

When you do create a request, keep the summary short and only include:

who needs help,
what happened,
what the agent already checked,
how urgent it is,
the caller's language,
and the preferred follow-up method.

Do not include passwords, OTPs, PINs, account numbers, or the full conversation.

After the request is created, give the caller a reference ID and explain that a human
will review it when available.


KNOWLEDGE

You can provide general guidance about careers, technical skills, projects, resumes, interviews, and internships.

Do not pretend to know private information about companies, job openings, salaries, or application status unless the information is provided to you or comes from a trusted source.


LANGUAGE

Match the user's language and speaking style.

If the user speaks in Telugu mixed with English, reply naturally in the same Telugu-English mix.

If the user switches to another language, respond in that language when possible.

Keep the language simple and conversational.


OUTBOUND CALLS

If this session is part of an outbound phone call, begin with the reason for the call,
say who is calling, and explain how the person can stop future calls or end the call
right away.

Do not open with a generic greeting when the session metadata shows this is an outbound call.
Keep the opening short, calm, and respectful.


GUARDRAILS

Never guarantee that a student will get a job, internship, admission, or offer.

Never claim to be a recruiter or an official representative of a company.

Never invent job openings, salaries, company policies, deadlines, or eligibility requirements.

Never make important decisions for the student.

Do not provide medical, legal, or financial advice as a professional.

If a question is outside your role or you are unsure about the answer, clearly say that you cannot reliably help with it and offer an appropriate escalation path.


ESCALATION

When a request is outside your role, say:

"That is outside what I can reliably help with. I can help you with your career or learning questions, or you can check with the appropriate professional or official source."


STYLE

Speak naturally and conversationally.

Keep sentences short and easy to understand.

Be encouraging without making unrealistic promises.

Avoid complex formatting, bullet points, emojis, or symbols because your responses will be spoken aloud.
"""


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

    @function_tool
    async def get_learning_recommendation(
        self,
        context: RunContext,
        current_skill: str,
        goal: str,
    ) -> str:
        """Get a learning path for a student's current skill and career goal.

        Use this tool when a student asks what they should learn next
        or asks for a learning path based on their current skill and goal.

        Args:
            current_skill: The main skill the student currently knows,
                such as Python, HTML, or JavaScript.

            goal: The student's target career goal,
                such as AI Engineer, Software Engineer,
                or Frontend Developer.
        """

        logger.info(
            "Looking up learning path: skill=%s, goal=%s",
            current_skill,
            goal,
        )

        learning_path = get_learning_path(
            current_skill,
            goal,
        )

        if learning_path is None:
            return (
                "I couldn't find a learning path for that combination "
                "in my current learning dataset. "
                "I don't want to invent a recommendation."
            )

        tracker = get_call_tracker(context)
        if tracker is not None:
            tracker.mark_success("learning recommendation delivered")

        return (
            f"For someone with {current_skill} skills aiming to become "
            f"a {goal}, the recommended learning path is: "
            + ", ".join(learning_path)
        )

    @function_tool
    async def lookup_caller(
        self,
        context: RunContext,
        user_id: str,
    ) -> str:
        """Look up a caller's saved information using their user ID.

        Use this tool when a reliable caller ID is available and you need
        to check whether the caller has been seen before.
        """

        logger.info("Looking up caller: %s", user_id)

        user = lookup_user(user_id)

        if user is None:
            return json.dumps(
                {
                    "found": False,
                    "message": "No saved caller information was found.",
                }
            )

        return json.dumps(
            {
                "found": True,
                "user": user,
            }
        )

    @function_tool
    async def save_caller(
        self,
        context: RunContext,
        user_id: str,
        name: str,
        language_preference: str = "",
        facts: str = "{}",
    ) -> str:
        """Save caller information after the caller has clearly given permission.

        Only use this tool after the caller has explicitly agreed to remember
        the information.

        Args:
            user_id: Unique identifier for the caller.
            name: Caller's name.
            language_preference: Preferred language.
            facts: JSON object containing useful non-sensitive facts.
        """

        logger.info("Saving caller information for: %s", user_id)

        try:
            facts_dict = json.loads(facts)
        except json.JSONDecodeError:
            return json.dumps(
                {
                    "success": False,
                    "message": "The facts must be valid JSON.",
                }
            )

        if not isinstance(facts_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "message": "The facts must be a JSON object.",
                }
            )

        save_user(
            user_id=user_id,
            name=name,
            language_preference=language_preference,
            facts=facts_dict,
        )

        return json.dumps(
            {
                "success": True,
                "message": "Caller information has been saved.",
            }
        )

    @function_tool
    async def create_human_help_request(
        self,
        context: RunContext,
        requester_name: str,
        issue: str,
        what_checked: str,
        permission_granted: bool = False,
        urgency: str = "medium",
        language: str = "",
        follow_up_method: str = "",
    ) -> str:
        """Create a short request for a human helper after the caller agrees.

        Use this when the learner is upset, wants a teacher or human, or the
        requested learning path is unavailable and a human follow-up is needed.
        Ask for permission before calling this tool.
        """

        if not permission_granted:
            return json.dumps(
                {
                    "success": False,
                    "message": "Permission is required before sharing the summary.",
                }
            )

        try:
            human_help_request = create_human_help_request(
                requester_name=requester_name,
                issue=issue,
                what_checked=what_checked,
                urgency=urgency,
                language=language,
                follow_up_method=follow_up_method,
                permission_granted=permission_granted,
            )
        except ValueError as exc:
            return json.dumps(
                {
                    "success": False,
                    "message": str(exc),
                }
            )

        tracker = get_call_tracker(context)
        if tracker is not None:
            tracker.mark_success("human help request created")

        return json.dumps(
            {
                "success": True,
                "request_id": human_help_request.request_id,
                "status": human_help_request.status,
                "summary": human_help_request.summary,
                "next_step": "A human helper will review this request when available.",
            }
        )


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    job_metadata = parse_job_metadata(getattr(ctx.job, "metadata", None))
    is_outbound_call = "phone_number" in job_metadata

    # Set up the voice AI pipeline using:
    # Deepgram STT
    # Gemini LLM
    # Murf Falcon TTS
    # LiveKit multilingual turn detection

    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
        ),
        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),
        tts=murf.TTS(
            voice="Anisha",
            locale="en-IN",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(
                min_sentence_len=2,
            ),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
        userdata={},
    )

    # Start the agent session
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    # Connect to the LiveKit room
    await ctx.connect()

    participant = await ctx.wait_for_participant()
    channel = "sip" if "SIP" in str(participant.kind).upper() else "browser"
    call_tracker = start_call(
        channel=channel,
        participant_identity=participant.identity,
        room_name=ctx.room.name,
    )
    session.userdata["call_tracker"] = call_tracker

    def finalize_call(_reason=None):
        tracker = session.userdata.get("call_tracker")
        if tracker is not None:
            tracker.finish()

    ctx.room.on("disconnected", finalize_call)

    if is_outbound_call:
        await session.generate_reply(
            instructions=build_outbound_opening_instructions(
                learner_name=job_metadata.get("learner_name", ""),
                call_reason=job_metadata.get(
                    "call_reason", "your daily practice reminder"
                ),
                opt_out_phrase=job_metadata.get("opt_out_phrase", "say stop calling"),
            )
        )


if __name__ == "__main__":
    cli.run_app(server)
