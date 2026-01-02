# System Architecture – Phase I

## Components
- Task model: A simple Python class or dataclass representing a task (id, title, description, completed).
- In-memory storage: A global list or manager class holding all Task instances.
- CLI layer: Menu loop with numbered options, input handling, and display logic.
- Separation of concerns: Business logic separated from presentation.

## Data Flow
User → CLI Menu → Command Handler → Task Manager → In-memory List → Updated Display

## Constraints
- Pure Python 3.13+
- No external libraries
- PEP 8 compliant
- Error handling for invalid inputs and non-existent IDs
- Auto-incrementing integer IDs starting from 1