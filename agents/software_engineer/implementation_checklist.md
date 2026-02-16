# SWE Implementation Checklist

Before declaring the task "Complete," verify your code against these points:

## 1. Spec Compliance
- [ ] **Structure:** Does the class/function structure match the "Internal Component Design" in the Spec?
- [ ] **Signatures:** Do API endpoints and method signatures match the "Interface Design"?
- [ ] **Logic:** Are all business rules and validation steps implemented?

## 2. Convention Compliance
- [ ] **Naming:** Are variables/classes named according to `conventions/{LANGUAGE}.md`? (e.g., `snake_case` vs `camelCase`)
- [ ] **Types:** Is Strict Typing applied? (No `any`, all arguments typed)
- [ ] **Formatting:** Is the code formatted (e.g., Prettier/Black style)?

## 3. Robustness & Security
- [ ] **Error Handling:** Are exceptions caught and handled gracefully? (No silent failures)
- [ ] **Secrets:** Are all API keys/passwords pulled from Environment Variables?
- [ ] **Input Validation:** Is user input validated before processing?

## 4. Documentation
- [ ] **Docstrings:** Do all public classes and functions have description comments?
- [ ] **Clarity:** Is complex logic explained with inline comments?