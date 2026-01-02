# Feature: Delete Task

## User Story
As a user, I want to permanently remove a completed or unwanted task.

## Functional Requirements
- Prompt for task ID to delete.
- Show the task details and ask for confirmation (y/n).
- On confirmation, remove task from memory.
- Display success or cancellation message.

## Acceptance Criteria
- Correct task is deleted.
- Invalid ID shows error.
- No confirmation = task remains.
- List reflects deletion immediately.