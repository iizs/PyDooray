# Common Coding Conventions

This document defines the **Universal Standards** applicable to all programming languages and file types within the project. These rules serve as the baseline; language-specific conventions override these only when explicitly stated.

## 1. File & Format Standards
- **Encoding:** All files must be saved in **UTF-8** without BOM (Byte Order Mark).
- **Line Endings:** Use **LF** (Unix-style, `\n`) for line breaks. CRLF (Windows-style) is prohibited.
- **End of File:** Every file must end with a single newline character.
- **Trailing Whitespace:** Remove all trailing whitespace from lines.
- **Indentation:**
  - Do not mix tabs and spaces.
  - Default: **Spaces** (2 or 4 spaces, depending on the language-specific convention).

## 2. Naming Principles
- **Language:** All file names, directory names, variables, functions, and classes must be in **English**.
- **Descriptive:** Names should reveal intent. Avoid generic names like `tmp`, `data`, `obj`, `item` unless the scope is extremely small (e.g., loop index).
- **Case Sensitivity:**
  - File names: Prefer `kebab-case` (e.g., `user-profile.ts`) or `snake_case` (e.g., `user_profile.py`) based on language idioms. Avoid spaces and special characters.
  - Directories: Prefer `kebab-case` or `snake_case`.

## 3. Comments & Documentation
- **Language:** **English Only.** All comments, docstrings, and in-code documentation must be written in English.
- **Focus:** Explain **Why** code exists, not **What** it does. The code itself should explain the "What".
  - *Bad:* `// Increment i by 1`
  - *Good:* `// Increment retry counter to prevent infinite loop in network request`
- **TODOs:** Use `TODO(Author): Description` format for incomplete tasks. Do not leave empty placeholders without a TODO marker.

## 4. Security & Credentials
- **Goal:** Ultimately achieve "Zero Hardcoded Secrets" in the codebase.
- **New Files & Features (Strict):**
  - **Environment Variables:** Use `${ENV_VAR}` strictly for all new configurations.
  - **No Commits:** NEVER commit real secrets in new configuration files. Use template files (e.g., `config.yaml.example`) instead.

- **Legacy Exception (Transitional Protocol):**
  We acknowledge that existing legacy code relies on committed configuration files (YAML/JSON) containing secrets.
  - **Freeze Debt:** You may maintain existing hardcoded secrets to ensure backward compatibility.
  - **No New Secrets:** Do NOT add *new* secrets to these legacy files. New secrets must follow the "New Files & Features" rule (Env Vars).
  - **Migration Opportunity:** When modifying a legacy configuration file, you are strongly encouraged (but not forced) to migrate the specific keys involved in the change to Environment Variables.
  - **Private Repo Mandatory:** Any repository containing legacy hardcoded secrets must remain **Private**.

- **Git Ignore:** Ensure `.env`, `*.key`, `*.pem`, and build artifacts are listed in `.gitignore`.

## 5. Code Quality (General)
- **DRY (Don't Repeat Yourself):** If logic is repeated 3 times, refactor it into a function or module.
- **KISS (Keep It Simple, Stupid):** Prefer simple, readable code over clever, complex one-liners.
- **YAGNI (You Aren't Gonna Need It):** Do not implement features "just in case." Implement only what is required by the current Spec.
- **Magic Numbers:** Avoid using unexplained numbers in code. Define them as named constants.
  - *Bad:* `if (status == 2)`
  - *Good:* `const STATUS_ACTIVE = 2; if (status == STATUS_ACTIVE)`