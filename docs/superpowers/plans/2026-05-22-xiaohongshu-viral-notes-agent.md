# Xiaohongshu Viral Notes Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a discoverable Codex skill that collects and analyzes viral Xiaohongshu notes for the light-asset side-business knowledge-base niche and exports structured JSON.

**Architecture:** Create the skill in a staging directory under `D:\project`, because that path is writable in the current session. Keep the skill lightweight: `SKILL.md` defines triggering conditions and workflow, `references/` defines schema and track rules, and `scripts/normalize_xhs_notes.py` handles deterministic normalization and relative-heat scoring.

**Tech Stack:** Markdown, YAML, Python 3, local skill-creator scripts (`init_skill.py`, `quick_validate.py`)

---

### Task 1: Scaffold The Staging Skill Directory

**Files:**
- Create: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\SKILL.md`
- Create: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\agents\openai.yaml`
- Create: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\scripts\`
- Create: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\references\`

- [ ] **Step 1: Initialize the skill scaffold**

Run:

```powershell
python C:\Users\25147\.codex\skills\.system\skill-creator\scripts\init_skill.py xiaohongshu-viral-notes-agent --path D:\project\staging-skills --resources scripts,references --interface display_name="Xiaohongshu Viral Notes Agent" --interface short_description="Analyze viral Xiaohongshu notes for side-business niches" --interface default_prompt="Use $xiaohongshu-viral-notes-agent to collect and analyze viral Xiaohongshu notes in the light-asset side-business niche."
```

Expected: a new skill directory is created with `SKILL.md`, `agents/openai.yaml`, `scripts/`, and `references/`.

- [ ] **Step 2: Verify the scaffold exists**

Run:

```powershell
Get-ChildItem -Recurse D:\project\staging-skills\xiaohongshu-viral-notes-agent
```

Expected: `SKILL.md`, `agents\openai.yaml`, `scripts\`, and `references\` are listed.

### Task 2: Write The Skill Guidance

**Files:**
- Modify: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\SKILL.md`
- Create: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\references\output-schema.md`
- Create: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\references\track-rules.md`

- [ ] **Step 1: Replace the scaffolded SKILL.md with the approved workflow**

Write frontmatter with `name` and `description`, then add sections for scope, inputs, workflow, scoring rules, output requirements, and limitations.

- [ ] **Step 2: Add the output schema reference**

Create `references\output-schema.md` with the JSON object layout, required fields, and one concrete example payload.

- [ ] **Step 3: Add the track rules reference**

Create `references\track-rules.md` with the primary niche definition, subtracks, keyword mapping, and exclusions.

### Task 3: Implement The Normalization Script

**Files:**
- Create: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\scripts\normalize_xhs_notes.py`

- [ ] **Step 1: Write the failing help-path check**

Run:

```powershell
python D:\project\staging-skills\xiaohongshu-viral-notes-agent\scripts\normalize_xhs_notes.py --help
```

Expected before implementation: file not found.

- [ ] **Step 2: Implement the minimal script**

Create a CLI that:
- reads raw JSON from `--input`
- writes normalized JSON to `--output`
- scores notes with `relative_heat_score`
- tags each note with `subtrack`
- emits `run_meta`, `track_summary`, `notes`, `viral_patterns`, and `content_opportunities`

- [ ] **Step 3: Verify the script interface exists**

Run:

```powershell
python D:\project\staging-skills\xiaohongshu-viral-notes-agent\scripts\normalize_xhs_notes.py --help
```

Expected: help text prints with the required arguments.

### Task 4: Validate The Skill Package

**Files:**
- Validate: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\`

- [ ] **Step 1: Run the skill validator**

Run:

```powershell
python C:\Users\25147\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\project\staging-skills\xiaohongshu-viral-notes-agent
```

Expected: `Skill is valid!`

- [ ] **Step 2: Run a smoke test for the normalization script**

Create a tiny sample JSON file and run:

```powershell
python D:\project\staging-skills\xiaohongshu-viral-notes-agent\scripts\normalize_xhs_notes.py --input D:\project\staging-skills\sample-xhs-notes.json --output D:\project\staging-skills\sample-xhs-report.json
```

Expected: output JSON is created with normalized `notes` and `relative_heat_score`.

### Task 5: Promote The Skill To The Codex Skills Directory

**Files:**
- Copy: `D:\project\staging-skills\xiaohongshu-viral-notes-agent\` -> `C:\Users\25147\.codex\skills\xiaohongshu-viral-notes-agent\`

- [ ] **Step 1: Request permission to write outside the current workspace**

Ask for approval because `C:\Users\25147\.codex\skills` is outside the writable root.

- [ ] **Step 2: Copy the finished skill**

Run after approval:

```powershell
Copy-Item -Recurse -Force D:\project\staging-skills\xiaohongshu-viral-notes-agent C:\Users\25147\.codex\skills\
```

Expected: the skill appears under the Codex auto-discovery directory.

- [ ] **Step 3: Verify the copied files**

Run:

```powershell
Get-ChildItem -Recurse C:\Users\25147\.codex\skills\xiaohongshu-viral-notes-agent
```

Expected: copied files match the staging skill.
