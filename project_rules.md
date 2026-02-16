## Project-Specific Rules

### 1. Version Compatibility (Python)
- **Constraint**: Maintain strict compatibility with **Python 3.10**.
- **Requirement**: 
  - Do not use features introduced in Python 3.11+ (e.g., `ExceptionGroup`, `typing.Self` without future imports, or new `match-case` refinements if they break 3.10).
  - Use `from __future__ import annotations` if using post-3.10 type hinting styles.
  - Ensure all new dependencies added to `pyproject.toml` or `requirements.txt` support Python 3.10.

### 2. Dependency Management (Future-Proofing)
- **Rule**: When adding or updating packages, verify that the version is compatible with the existing stack defined in Section 1.
- **Action**: If a conflict arises between a new package and Python 3.10 compatibility, prioritize 3.10 support or seek a backport library.