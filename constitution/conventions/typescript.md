# TypeScript Coding Conventions

This document defines the coding standards for TypeScript (and JavaScript) projects. It extends the `_common.md` conventions and aligns with the **Airbnb JavaScript Style Guide** and **Prettier** defaults.

## 1. Base Standard & Environment
- **Base Style:** Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) (with TypeScript adaptations).
- **Formatter:** Code must be formatted using **Prettier**.
- **Linter:** **ESLint** is mandatory. No console warnings/errors are allowed in production builds.
- **Strict Mode:** `tsconfig.json` must have `"strict": true` enabled.

## 2. Type Safety (Strict)
- **No `any`:** The usage of `any` is **strictly prohibited**.
  - Use `unknown` if the type is truly uncertain, and perform type narrowing before use.
  - If a temporary `any` is unavoidable during migration, it must be commented with `// TODO: Fix type`.
- **Interface vs Type:**
  - Use **`interface`** for defining object shapes (extensibility).
  - Use **`type`** for unions, intersections, and primitives.
- **Explicit Returns:** Exported functions should have explicit return types for clarity and faster compilation.
- **Null Checks:** Rely on Optional Chaining (`?.`) and Nullish Coalescing (`??`) instead of verbose `&&` checks.

## 3. Modern Syntax (ES6+)
- **Variables:**
  - Use `const` by default.
  - Use `let` only when reassignment is necessary.
  - **`var` is forbidden.**
- **Functions:**
  - Prefer **Arrow Functions** (`() => {}`) for callbacks and functional components.
  - Use standard function declarations for top-level naming consistency if preferred, but be consistent.
- **Strings:** Use Template Literals (`` `...` ``) instead of string concatenation (`+`).
- **Destructuring:** Use object/array destructuring for accessing properties.
  - *Bad:* `const name = user.name;`
  - *Good:* `const { name } = user;`

## 4. Asynchronous Programming
- **Async/Await:** Prefer `async`/`await` over `.then()` chains.
- **Concurrency:** Use `Promise.all()` (or `allSettled`) when tasks do not depend on each other. Avoid "waterfall" await calls.
- **Error Handling:** Use `try-catch` blocks for async operations.
  - *Note:* Do not leave catch blocks empty. Log or rethrow the error.

## 5. File & Naming Conventions
- **File Names:**
  - General files: `kebab-case.ts` (e.g., `user-service.ts`)
  - React Components: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- **Variables/Functions:** `camelCase` (e.g., `fetchUserData`)
- **Classes/Interfaces/Types:** `PascalCase` (e.g., `UserInterface`)
- **Constants:** `UPPER_SNAKE_CASE` for global/static constants.

## 6. React/Next.js Specifics (If applicable)
- **Components:** Use **Functional Components** with Hooks. Class components are deprecated for new code.
- **Hooks:** Follow the Rules of Hooks (only call at top level). Custom hooks must start with `use`.
- **Props:** Do not pass whole objects if only specific fields are needed (prevents unnecessary re-renders).

## 7. Testing
- **Framework:** Jest or Vitest.
- **Structure:** Test files should be co-located with the source file or in a `__tests__` directory.
  - Pattern: `filename.test.ts` or `filename.spec.ts`