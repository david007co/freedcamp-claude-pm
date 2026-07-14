# Freedcamp + Claude Code — Personal Project Manager

> **You talk. Claude organizes. Freedcamp reflects reality.**

This project connects [Claude Code](https://claude.ai/code) to your Freedcamp account via API.
You give casual text updates in the Claude Code chat. Claude handles all the API calls to keep
your projects and tasks organized — no manual Freedcamp maintenance required.

---

## What this gives you

- Tell Claude "finished X for client Y" → task marked done automatically
- Tell Claude "new idea: Z" → task created in the right project
- Tell Claude "what should I work on?" → Claude checks your open tasks and suggests options
- Tell Claude "done with X, took 45 min" → task closed + time logged for invoicing
- Full context preserved between sessions via memory files

---

## Prerequisites

- Python 3.8+
- [Claude Code](https://claude.ai/code) (VS Code extension or CLI)
- A [Freedcamp](https://freedcamp.com) account (Free plan works; Pro recommended for time tracking)
- Your Freedcamp API key and secret (from [freedcamp.com/my_apps](https://freedcamp.com/my_apps))

---

## Quickstart (5 steps)

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/freedcamp-claude-pm.git
cd freedcamp-claude-pm

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up credentials
cp .env.example .env
# Edit .env with your Freedcamp API key and secret

# 4. Test connection
python src/fc.py projects

# 5. Open in VS Code with Claude Code and start talking
```

See `docs/setup-guide.md` for the full step-by-step, including how to find your Freedcamp
User ID and how to set up your Personal Hub (the Focus/Inbox system).

---

## How it works

```
You:     "finished the invoice for Acme Corp"
Claude:  → finds the task in Acme project
         → marks it completed
         → adds a closing comment
         → confirms in one sentence
```

Claude reads `CLAUDE.md` at session start to understand your projects, clients, and style.
You fill in that file once with your context. Everything else is automatic.

---

## File structure

```
.
├── CLAUDE.md                  ← Claude's operational instructions (fill this in)
├── .env                       ← Your API keys (never commit this)
├── .env.example               ← Template for .env
├── requirements.txt           ← Python dependencies
├── src/
│   └── fc.py                 ← Freedcamp API CLI tool
├── docs/
│   ├── setup-guide.md        ← Full setup walkthrough
│   └── why-this-works.md     ← The psychology behind this system
└── memory-templates/
    ├── MEMORY.md             ← Copy to ~/.claude/projects/.../memory/
    ├── user_profile.md       ← Your working style (for Claude's memory)
    └── project_map.md        ← Your Freedcamp project IDs
```

---

## Research

Before building this, read `docs/why-this-works.md`. It explains the psychological principles
behind why most task management systems fail and why this one is designed differently.

---

## Credits

Built on the [Freedcamp REST API v1](https://freedcamp.com/help_/tutorials/wiki/wiki_public/view/DFaab).
Designed to work with [Claude Code](https://claude.ai/code) by Anthropic.
