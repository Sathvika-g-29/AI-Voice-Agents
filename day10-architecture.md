# Day 10 Architecture Diagram

Use this diagram in the Day 10 blog post for the Student Career Guide voice agent.

```mermaid
flowchart LR
    U[User / Caller<br/>Browser or Phone] --> LK[LiveKit Real-Time Transport]

    LK --> STT[Deepgram Nova-3<br/>Speech to Text]
    STT --> LLM[Google Gemini 3.5 Flash Lite<br/>Reasoning + Tool Selection]

    LLM --> T1[Memory Tools<br/>lookup_caller<br/>save_caller]
    LLM --> T2[Learning Tool<br/>get_learning_recommendation]
    LLM --> T3[Human Help Tool<br/>create_human_help_request]
    LLM --> T4[Outbound Call Flow]
    LLM --> T5[Specialist Handoff<br/>handoff_to_mock_interview_specialist]

    T1 --> DB1[(SQLite Memory DB)]
    T2 --> DATA[(Local Learning Dataset)]
    T3 --> DB2[(SQLite Human Help DB)]
    T4 --> OUT[Twilio Trial or SIP Outbound Call]
    T5 --> SPEC[Mock Interview Specialist Agent]

    SPEC --> LLM2[Specialist Reasoning<br/>Interview Practice + Feedback]
    LLM2 --> T5R[Return to Main Agent]
    T5R --> LLM

    LLM --> TTS[Murf Falcon TTS<br/>Voice: Anisha]
    TTS --> LK
    LK --> U

    LK --> ANA[Call Analytics Tracker]
    ANA --> ADB[(SQLite Call Analytics DB)]
    ANA --> JSON[(Safe JSON Export)]
    JSON --> DASH[Call Analytics Dashboard<br/>/call-analytics or /dashboard]

    DB2 --> HELP[Human Help Requests Page]
    DB1 --> MEM[Caller Memory Used in Conversation]
```

Caption:

> Architecture overview of the Student Career Guide voice agent. Audio flows through LiveKit, speech is transcribed by Deepgram, the LLM decides whether to answer directly or call a tool, Murf Falcon speaks the result, and local stores keep memory, analytics, and escalation data safe.
