"""
hive_crewai_agent.py
─────────────────────────────────────────────────────────────────────
Hive Embed Bounty — Minimal CrewAI agent that mints + verifies a
Hive receipt, satisfying all eligibility requirements.

SETUP
-----
1. pip install -r requirements.txt
2. Get a FREE Groq API key at console.groq.com (no credit card needed).
   Set it as GROQ_API_KEY env var, or paste it into the script below.
3. Register once to get your referrer code:

   curl -s -X POST https://hivemorph.onrender.com/v1/bounty/register      -H "Content-Type: application/json"      -d '{
       "handle":     "@your_x_handle",
       "repo_url":   "https://github.com/you/this-repo",
       "verify_url": "https://thehiveryiq.com/verify/?id=PLACEHOLDER",
       "framework":  "crewai"
     }'

4. Paste the returned referrer_code into REFERRER_CODE below.

RUN
---
   python main.py

A Hive receipt is minted on every agent step. The receipt ID and
verify URL are printed at the end — submit that URL in your bounty
claim at https://thehiveryiq.com/bounty.
"""

import json
import os
import time
from crewai import Agent, Crew, Task
from langchain_groq import ChatGroq
from crewai_hive import mint_receipt

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Referrer code from the bounty registration response.
REFERRER_CODE = os.getenv("HIVE_REFERRER_CODE", "bountyb77b4c68")

# Free Groq API key — sign up at console.groq.com (no credit card needed).
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_REPLACE_ME")

# Groq chat model used by the CrewAI agent.
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
)

class RecordingHiveStepCallback:
    def __init__(self, tag: str):
        self.tag = tag
        self.last_receipt_id = None

    def __call__(self, step_output):
        action_type = type(step_output).__name__
        text = ""
        tool = None
        try:
            if hasattr(step_output, "tool"):
                tool = getattr(step_output, "tool", None)
            text = (
                getattr(step_output, "log", None)
                or json.dumps(getattr(step_output, "return_values", {}) or {})
                or str(step_output)
            )
        except Exception:
            text = str(step_output)

        metadata = {
            "framework": "crewai",
            "event": "agent_step",
            "action_type": action_type,
            "tool": tool,
            "output_hash": __import__("hashlib").sha256(text.encode("utf-8")).hexdigest(),
            "ts": int(time.time()),
            "tag": self.tag,
            "sdk": "crewai-hive",
        }
        rid = mint_receipt(metadata)
        if rid:
            self.last_receipt_id = rid
            print(f"[hive] receipt {rid} → https://thehiveryiq.com/verify/?id={rid}")

# ── HIVE CALLBACK ──────────────────────────────────────────��──────────────────
hive_cb = RecordingHiveStepCallback(tag=REFERRER_CODE)

# ── AGENT ─────────────────────────────────────────────────────────────────────
researcher = Agent(
    role="Research Analyst",
    goal=(
        "Research a given topic thoroughly and produce a clear, "
        "well-structured summary."
    ),
    backstory=(
        "You are a seasoned research analyst with expertise in synthesising "
        "information from diverse sources into actionable insights."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ── TASK ──────────────────────────────────────────────────────────────────────
research_task = Task(
    description=(
        "Research and summarise the current state of AI agent frameworks "
        "(LangGraph, CrewAI, AutoGen). Cover: key design philosophy, "
        "main use-cases, and notable limitations. Output as three clear "
        "paragraphs — one per framework."
    ),
    agent=researcher,
    expected_output=(
        "Three paragraphs, each covering one AI agent framework "
        "(LangGraph, CrewAI, AutoGen), its design philosophy, use-cases, "
        "and limitations."
    ),
)

# ── CREW ──────────────────────────────────────────────────────────────────────
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    step_callback=hive_cb,
    verbose=True,
)

# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Starting Hive-enabled CrewAI agent ===\n")
    result = crew.kickoff()

    print("\n=== Agent output ===")
    print(result)

    receipt_id = getattr(hive_cb, "last_receipt_id", None)
    if receipt_id:
        verify_url = f"https://thehiveryiq.com/verify/?id={receipt_id}"
        print("\n✅  Hive receipt minted!")
        print(f"    Receipt ID : {receipt_id}")
        print(f"    Verify URL : {verify_url}")
        print("\n👉  Submit this verify URL in your bounty claim at:")
        print("    https://thehiveryiq.com/bounty\n")
    else:
        print("\n⚠️  No receipt ID captured — check HiveStepCallback docs for the")
        print("   correct attribute name, or inspect hive_cb after the run.\n")
