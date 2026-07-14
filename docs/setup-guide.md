# Full Setup Guide

Follow these steps in order. The whole setup takes about 20–30 minutes.

---

## Step 1 — Prerequisites

Make sure you have:
- **Python 3.8+** — `python --version` to check
- **pip** — `pip --version`
- **[VS Code](https://code.visualstudio.com/) with the [Claude Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)** *(recommended — easiest way to use this project)*
  *(alternative: Claude Code CLI via `npm install -g @anthropic-ai/claude-code`)*
- A **Freedcamp account** — [freedcamp.com](https://freedcamp.com)
  - Free plan works for basic use
  - Pro plan ($) required for **Time Tracking** (log-time command)
  - Pro plan required for **unlimited projects**

---

## Step 2 — Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/freedcamp-claude-pm.git
cd freedcamp-claude-pm
pip install -r requirements.txt
```

---

## Step 3 — Get your Freedcamp API credentials

1. Log in to Freedcamp
2. Go to **[freedcamp.com/my_apps](https://freedcamp.com/my_apps)**
3. Click **Create Application** (or use existing)
4. Copy your **API Key** and **API Secret**

Keep these safe. They give full access to your Freedcamp account.

---

## Step 4 — Find your Freedcamp User ID

Your user ID is needed for time logging. To find it:

**Option A — From the Freedcamp URL**
1. Go to your Freedcamp profile page
2. Look at the URL — it typically contains your user ID as a number

**Option B — From the API**
After setting up your `.env` (Step 5), run:
```bash
python src/fc.py projects
```
Then look at any project in the response. If you log a time entry in Freedcamp's web UI,
inspect the network request to see the `assigned_to_id` — that is your user ID.

**Option C — Contact Freedcamp support**
Ask them for your account's user ID. They respond quickly.

---

## Step 5 — Configure your `.env`

```bash
cp .env.example .env
```

Open `.env` and fill in:
```
FC_API_KEY=your_api_key_here
FC_API_SECRET=your_api_secret_here
FC_USER_ID=your_numeric_user_id_here
```

**Never commit `.env` to git.** It is in `.gitignore` by default.

---

## Step 6 — Test the connection

```bash
python src/fc.py projects
```

You should see a JSON list of all your Freedcamp projects. This confirms your API credentials
are working. You don't need to copy any IDs manually — when you ask Claude to create a new
project, it will run this command itself to look up the right group ID automatically.

If you get an error:
- Double-check your API key and secret in `.env`
- Make sure the `.env` file is in the project root (same folder as `requirements.txt`)
- Check that `python-dotenv` installed correctly: `pip install python-dotenv`

---

## Step 7 — Set up your Personal Hub project in Freedcamp

Your **Personal Hub** is the control center ~~equivalent to a "Quick Personal Todos"~~ project.
It holds your Focus list, backlog, and inbox.

**In the Freedcamp web UI:**
1. Create a new project called `Personal Hub` (or any name you prefer)
2. Inside it, create four **Task Lists**:
   - `🎯 Focus`
   - `📋 Planned / Upcoming`
   - `💤 Someday`
   - `📥 Inbox`

**Find the list IDs:**
After creating the lists, create a test task in each list, then run:
```bash
python src/fc.py lists <your_personal_hub_project_id>
```
This returns the list IDs. Copy them into `CLAUDE.md` in the Focus system section.

---

## Step 8 — Configure CLAUDE.md

Open `CLAUDE.md` and fill in:
1. **Your context section** — your schedule, clients, projects, working style
2. **Focus system list IDs** — from Step 7
3. **Project mapping tips** — shortcuts so Claude knows "client X" = project Y

The project mapping table will be filled in by Claude during your first session — you don't need to look up IDs manually.

This file is what makes Claude understand *you*. Spend 10–15 minutes on it.

---

## Step 9 — Set up memory files

Claude Code maintains persistent memory files so it remembers context between sessions.
Copy the templates from `memory-templates/` to Claude's project memory directory:

**On Mac/Linux:**
```bash
mkdir -p "~/.claude/projects/$(pwd | sed 's/\//-/g' | sed 's/://g')/memory"
cp memory-templates/* "~/.claude/projects/$(pwd | sed 's/\//-/g' | sed 's/://g')/memory/"
```

**On Windows (PowerShell):**
```powershell
$slug = (Get-Location).Path -replace '[:\\/]', '-'
$memDir = "$env:USERPROFILE\.claude\projects\$slug\memory"
New-Item -ItemType Directory -Force $memDir
Copy-Item memory-templates\* $memDir
```

Then open the copied files and fill in the templates with your information.

---

## Step 10 — Configure Claude Code permissions

In VS Code, open the command palette and search for "Claude Code: Open Settings".
Or edit `.claude/settings.local.json` directly:

```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:freedcamp.com)",
      "PowerShell(python src/fc.py tasks *)",
      "PowerShell(python src/fc.py create-task *)",
      "PowerShell(python src/fc.py comment *)",
      "PowerShell(python src/fc.py log-time *)",
      "PowerShell(python src/fc.py lists *)",
      "PowerShell(python src/fc.py get-times *)"
    ]
  }
}
```

This allows Claude to call Freedcamp automatically without prompting you for permission each time.
On Mac/Linux, replace `PowerShell` with `Bash`.

---

## Step 11 — First session

Open the project in VS Code with Claude Code. Start a new conversation and say something like:

> "Let's get started. My name is [name]. I have these projects in Freedcamp: [list them]. 
> Here's what I'm currently working on: [give a quick status]."

Claude will read `CLAUDE.md`, understand your setup, and be ready to help organize.

From that point on, just talk naturally. Updates like:
- "finished the homepage for client X"
- "new idea: build a Chrome extension for Y"
- "working on invoice for Z, got stuck on the tax calculation"
- "what should I focus on this week?"

---

## Troubleshooting

**"ERROR: FC_API_KEY and FC_API_SECRET not set"**
→ Your `.env` file is missing or in the wrong location. It must be in the project root.

**"ERROR 401: Unauthorized"**
→ Your API key or secret is incorrect. Regenerate from freedcamp.com/my_apps.

**"ERROR 400: No access to the app"** (when logging time)
→ The Time Records app is not enabled on that project. In Freedcamp: Project Settings → Apps → Enable Time Records.

**Claude doesn't remember previous sessions**
→ Memory files need to be in the right location. See Step 9. Claude reads them at session start.

**`python src/fc.py lists <id>` returns empty**
→ Lists show up only if they contain at least one task. Create a test task in each list via the Freedcamp web UI first.
