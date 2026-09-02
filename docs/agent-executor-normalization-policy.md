# Moda Interact Executor Normalization Policy

## Purpose

Task YAML stores a small, stable Moda executor identifier.

Provider/runtime display names must not be written directly into task metadata.

Canonical executor values are:

```text
copilot
codex
claude
continue
```

## Normalization

Normalize runtime/provider labels before claiming a task:

```text
GitHub Copilot
GitHub Copilot Agent Mode
github-copilot
github_copilot
copilot
    -> copilot

Codex
codex
    -> codex

Claude
Claude Code
claude-code
claude_code
claude
    -> claude

Continue
continue
    -> continue
```

Case and separator differences do not create new executor identifiers.

Examples:

```yaml
# correct
executor: copilot

# incorrect
executor: github-copilot
```

```yaml
# correct
executor: claude

# incorrect
executor: claude-code
```

## Claim rule

Immediately before a claim, determine the current runtime and normalize it to
one of the canonical values above.

Write only the canonical value:

```yaml
status: in_progress
executor: <copilot|codex|claude|continue>
claimed_at: <timestamp>
attempt: <previous + 1>
```

Do not invent another executor value.

## Existing active claims

When checking whether another executor has already claimed a task, compare
executor identities after normalization.

For example:

```text
github-copilot == copilot
claude-code    == claude
```

An alias-equivalent claim is the same executor identity and must not be treated
as a competing claim.

If the current agent is already legitimately working an alias-labelled active
claim, do not interrupt the implementation merely to rewrite metadata. Normalize
the executor field the next time that task file is legitimately updated, such
as when returning it to `review`.

## Historical tasks

Do not bulk-rewrite completed historical tasks only to normalize old executor
labels. The policy applies to new claims and to task files already being updated
for legitimate workflow reasons.

## Logical agent vs executor

These are separate concepts:

```text
assigned_agent: moda_admin
executor: copilot
```

`assigned_agent` identifies Moda repository ownership.

`executor` identifies the normalized AI/runtime surface carrying out that
attempt.
