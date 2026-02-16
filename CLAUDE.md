# Claude Code Configuration & Guidelines

## 1. Project Context
- **Name:** PyDooray
- **Primary Language:** python
- **Source of Truth:** All AI protocols are defined in the `speckit-core/` submodule.

## 2. Agent Commands (Persona Injection)
The following files define the personas and protocols for this project.
When asked to perform a specific role, **load the corresponding context files**.

**⚠️ IMPORTANT OVERRIDE RULE:**
If a `project_rules.md` file exists in the root, you MUST read it.
Rules defined in `project_rules.md` **take precedence** over `speckit-core` protocols.

### 🧠 @SA (Solution Architect)
- **Trigger:** `@SA`
- **Context to Load:**
  - `speckit-core/agents/solution_architect/prompt.md`
  - `project_rules.md` (if exists)
- **Role:** Analyze requirements, define technology stack, and make high-level architectural decisions.

### 📐 @TL (Tech Lead)
- **Trigger:** `@TL`
- **Context to Load:**
  - `speckit-core/agents/tech_lead/prompt.md`
  - `speckit-core/agents/tech_lead/tech_spec_template.md`
  - `project_rules.md` (if exists)
- **Role:** Create detailed Technical Specifications (Data Model, API, Internal Class Structure) based on architectural decisions.

### 💻 @SWE (Software Engineer)
- **Trigger:** `@SWE`
- **Context to Load:**
  - `speckit-core/agents/software_engineer/prompt.md`
  - `speckit-core/constitution/conventions/{LANGUAGE}.md` (Replace `{LANGUAGE}` with actual file name)
  - `project_rules.md` (if exists)
- **Role:** Implement code strictly following the provided Spec and Language Conventions. Do not invent logic not in the spec.

### 🔄 Spec Synchronizer (Sync)
- **Trigger:** `@Sync`
- **Context to Load:**
  - `speckit-core/agents/spec_synchronizer/prompt.md`
  - `project_rules.md` (if exists)
- **Role:** Read the current Code and existing Spec, then update the Spec to match the Code.

### 📝 @TW (Tech Writer)
- **Trigger:** `@TW`
- **Context to Load:**
  - `speckit-core/agents/tech_writer/prompt.md`
  - `speckit-core/agents/tech_writer/readme_template.md`
  - `speckit-core/agents/tech_writer/api_doc_template.md`
  - `project_rules.md` (if exists)
- **Role:** Write `README.md` or API documentation that is readable by Humans and parsable by Agents.

## 3. Operational Commands
Use these commands to verify the code:

- **Build:** `echo "Update this with your build command"`
- **Test:** `echo "Update this with your test command"`
- **Lint:** `echo "Update this with your lint command"`

## 4. Git Worktree & Environment Guidelines

To ensure a seamless and isolated development process, especially for PyPI package development and automated testing, follow these strictly:

### 1. Worktree Isolation & Base Point
- **Isolation**: Always use `git worktree` for new features or bug fixes to maintain a clean working directory.
- **Base Point**: Unless specified otherwise, create a new worktree based on the user's **current HEAD** to preserve the latest context.
- **Branching**: Do not modify the user's active branch directly. Create a descriptive feature branch (e.g., `feat/ai-implementation`) from the current HEAD within the worktree.

### 2. Environment Setup & Dependency Management
- **Python Version Selection**: 
    - Before creating a venv, **check the `pyproject.toml`, `setup.cfg` or `setup.py`** for the `requires-python` specification.
    - If the project requires a specific version (e.g., Python 3.11, PyPy), ensure you use the correct executable.
    - **Crucial**: If the required version is ambiguous or if multiple versions are available, **ask the user explicitly** which Python executable/version to use for the worktree.
- **Local venv**: Initialize a dedicated virtual environment (`.venv`) inside each worktree directory.
- **Dependency Installation**: After activating the `.venv`, install dependencies in the following order:
    1. `pip install --upgrade pip`
    2. `pip install -r requirements.txt` (Core dependencies)
    3. `pip install -r tests/requirements.txt` (Test-specific tools like pytest, mock, etc.)
    4. `pip install -e .` (Install the package in **Editable Mode** to ensure code changes in the worktree are immediately reflected).

### 3. Secrets & Configuration Sharing
- **Symbolic Links for Tests**: To run tests, you must access sensitive configuration files that are not committed to the repository. **Create a symbolic link** for the following file from the main repository root to the worktree root:
    - **Target File**: `tests/tokens.py`
    - **Command**: `ln -s ../[main-folder-name]/tests/tokens.py tests/tokens.py`
- **Security**: 
    - Ensure that the symlink itself is not committed.
    - Never attempt to create a physical copy of `tokens.py` within the worktree to avoid accidental commits of sensitive data.
    - If the file is missing in the main directory, explicitly ask the user for the necessary credentials before proceeding with tests.

### 4. Testing & Verification
- **Internal Execution**: Run all tests and scripts strictly within the worktree's `.venv`.
- **Validation**: Verify that the "Editable Install" is working correctly so that your logic changes are being tested, not the version in the main folder.
- **Reporting**: Only report progress or request a merge after all tests in `tests/` pass successfully within the isolated environment.

### 5. Cleanup
- Upon successful completion and commit, notify the user.
- With user approval, propose to remove the worktree (`git worktree remove`) and delete the temporary feature branch to keep the repository tidy.