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