# Feature: Update Existing Task

## User Story
As a user, I want to modify the title or description of an existing task.

## Functional Requirements
- Prompt for task ID to update.
- Display current title and description.
- Prompt for new title (press Enter to keep current).
- Prompt for new description (press Enter to keep current).
- Update the task in memory and confirm changes.

## Acceptance Criteria
- Valid ID updates the correct task.
- Invalid ID shows error and returns to menu.
- User can update title only, description only, both, or neither (to cancel).