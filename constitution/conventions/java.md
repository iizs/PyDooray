# Java Coding Conventions

This document defines the coding standards for Java projects. It extends the `_common.md` conventions and adopts the **Google Java Style Guide** as the baseline, with specific overrides and additions defined below.

## 1. Base Standard & Version
- **Base Style:** Adhere to the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html).
- **Target Version:** Use **Java 17 LTS** (or higher).
- **Modern Features:** Actively utilize modern Java features such as `Records`, `Switch Expressions`, and `Pattern Matching` where applicable.

## 2. Formatting & Structure
- **Line Length:** 120 characters (relaxed from Google's 100).
- **Indentation:** 4 spaces (Overriding Google's 2 spaces for better readability in modern IDEs).
- **Import Ordering:**
  1. Static imports
  2. `java.*`
  3. `javax.*`
  4. Third-party libraries (`org.*`, `com.*`, etc.)
  5. Internal packages (`com.nhn.*`)
- **Ordering:** Fields → Constructors → Public Methods → Private Methods.

## 3. Library & Framework Rules
### 3.1. Lombok Usage (Strict)
Lombok is allowed but restricted to prevent "Magic Code" issues.
- **Allowed:** `@Getter`, `@ToString`, `@Builder`, `@Slf4j`, `@RequiredArgsConstructor`.
- **Restricted:**
  - **`@Data`:** **Do NOT use.** It generates `equals()`, `hashCode()`, and `@Setter` implicitly, which can cause severe performance issues (especially with JPA/Hibernate). Use individual annotations instead.
  - **`@Setter`:** Minimize usage. Prefer immutable objects constructed via `@Builder`.
  - **`@AllArgsConstructor`:** Use with caution. Prefer `@Builder`.

### 3.2. Logging
- **Framework:** Use **SLF4J** interface with an implementation (Logback/Log4j2).
- **Forbidden:** NEVER use `System.out.println` or `e.printStackTrace()` in production code.
- **Format:** Use parameterized logging.
  - *Bad:* `log.info("User " + userId + " logged in.");`
  - *Good:* `log.info("User {} logged in.", userId);`

## 4. Coding Practices
### 4.1. Null Safety
- **Avoid Nulls:** Return `Optional<T>` instead of `null` for methods that may not produce a result.
- **Collections:** Return empty collections (`Collections.emptyList()`), never `null`.
- **Utils:** Use `java.util.Objects.requireNonNull()` or `com.google.common.base.Preconditions` for argument validation.

### 4.2. Exception Handling
- **Specific Catch:** Catch specific exceptions. Never catch `Exception` or `Throwable` unless acting as a global handler.
- **No Swallow:** Never leave a catch block empty. At minimum, log the error.
- **Custom Exceptions:** Create custom exceptions only when specific handling logic is required by the caller. Otherwise, use standard exceptions (`IllegalArgumentException`, `IllegalStateException`).

### 4.3. Variable Declaration
- **`var` Keyword:** Allowed for local variables **only when the type is obvious** from the right-hand side.
  - *Good:* `var users = new ArrayList<User>();`
  - *Bad:* `var result = complexService.process();` (Type is unclear)

## 5. Testing
- **Framework:** JUnit 5 (Jupiter) is the standard.
- **Assertions:** Use **AssertJ** (`assertThat(...)`) over JUnit assertions for better readability and fluent API.
- **Mocking:** Use Mockito.
- **Naming:** `MethodName_State under test_Expected behavior`
  - *Example:* `calculateTotal_WithNegativeInput_ThrowsException`