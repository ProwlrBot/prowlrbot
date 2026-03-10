# Troubleshooting Guide

Common issues and solutions for ProwlrBot installation and operation.

---

## Installation Issues

### WSL: I/O Error During pip install

**Symptoms:**
- `OSError: [Errno 5] Input/output error` during `pip install`
- WSL crashes or becomes unresponsive after the error
- WSL won't start after restarting the terminal

**Cause:** pip installing a large number of packages (223+) can overwhelm the WSL virtual filesystem, especially on NTFS-mounted paths or when disk space is low.

**Fix:**

1. Restart Windows fully (not just WSL)
2. Once WSL is back:

```bash
# If WSL won't start, run in PowerShell (Admin):
wsl --shutdown
wsl -d Ubuntu    # or your distro name

# If still broken:
wsl --terminate Ubuntu
# Last resort (deletes WSL data):
# wsl --unregister Ubuntu && wsl --install Ubuntu
```

3. Clean install with a venv inside the project:

```bash
git clone https://github.com/ProwlrBot/prowlrbot.git
cd prowlrbot

# Create venv INSIDE the project directory (not elsewhere)
python3 -m venv .venv
source .venv/bin/activate

# Install in steps (reduces I/O pressure)
pip install --upgrade pip
pip install -e .            # core packages first
pip install -e ".[dev]"     # dev dependencies second
```

**Prevention:**
- Always create the venv inside the project directory (`.venv/`), not in a separate location
- This keeps the venv on the same filesystem as the project
- Avoid cross-filesystem operations in WSL (e.g., venv on Windows mount, project on Linux FS)
- Use the Linux filesystem (`/home/user/`) not Windows mounts (`/mnt/c/`)

---

### pip install fails with dependency conflicts

**Symptoms:**
- `ERROR: Cannot install prowlrbot` with version conflict messages

**Fix:**

```bash
# Create a fresh venv (don't reuse old ones)
python3 -m venv .venv --clear
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```

If a specific package conflicts, check `pyproject.toml` for version constraints and report an issue.

---

### ModuleNotFoundError: No module named 'prowlrbot'

**Symptoms:**
- `prowlr` command not found after install
- Python can't import prowlrbot

**Fix:**

```bash
# Make sure you're in the activated venv
source .venv/bin/activate
which python3    # Should show .venv/bin/python3

# Reinstall in editable mode
pip install -e .

# Verify
prowlr --version
```

---

## Runtime Issues

### Port 8088 already in use

**Symptoms:**
- `ERROR: [Errno 98] Address already in use`

**Fix:**

```bash
# Find what's using the port
lsof -i :8088    # macOS/Linux
netstat -ano | findstr :8088    # Windows

# Kill it or use a different port
prowlr app --port 8089
```

---

### Provider detection finds no providers

**Symptoms:**
- `No providers detected` on startup

**Fix:**

```bash
# Set at least one API key
prowlr env set OPENAI_API_KEY sk-your-key
# Or for Anthropic:
prowlr env set ANTHROPIC_API_KEY sk-ant-your-key

# Or run Ollama locally (auto-detected):
ollama serve
prowlr app
```

---

### MCP connection refused

**Symptoms:**
- `Connection refused` when war room tries to connect
- MCP tools not available

**Fix:**

```bash
# Check if the bridge is running
curl http://localhost:8099/healthz

# If not, start it
prowlr app    # Bridge starts automatically with the app

# For cross-machine connections, ensure:
# 1. Both machines can reach each other (Tailscale recommended)
# 2. Port 8099 is open
# 3. HMAC secret matches on both sides
```

---

### Console shows blank page

**Symptoms:**
- `http://localhost:8088` loads but shows white screen

**Fix:**

```bash
# Rebuild the console
cd console
npm ci
npm run build

# Restart the server
prowlr app
```

---

## WSL-Specific Issues

### WSL filesystem best practices

1. **Always work on the Linux filesystem** — use `/home/user/prowlrbot`, NOT `/mnt/c/Users/.../prowlrbot`
2. **Keep venvs inside the project** — `.venv/` in the repo root
3. **Don't mix Windows and Linux tools** — use Linux `git`, `python3`, `pip` inside WSL
4. **Check disk space** — `df -h /home` should show sufficient space before installing

### WSL networking for war room

The war room bridge needs network connectivity between agents. In WSL:

```bash
# Get your WSL IP
hostname -I

# The bridge listens on 0.0.0.0:8099 by default
# From Windows, access via the WSL IP
# From other machines, you may need port forwarding or Tailscale
```

---

## Getting Help

- [GitHub Issues](https://github.com/ProwlrBot/prowlrbot/issues/new?template=bug_report.yml) — bug reports
- [GitHub Discussions](https://github.com/ProwlrBot/prowlrbot/discussions) — questions
- [SECURITY.md](https://github.com/ProwlrBot/prowlrbot/blob/main/SECURITY.md) — security vulnerabilities
