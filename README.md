# Hive Embed Agent

Hive Embed Agent is a CrewAI-based research agent integrated with Hive for on-chain verification. It is designed to coordinate research workflows, validate outputs, and record verifiable on-chain receipts for completed work.

## Tech Stack

- CrewAI framework
- Groq with Llama 3.3 70B
- hive-embed-sdk

## Key Feature

The project uses `HiveStepCallback` to automate on-chain receipt minting during agent execution. This provides a verifiable record of completed steps and helps keep research outputs auditable.

## Setup

### Requirements

- Python 3.10 or later
- `pip`

### Install dependencies

```bash
pip install -r requirements.txt
```

The project dependencies include:

- `crewai==0.1.32`
- `langchain-groq`
- `crewai-hive` from GitHub

### Environment variables

Set the following environment variables before running the agent:

```bash
export GROQ_API_KEY="your_groq_api_key"
export HIVE_API_KEY="your_hive_api_key"
```

### Run

After installing dependencies and setting the environment variables, run the agent with:

```bash
python main.py
```

## Notes

- Keep secrets out of version control.
- Review the agent configuration in `main.py` if you need to adjust the model, callback behavior, or Hive integration settings.
