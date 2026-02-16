# Common Operational Protocols

## 1. File Operation Rules
- **Read Before Write:** Before modifying ANY file, you must read its current content to understand the context and prevent overwriting unrelated logic.
- **Atomic Writes:** When providing code, provide the **Full File Content** unless the file is massive. If using diffs/snippets, clearly indicate the location.
- **Path Awareness:** Always verify the file path relative to the project root.

## 2. Thinking Process (Chain of Thought)
Before executing a task, output a brief internal monologue inside a block:
```text
[ANALYSIS]
1. Goal: ...
2. Constraints: ...
3. Plan: ...
```

## 3. Reference Check

- **Constitution**: Check `speckit-core/constitution/global_constitution.md`.
- **Convention**: Convention: `Check speckit-core/constitution/conventions/{LANGUAGE}.md`. (Resolve `{LANGUAGE}` based on the target component's stack, e.g., 'python', 'java'.)
- **Specs**: Check files in the designated specification directory (e.g., `docs/specs/`).