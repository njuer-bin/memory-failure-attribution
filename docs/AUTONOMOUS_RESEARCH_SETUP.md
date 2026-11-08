# Claude Code Autonomous Research Setup

This repository includes a Claude Code operating charter, specialist subagents, and a scheduled GitHub Actions workflow. The workflow is committed but will not execute successfully until the repository owner configures Anthropic credentials and enables Actions.

## What is included

- `CLAUDE.md`: persistent project-level research rules and L1/L2/L3 permissions.
- `.claude/agents/`: literature, experimental design, skeptical review, and statistics specialists.
- `.claude/commands/research-cycle.md`: reusable manual research-cycle command.
- `.github/workflows/claude-research-cycle.yml`: daily scheduled and manual cloud execution.
- `docs/CURRENT_STATE.md`, backlog, decision log, stop conditions, experiment registry, and result ledger: durable state across sessions.

## 1. Configure credentials

In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**.

Add:
- Name: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key.

Never put the key in repository files, workflow YAML, Issues, or commits. The workflow uses the official `anthropics/claude-code-base-action` and reads the key from GitHub Actions Secrets.

## 2. Enable workflow permissions

Open **Settings → Actions → General → Workflow permissions**.

The workflow needs permission to write repository contents so Claude can commit research notes on the research branch. It does not need permission to merge pull requests or modify repository settings.

If repository policy blocks write permissions for GitHub Actions, the run will fail to push. Do not solve this by granting broad administrator permissions.

## 3. Run a first manual smoke test

Open **Actions → Claude Research Cycle → Run workflow**.
- Branch: `research/memory-filtering-protocol`
- Mode: `audit` for the first run.
- The first run should inspect the state, verify source/artifact access, and update logs. It should not launch model experiments.

After the run, inspect the workflow log and commit history. Confirm that changes are on the research branch only.

## 4. Scheduled execution

The workflow is scheduled daily at 00:00 UTC (08:00 China/Singapore time). GitHub scheduled workflows can be delayed under load. Manual dispatch is available.

The daily job is intentionally bounded by a maximum Claude turn count and a single concurrent run. It must complete one high-value task or report a blocker; it must not loop indefinitely inside one GitHub Actions job.

## 5. Change the research direction

Edit the following files directly or open a PR:
- `docs/RESEARCH_CHARTER.md` — core question and scope;
- `docs/RESEARCH_BACKLOG.md` — priorities;
- `docs/STOP_CONDITIONS.md` — stop/pivot rules.

The next run reads the updated files. Changes to the core question still require explicit human approval and should be recorded in `docs/DECISION_LOG.md`.

## 6. Modes

- `audit`: literature/artifact/data audit; default and safest.
- `experiment`: only execute experiments already registered and within the stated budget. Does not authorize new high-cost experiments.
- `review`: skeptical review of the current state, claims, and evidence.

## 7. Safety and limitations

- Scheduled execution requires an Anthropic API key and may incur API charges.
- The workflow has write access to repository contents on its target branch. Review all commits.
- It is not an autonomous human-subjects approval system. It cannot contact annotators or participants without explicit authorization.
- External web availability, API quotas, and artifact hosting may interrupt a run.
- GitHub Actions is not a durable always-on process; it runs once per schedule and exits.
- The scheduled job is not a substitute for preregistration or independent scientific review.
- Do not add raw licensed datasets or personal data to the repository.
