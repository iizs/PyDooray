# JSP (JavaServer Pages) Coding Conventions

This document defines the coding standards for JSP files. It acts as a **Strict Containment Policy** to prevent logic leakage into the view layer.

## 1. Core Philosophy: View Only
- **Separation of Concerns:** JSP files must **ONLY** handle presentation logic (HTML structure and data display).
- **No Business Logic:** Never perform database queries, complex calculations, or state modifications within a JSP file. All business logic must reside in Java Classes (Controllers/Services).

## 2. Syntax & Standards
### 2.1. No Scriptlets (Strict)
- **Prohibited:** The use of Java Scriptlets (`<% ... %>`, `<%! ... %>`, `<%= ... %>`) is **strictly forbidden** in new code.
- **Alternative:** Use **JSTL (JavaServer Pages Standard Tag Library)** and **EL (Expression Language)** `${...}`.
  - *Bad:* `<% if (user.isAdmin()) { %> ... <% } %>`
  - *Good:* `<c:if test="${user.admin}"> ... </c:if>`

### 2.2. Tag Libraries
- **Declaration:** Declare tag libraries at the top of the file.
- **Prefixes:** Use standard prefixes:
  - Core: `<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>`
  - Functions: `<%@ taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions" %>`
  - Formatting: `<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>`

## 3. Formatting & Structure
- **Indentation:** Follow standard HTML indentation (2 or 4 spaces, consistent with project settings).
- **Directives:** Page directives (`<%@ page ... %>`) should be the very first lines of the file.
- **Attributes:** Always quote attribute values.
  - *Bad:* `<c:if test=${condition}>`
  - *Good:* `<c:if test="${condition}">`

## 4. Security (XSS Prevention)
- **Escaping:** Never output raw user input directly.
- **Mechanism:**
  - Use `<c:out value="${var}" />` which provides default XML escaping.
  - Or use `${fn:escapeXml(var)}` inside attributes.
  - *Dangerous:* `<div>${userInput}</div>` (Vulnerable to XSS)
  - *Safe:* `<div><c:out value="${userInput}" /></div>`

## 5. JavaScript & CSS Integration
- **Externalize:** Do not write long blocks of JavaScript or CSS inside `<script>` or `<style>` tags in JSP.
- **Import:** Move them to static resources (`.js`, `.css`) and include them.
- **Data Passing:** If passing server-side data to JavaScript is necessary, use `data-*` attributes on HTML elements, then read them in JS.
  - *Avoid:* `var userId = "${userId}";` (Can break if quotes exist in data)
  - *Prefer:* `<div id="app" data-user-id="${userId}"></div>`

## 6. Legacy Protocol
- **Refactoring:** If modifying a legacy JSP full of scriptlets:
  - Do not rewrite the entire file unless authorized.
  - However, **newly added sections** must use JSTL/EL.
  - Do not mix Scriptlets and JSTL in the same block if possible.