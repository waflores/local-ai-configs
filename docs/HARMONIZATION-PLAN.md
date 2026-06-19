# Harmonization Plan

## Overview

This document addresses all dissonance points identified in the project and provides a clear path to harmonization. The goal is to create a self-documenting, self-configuring environment that AI agents (even less powerful ones) can easily understand and operate within.

## Verification Status

Based on codebase analysis, the following claims have been verified:

### ✅ VERIFIED - Action Required

- **Claim #1 (Authority Block):** TRUE - Root README.md lacks `.continue` authority block
- **Claim #2 (Model Inventory):** TRUE - llama-swap/README.md needs model location note
- **Claim #4 (Model Location):** TRUE - Root README.md needs model location clarification
- **Claim #5 (Version Dates):** TRUE - llamastash references need removal from core docs
- **Claim #6 (Machine-Readable Schema):** TRUE - Root README.md needs machine-readable header

### ❌ NOT VERIFIED - Remove from Plan

- **Claim #3 (Configuration Path Dissonance):** FALSE - Both README files correctly reference `inferhost/config.yaml`. No dissonance exists.

**RECOMMENDATION:** Remove Claim #3 from the dissonance points list as it's not applicable.

### Implementation Notes

1. **Claim #1:** Add authority block to Root README.md
1. **Claim #2:** Add model location note to llama-swap/README.md
1. **Claim #4:** Add model location section to Root README.md
1. **Claim #5:** Remove llamastash references from Root README.md and .continue/README.md
1. **Claim #6:** Add machine-readable header to Root README.md

**Note:** Claim #3 should be removed as it's not applicable to the current codebase.

## Current Dissonance Points

### 1. Root README.md vs. .continue Authority

**Issue:** Root README.md is comprehensive but lacks the `.continue` authority block.

**Impact:** AI agents might not prioritize `.continue` folder.

**Resolution:** Add authority block to root README.md.

**Action:**

````markdown
## Authority

This project uses the `.continue` folder to define AI agent behavior. Agents should consult:

- `.continue/agents/` for project-specific AI agent instructions
- `.continue/config.json` for project-specific configuration
- `.continue/prompts/` for project-specific prompts

## Machine-Readable Header

```yaml
project:
  name: llama-swap + continue.dev
  core_stack:
    - continue.dev
    - llama-server
  authority:
    folder: ".continue"
    priority: "high"
````

### 2. Model Inventory Inconsistency

**Issue:** Root README.md lists 22 models with detailed tables, but llama-swap/README.md has no model inventory.

**Impact:** AI agents might expect models to be in `llama-swap/` instead of `inferhost/models/`.

**Resolution:** Add model location note to llama-swap/README.md.

**Action:**

```markdown
## Model Location

Models are stored at `/home/waflores/.lmstudio/models`.

See Root README.md for complete model inventory.
```

### 3. Configuration Path Dissonance

**Issue:** Root README.md references `llama-swap/config.yaml` (doesn't exist), while llama-swap/README.md references `inferhost/config.yaml`.

**Impact:** Confusing path references.

**Resolution:** Clarify which config file is primary.

**Action:**

```markdown
## Configuration

The primary configuration file is `llama-swap/config.yaml`.

See Root README.md for `llama-swap` configuration.
```

### 4. Model Location Dissonance

**Issue:** Root README.md lists models but doesn't specify location, while .continue/PROJECT-CONTRACT.md says models are at `/home/waflores/DevFolder/ai/local-config/inferhost/models`.

**Impact:** Inconsistent model location references.

**Resolution:** Update root README.md to clarify model location.

**Action:**

```markdown
## Model Location

Models are stored at `/home/waflores/.lmstudio/models`.
```

### 5. Version Date Inconsistency

**Issue:** Root README.md is dated 2026, while llamastash docs (from earlier) are dated 2024.

**Impact:** Outdated references to llamastash.

**Resolution:** Remove llamastash references from core docs.

**Action:**

- Remove llamastash from Root README.md
- Remove llamastash from .continue/PROJECT-CONTRACT.md
- Keep llamastash only in `other_experiments/README.md`

### 6. Missing Machine-Readable Schema

**Issue:** Root README.md has no machine-readable header, while .continue/PROJECT-CONTRACT.md has authority block.

**Impact:** Inconsistent machine-readability.

**Resolution:** Add machine-readable header to root README.md.

**Action:**

````markdown
## Machine-Readable Header

```yaml
project:
  name: llama-swap + continue.dev
  core_stack:
    - continue.dev
    - llama-server
  authority:
    folder: ".continue"
    priority: "high"
````

## Implementation Priority

1. **Immediate (High Priority):**

   - Add authority block to Root README.md
   - Add model location to Root README.md
   - Add model location to llama-swap/README.md
   - Remove llamastash references from core docs

1. **Short-term (Medium Priority):**

   - Add machine-readable header to Root README.md
   - Update configuration path references
   - Create `.continue/config.json` with project-specific configuration

1. **Long-term (Low Priority):**

   - Populate `.continue/prompts/` with project-specific prompts
   - Create `.continue/agents/` sub-agents for specific tasks
   - Add performance benchmarks to Root README.md

## Machine-Readable Authority Block

All top-level README.md files should include:

```yaml
authority:
  folder: ".continue"
  priority: "high"
  instructions:
    - "Consult .continue/agents/ for project-specific AI agent instructions."
    - "Consult .continue/config.json for project-specific configuration."
    - "Consult .continue/prompts/ for project-specific prompts."
```

## Core Stack Definition

The core stack consists of:

- **continue.dev:** IDE agent for AI-assisted development
- **llama-server:** Inference engine
- **llama-swap:** Model management tool

**Other experiments** (context-verification, nix, llamastash) are clearly demarcated and should not distract AI agents from the core stack.

## Hello World Path

For AI agents to get started immediately:

1. Consult `.continue/agents/PROJECT-CONTRACT.md`
1. Start `llama-swap` with `/home/waflores/.nix-profile/bin/llama-swap -config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml -watch-config`
1. Use `cn` to chat with models

## Success Criteria

- [ ] All top-level README.md files include authority block
- [ ] All model location references are consistent
- [ ] All configuration path references are clear
- [ ] llamastash references removed from core docs
- [ ] Machine-readable headers present in all README.md files
- [ ] AI agents can get started without reasoning capabilities
