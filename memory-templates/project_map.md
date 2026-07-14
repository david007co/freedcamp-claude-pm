---
name: project-map
description: Freedcamp project IDs, list IDs, API notes, and current project states
metadata:
  type: project
---

## API technical notes

- `python src/fc.py <command>` — main tool
- Task status: 0=open, 1=completed, 2=in-progress
- Time logging: POST /times with `{project_id, assigned_to_id, date, minutes_count, link_item_id, link_app_id:"2"}`
- Time Records app must be enabled per-project (Project Settings → Apps)
- Create task lists: NOT supported by API — must do in Freedcamp web UI
- Move task to another project: NOT supported by API
- Your user ID: [FILL IN — see docs/setup-guide.md Step 4]

## Freedcamp project map

<!-- Run `python src/fc.py projects` and fill in this table -->

| ID | Project | Group | State |
|----|---------|-------|-------|
| [ID] | Personal Hub | Personal | Active |
| [ID] | [Client Project 1] | Clients | Active |
| [ID] | [Client Project 2] | Clients | Background |
| [ID] | [Personal Project] | Personal | Active |
| [ID] | [Business Idea] | Ideas | Parked |

**State definitions:**
- **Active**: Working on this now or very soon
- **Background**: Real but not this month
- **Parked**: Consciously deferred, not abandoned
- **Archive**: Done or permanently shelved

## Personal Hub list structure

<!-- Find list IDs by running: python src/fc.py lists <personal_hub_project_id> -->

- `🎯 Focus` (ID: [FILL IN]) — max 5 items, this week's commitments
- `📋 Planned / Upcoming` (ID: [FILL IN]) — next 2–4 weeks
- `💤 Someday` (ID: [FILL IN]) — no pressure, no timeline
- `📥 Inbox` (ID: [FILL IN]) — capture first, sort later

## Current Focus list

<!-- Update this each session so future sessions have context -->

1. [Task/project name] (task ID: [ID])
2. [Task/project name] (task ID: [ID])
3. [Task/project name] (task ID: [ID])

## Project context notes

<!-- Add notes about each active project that aren't obvious from the tasks -->

- **[Project 1]**: [Current situation, key context, what's next]
- **[Project 2]**: [Current situation, key context, what's next]
