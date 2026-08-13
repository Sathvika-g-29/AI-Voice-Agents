# Day 5 — Tool Calling with Local Learning Data

## Overview

On Day 5 of the **10 Days of Voice Agents** challenge, I taught my Student Career Guide voice agent how to use a function tool to retrieve domain-specific learning recommendations.

Instead of relying only on the LLM's generated knowledge, the agent can call a dedicated learning-path tool when a student asks what they should learn next based on their current skill and career goal.

The project uses **Murf Falcon** for text-to-speech and **LiveKit Agents** for the voice agent pipeline.

## What I Built

The agent can now:

* Understand a student's current technical skill.
* Understand their target career goal.
* Decide when a learning-path lookup is required.
* Call the `get_learning_recommendation` function tool.
* Retrieve a learning path from a local dataset.
* Speak the result naturally through the voice interface.
* Handle unsupported skill and career combinations without inventing information.

## Architecture

```text
User speaks
     ↓
Deepgram STT
     ↓
Gemini LLM
     ↓
Agent decides whether a tool is needed
     ↓
get_learning_recommendation()
     ↓
Local Learning Dataset
     ↓
Learning Path
     ↓
Gemini generates a natural response
     ↓
Murf Falcon TTS
     ↓
User hears the response
```

## Day 5 Tool

The main tool is:

```python
get_learning_recommendation(current_skill, goal)
```

The tool accepts:

* `current_skill` — the student's current skill, such as Python.
* `goal` — the student's target career, such as AI Engineer.

For example:

```text
Current skill: Python
Career goal: AI Engineer
```

The tool returns:

```text
Python fundamentals
NumPy and Pandas
Machine Learning fundamentals
scikit-learn
Deep Learning with PyTorch
LLMs and RAG
LangChain and LangGraph
```

The agent then converts this information into a conversational spoken response.

## Data Source

For Day 5, I am using a **hand-built local dataset** rather than a live internet API.

This was an intentional choice because the challenge allows a local dataset when a suitable external data source is not available.

The dataset currently contains learning paths for selected combinations of technical skills and career goals.

The local data is stored in:

```text
src/learning_data.py
```

The agent does not pretend that this information is live or continuously updated.

## Why Use a Tool?

Without the tool, the LLM could generate a learning path entirely from its own knowledge.

With the tool, the application explicitly separates:

```text
Reasoning
    +
Domain data
```

The LLM decides when the domain data is required, while the tool retrieves the actual learning path.

This also gives the application a controlled failure path.

## Failure Handling

If the requested skill and career combination is not available in the dataset, the tool returns a safe response instead of inventing a recommendation.

Example:

```text
I couldn't find a learning path for that combination
in my current learning dataset. I don't want to invent
a recommendation.
```

This prevents the voice agent from presenting unsupported information as if it came from the application's data source.

## Example Conversation

### Successful lookup

**User:**

> I know Python and I want to become an AI Engineer. What should I learn next?

**Agent:**

> For someone with Python skills aiming to become an AI Engineer, I'd recommend starting with Python fundamentals, then NumPy and Pandas, followed by machine learning fundamentals, scikit-learn, deep learning with PyTorch, LLMs and RAG, and finally LangChain and LangGraph.

### Unsupported lookup

**User:**

> I know COBOL and I want to become a Quantum Engineer. What should I learn?

**Agent:**

> I couldn't find a learning path for that combination in my current learning dataset. I don't want to invent a recommendation.

## Tool Description

The tool description tells the LLM when it should be used:

```text
Use this tool when a student asks what they should learn next
or asks for a learning path based on their current skill and goal.
```

This is important because the model uses the tool description to determine when a function call is appropriate.

## Technologies

* Python
* LiveKit Agents
* Gemini
* Deepgram
* Murf Falcon TTS
* Silero VAD
* SQLite for persistent caller memory
* Local learning dataset

## Day 4 + Day 5 Progress

### Day 4 — Memory

