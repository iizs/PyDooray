# [SPEC] {Feature Name}

**Status:** {Draft | Reviewed | Approved}
**Author:** Tech Lead
**Date:** {YYYY-MM-DD}
**Target Component:** {Repo or Module Name}

## 1. Overview
> Briefly explain what this feature is and why we are building it.

## 2. Data Model (Schema & Types)
> Define the data structures (Domain Entities, DTOs, or DB Tables) required for this feature.
> **Note to SWE:** Assume these tables/entities are ALREADY created by a DBA. Do not write code to create them at runtime.

**[Example Output]**
```java
// UserRequest Record
public record UserRequest(
    @NotBlank String username,
    @Email String email
) {}

// User Entity
@Entity
@Table(name = "users")
public class User {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;
}
```

## 3. Interface Design (API / Signatures)
> Define external boundaries such as REST API Endpoints, Public Method Signatures, or Event Payloads.

### 3.1. {Endpoint / Method Name}

**[Example Output]**
* **Method:** `POST /api/v1/users`
* **Request Body:**
```json
{ "username": "user1", "email": "test@test.com" }
```
* **Response (200 OK):**
```json
{ "id": 101, "status": "PENDING" }
```
* **Error Responses:**
  * `400 Bad Request`: Invalid email format
  * `409 Conflict`: Email already exists

## 4. Internal Component Design (Class/Module Structure)
> Define the internal structure required to implement the interface. List key classes, functions, or modules.

**[Example Output]**
* **Controller:** `UserController` (Handles HTTP requests, Validation)
* **Service:** `UserService` (Contains business logic, Transaction mgmt)
    * `createUser(request)`
    * `getUserById(id)`
* **Repository:** `UserRepository` (Data Access Layer)
    * `findByEmail(email)`
* **Utils:** `PasswordHasher` (Helper class)

## 5. Business Logic & Algorithms
> Describe the core flow, validation logic, or complex algorithms step-by-step. Use Pseudo-code if necessary.

**[Example Output]**
1. **Input Validation:** Check if `email` is already registered.
2. **Logic Branch:**
    * **IF exists:** Throw `DuplicateUserException`.
    * **ELSE:**
        1. Hash password using BCrypt.
        2. Save User entity to DB.
        3. Publish `UserCreatedEvent` to Kafka.

## 5. Security & Constraints
* **Authentication/Authorization:** {e.g., Requires `ROLE_ADMIN`}
* **Secrets:** {e.g., Use `${JWT_SECRET}` from env}
* **Performance:** {e.g., Response must be under 200ms}
* **Transactions:** {e.g., Requires `@Transactional` propagation}