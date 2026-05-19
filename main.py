"""
main.py
─────────────────────────────────────────────────────────────────────
Hive Embed Bounty — Minimal CrewAI agent that mints + verifies a
Hive receipt, satisfying all eligibility requirements.

SETUP
-----
1. pip install git+https://github.com/srotzin/crewai-hive.git crewai
2. Register once to get your referrer code:

   curl -s -X POST https://hivemorph.onrender.com/v1/bounty/register      -H "Content-Type: application/json"      -d '{
       "handle":     "@your_x_handle",
       "repo_url":   "https://github.com/you/this-repo",
       "verify_url": "https://thehiveryiq.com/verify/?id=PLACEHOLDER",
       "framework":  "crewai"
     }'

3. Leave HIVE_REFERRER_CODE unchanged so bounty tracking works.
4. Set your OPENAI_API_KEY (or swap in any LLM).

RUN
---
   python main.py

A Hive receipt is minted on every agent step. The receipt ID and
verify URL are printed at the end — submit that URL in your bounty
claim at https://thehiveryiq.com/bounty.
"""

import os
from crewai import Agent, Crew, Task
from crewai_hive import HiveStepCallback  # pip install git+https://github.com/srotzin/crewai-hive.git

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Referrer code from the bounty registration response.
REFERRER_CODE = "bounty_b77b4c68"

# OpenAI key (or set OPENAI_API_KEY in your env).
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")

# ── HIVE CALLBACK ─────────────────────────────────────────────────────────────
# HiveStepCallback intercepts each CrewAI step and mints a Hive receipt.
# The tag= param is what attributes paid receipts to your referrer code.
hive_cb = HiveStepCallback(tag=REFERRER_CODE)

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
    step_callback=hive_cb,  # <── mints a Hive receipt on every step
    verbose=True,
)

# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Starting Hive-enabled CrewAI agent ===\n")
    result = crew.kickoff()

    print("\n=== Agent output ===")
    print(result)

    # The HiveStepCallback stores the last receipt ID so you can build
    # the verify URL immediately after the run.
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
