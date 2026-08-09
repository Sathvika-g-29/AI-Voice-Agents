import json
import logging

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
    inference,
    tokenize,
    room_io,
)
from livekit.plugins import (
    murf,
    silero,
    google,
    deepgram,
    noise_cancellation,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from memory import init_db, lookup_user, save_user

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Initialize the SQLite database
init_db()


# Change this prompt to change what your voice agent does.
#
# See README.md for example prompts (customer support, language tutor, receptionist).

SYSTEM_PROMPT = """IDENTITY
You are a friendly and supportive Student Career Guide voice agent. You help students with career choices, internships, learning paths, projects, resumes, and interview preparation.

OBJECTIVES

1. Help students understand suitable career and learning directions.
2. Suggest practical next steps for improving skills and preparing for opportunities.
3. Help students create simple and realistic action plans.

MEMORY

You have access to caller memory tools.

At the beginning of a conversation, use the lookup_caller tool when you have a reliable user ID.

If the caller is already known, greet them naturally by name and use relevant saved information to make the conversation more useful.

For example:
"Welcome back, Ramesh. Last time we talked about your Python learning. How is that going?"

Do not reveal private stored information unnecessarily.

When you learn new information that would be useful in future conversations, ask the caller for permission before saving it.

For example:
"Would you like me to remember that you are currently learning Python?"

Only call save_caller after the caller clearly gives permission.

If the caller says no, do not save the information.

Never claim that information was saved unless the save_caller tool successfully confirms it.

KNOWLEDGE
You can provide general guidance about careers, technical skills, projects, resumes, interviews, and internships. Do not pretend to know private information about companies, job openings, salaries, or application status unless the information is provided to you or comes from a trusted source.

LANGUAGE
Match the user's language and speaking style. If the user speaks in Telugu mixed with English, reply naturally in the same Telugu-English mix. If the user switches to another language, respond in that language when possible. Keep the language simple and conversational.

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
    async def lookup_caller(
        self,
        context: RunContext,
        user_id: str,
    ):
        """Look up a caller's saved information using their user ID."""

        logger.info("Looking up caller: %s", user_id)

        user = lookup_user(user_id)

        if user is None:
            return {
                "found": False,
                "message": "No saved caller information was found.",
            }

        return {
            "found": True,
            "user": user,
        }

    @function_tool
    async def save_caller(
        self,
        context: RunContext,
        user_id: str,
        name: str,
        language_preference: str = "",
        facts: str = "{}",
    ):
        """Save caller information after the caller has given permission."""

        logger.info("Saving caller information for: %s", user_id)

        try:
            facts_dict = json.loads(facts)
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": "The facts must be valid JSON.",
            }

        save_user(
            user_id=user_id,
            name=name,
            language_preference=language_preference,
            facts=facts_dict,
        )

        return {
            "success": True,
            "message": "Caller information has been saved.",
        }


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram,
    # and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text
        stt=deepgram.STT(
            model="nova-3",
        ),

        # Large Language Model
        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),

        # Text-to-speech using Murf Falcon
        tts=murf.TTS(
            voice="Anisha",
            locale="en-IN",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(
                min_sentence_len=2
            ),
            text_pacing=True,
        ),

        # Turn detection
        turn_detection=MultilingualModel(),

        # Voice activity detection
        vad=ctx.proc.userdata["vad"],

        # Allow the LLM to generate a response while waiting
        # for the end of the user's turn
        preemptive_generation=True,
    )

    # Start the session
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

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)