The agent learned how to remember information about returning callers.

It can:

* Look up a caller.
* Store information after receiving permission.
* Remember useful career and learning facts.
* Reuse saved information in future conversations.

Memory is stored locally using SQLite.

### Day 5 — Tool Calling

The agent can now use a dedicated function tool to retrieve learning recommendations.

This moves the agent beyond simply generating responses and gives it access to application-controlled domain data.

### Day 6 â€” Outbound Calls

The agent can now place outbound practice calls instead of only waiting for inbound browser sessions.

The outbound flow includes:

* a trial-friendly Twilio path for calling a verified number
* a LiveKit SIP fallback for testing when Twilio is not configured
* a spoken opening that says who is calling, why, and how to stop future calls

The outbound helpers live in:

```text
backend/src/outbound.py
backend/src/outbound_call.py
```

### Day 7 â€” Human Help

The agent can now stop and ask for a human helper when the request needs a person.

The human-help flow includes:

* asking for permission before sharing a summary
* creating a short request with only the useful details
* storing the request locally in SQLite
* showing open requests in a small dashboard page

The dashboard lives at:

```text
frontend/app/help-requests/page.tsx
```

### Day 8 â€” Call Analytics

The agent now records call outcomes and shows a simple dashboard with live counts.

For this project, a successful call means one of two things happened:

* the student received a learning recommendation
* the agent created a human-help request after permission was granted

The analytics flow includes:

* recording every browser or SIP call outcome locally
* keeping only safe metadata in the dashboard export
* showing total calls, successful calls, and failed calls on a web page

The dashboard lives at:

```text
frontend/app/call-analytics/page.tsx
```

You can also visit the alias:

```text
http://localhost:3000/dashboard
```

## Current Limitations

The learning data is currently local and manually maintained.

It is **not live data** and does not automatically reflect changes in courses, technologies, job markets, or external learning resources.

A future version could replace or supplement the local dataset with an external API or another live data source.

The outbound call path currently depends on either Twilio trial credentials or SIP trunk details.

The human-help dashboard is local to this repo and is meant for development and demonstration.

The call analytics dashboard is also local and intentionally shows only safe, non-sensitive metadata.

## Day 5 Completion Checklist

* [x] Define a domain-specific tool
* [x] Create a local domain dataset
* [x] Write a clear tool description
* [x] Connect the tool to the voice agent
* [x] Return tool results to the LLM
* [x] Speak the result naturally
* [x] Handle unsupported requests safely
* [x] Document that the data is local
* [x] Record the Day 5 demonstration video
* [x] Publish the Day 5 LinkedIn post
* [x] Submit the LinkedIn post link through Discord

## Day 6 Completion Checklist

* [x] Add outbound call support
* [x] Trigger a real outbound call to a number you control
* [x] Open the call with who, why, and opt-out language
* [x] Record the Day 6 demonstration video
* [x] Publish the Day 6 LinkedIn post
* [x] Push the Day 6 changes to GitHub

## Day 7 Completion Checklist

* [x] Add a human-help request tool
* [x] Ask for permission before sharing a summary
* [x] Store requests locally in SQLite
* [x] Show open requests in a dashboard page
* [x] Record the Day 7 demonstration video
* [x] Publish the Day 7 LinkedIn post
* [x] Submit the Day 7 form link

## Day 8 Completion Checklist

* [x] Define what a successful call means
* [x] Record outcomes from real browser or SIP calls
* [x] Build a simple dashboard for total, successful, and failed calls
* [x] Protect caller information on the dashboard
* [x] Test the success path and verify the counts increase
* [ ] Record the Day 8 demonstration video
* [ ] Publish the Day 8 LinkedIn post
* [ ] Submit the Day 8 form link

## Challenge

This project is being built as part of **10 Days of Voice Agents** and the **Voice for Bharat** challenge.

The goal is to progressively build a practical voice agent by adding capabilities such as memory, tools, domain knowledge, and safe failure handling.
