# Coding Standards

## Overview
Python/FastAPI backend and Next.js frontend with industry-standard formatting and linting tools, feature-based organization, and comprehensive testing.

## Code Formatting

**Tool**: Ruff (Python), Prettier (TypeScript/JavaScript)
**Key Settings**:
- Indentation: 4 spaces (Python), 2 spaces (TypeScript)
- Line length: 100 characters (Python), 80 characters (TypeScript)
- Trailing commas: multi-line only (TypeScript)
- Single quotes (TypeScript)

**Enforcement**: Pre-commit hook and CI pipeline

## Linting

**Tool**: Ruff (Python), ESLint (TypeScript)
**Base Config**: ESLint recommended with TypeScript rules
**Strictness**: Balanced - catches real issues without blocking productivity

**Key Rules**:
- Unused variables: warn
- No explicit `any`: warn
- Type hints required for all function signatures
- No `console.log` in production code

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Python variables/functions | snake_case | `get_user_by_id` |
| Python classes | PascalCase | `UserService` |
| Python constants | UPPER_SNAKE | `MAX_RETRIES` |
| TypeScript variables/functions | camelCase | `getUserById` |
| TypeScript classes/components | PascalCase | `UserProfile` |
| TypeScript constants | UPPER_SNAKE | `API_URL` |
| React hooks | camelCase with `use` | `useAuth` |
| Files (Python) | snake_case | `user_service.py` |
| Files (components) | PascalCase | `UserProfile.tsx` |
| Files (utilities) | kebab-case | `date-utils.ts` |

## File Organization

**Pattern**: Feature-based

**Structure**:
```text
src/
  backend/
    features/
      auth/
        routes/
        models/
        services/
      users/
        ...
    shared/
      middleware/
      utils/
  frontend/
    features/
      auth/
        components/
        hooks/
        api/
      dashboard/
        ...
    shared/
      components/
      utils/
  tests/
```

**Conventions**:
- Tests: Co-located `_test.py` / `.test.tsx` files, plus integration tests in `tests/`
- Types: Co-located with feature, shared types in `shared/types/`
- Index files: No barrel exports (explicit imports preferred)

## Testing Strategy

**Framework**: pytest (Python), Vitest (TypeScript)
**Coverage Target**: 80% minimum (backend), 60% minimum (frontend)

| Type | Tool | When to Use |
|------|------|-------------|
| Unit | pytest / Vitest | Individual functions and components |
| Integration | pytest / Vitest | API endpoints, module interactions |
| E2E | Playwright | Critical user flows |

**Conventions**:
- Test naming: `test_<function>_<scenario>` (Python), `describe('<component>') / it('<behavior>')` (TypeScript)
- Test structure: Arrange-Act-Assert
- Mock strategy: Mock at boundaries (external APIs, database)

## Error Handling

**Pattern**: Custom exception classes with FastAPI exception handlers

**Custom Errors**: Yes - domain-specific exceptions (e.g., `UserNotFoundError`, `InsufficientFundsError`)

**API Errors**: Standard JSON format:
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with id 123 not found",
    "details": {}
  }
}
```

## Logging

**Tool**: Standard Python logging module
**Format**: Structured JSON in production, text in development

| Level | Usage |
|-------|-------|
| error | Something failed, needs attention |
| warn | Something unexpected, but handled |
| info | Significant business events |
| debug | Detailed technical info (dev only) |

**Rules**:
- Always log: API requests (method, path, status, duration), authentication events, errors with context
- Never log: Passwords, tokens, API keys, PII
