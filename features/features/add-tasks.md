# Feature: Add New Task

## User Story
As a user, I want to add a new task with a title and description so that I can track my todos.

## Functional Requirements
- Prompt user for title (required, must not be empty).
- Prompt user for description (optional, can be empty).
- Automatically assign the next available integer ID (auto-increment).
- Create a new Task instance and append it to the in-memory storage.
- Display confirmation: "Task added successfully (ID: X)".

## Acceptance Criteria
- User can add a task with only a title.
- User can add a task with title and description.
- IDs are sequential and unique.
- New task immediately appears in the list.
- Empty title is rejected with a clear error and reprompt.