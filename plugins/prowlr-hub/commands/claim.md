---
name: claim
description: Create and claim a task on the war room mission board with file locking
---

# Claim a Task

Create and/or claim a task on the war room mission board. This atomically locks all specified files so no other agent can edit them.

## Instructions

If the user provides arguments, parse them as the task title. Otherwise, ask what they want to work on.

1. **Ask for task details** (if not provided):
   - Title: What are you working on?
   - Files: Which files will you edit? (comma-separated paths)
   - Priority: high, normal, or low (default: normal)

2. **Check conflicts first**: Call `check_conflicts` with the file list to verify nothing is locked

3. **Claim the task**: Call `claim_task` with:
   - `title`: The task title
   - `file_scopes`: Array of file paths
   - `description`: Brief description of the work
   - `priority`: Task priority

4. **Report the result**:
   - If successful: Show the task ID and locked files
   - If failed: Show which files are locked and by whom. Suggest alternatives.

## Example

User: `/claim Implement user authentication`

→ Ask which files they'll edit
→ Check conflicts on those files
→ Claim with title "Implement user authentication"
→ Report: "Claimed task-abc123. Locked: src/auth.py, src/middleware.py"
