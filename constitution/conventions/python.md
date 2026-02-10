# Python Coding Conventions

This document defines the coding standards for Python projects. It extends the `_common.md` conventions and adopts **PEP 8** as the baseline, with strict enforcement of **Type Hinting** and **Google Style Docstrings**.

## 1. Base Standard & Environment
- **Base Style:** Adhere strictly to [PEP 8](https://peps.python.org/pep-0008/).
- **Target Version:** **Python 3.10+** (Utilize modern features like `match` case and Union types `|`).
- **Formatter:** Code must be formatted using **Black**.
  - Line Length: **88** (Black default) or **120** (if specified in project config).
- **Import Sorting:** Use **isort** to organize imports automatically.

## 2. Type Hinting (Strict)
- **Mandatory Typing:** All function signatures (arguments and return values) must be explicitly typed.
  - *Bad:* `def process(data):`
  - *Good:* `def process(data: dict[str, Any]) -> list[str]:`
- **No `Any`:** Avoid `Any` whenever possible. Use `TypeVar`, `Union`, or specific protocols.
- **Pydantic:** For data validation and settings management, prefer **Pydantic** models over raw dictionaries.

## 3. Docstrings & Comments
- **Style:** Use **Google Style Python Docstrings**.
- **Requirement:** All public modules, functions, classes, and methods must have a docstring.
- **Format:**
  ```python
  def fetch_user(user_id: int) -> dict:
      """Fetches user data from the database.

      Args:
          user_id (int): The unique identifier of the user.

      Returns:
          dict: A dictionary containing user attributes.

      Raises:
          UserNotFoundError: If the user_id does not exist.
      """