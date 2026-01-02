import json
import os
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Any

# --- Model ---

@dataclass
class TodoItem:
    """Represents a single Todo item."""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    creation_date: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    priority: str = "medium"  # e.g., "high", "medium", "low"

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TodoItem to a dictionary suitable for JSON serialization."""
        data = self.__dict__.copy()
        data['creation_date'] = self.creation_date.isoformat()
        if self.due_date:
            data['due_date'] = self.due_date.isoformat()
        else:
            data['due_date'] = None
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TodoItem':
        """Creates a TodoItem from a dictionary, handling date deserialization."""
        if 'creation_date' in data and data['creation_date']:
            data['creation_date'] = datetime.fromisoformat(data['creation_date'])
        if 'due_date' in data and data['due_date']:
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        else:
            data['due_date'] = None # Ensure None is set if not present or null
        return TodoItem(**data)

# --- Manager ---

class TodoManager:
    """Manages a collection of Todo items with persistence."""

    def __init__(self, filename: str = "todos.json"):
        self.filename = filename
        self._todos: Dict[int, TodoItem] = {}
        self._next_id: int = 1
        self.load_todos()

    def load_todos(self):
        """Loads todos from a JSON file."""
        if not os.path.exists(self.filename):
            self._todos = {}
            self._next_id = 1
            return

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                loaded_todos = [TodoItem.from_dict(item_data) for item_data in data]
                
                self._todos = {todo.id: todo for todo in loaded_todos}
                if self._todos:
                    self._next_id = max(self._todos.keys()) + 1
                else:
                    self._next_id = 1
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            print(f"Warning: Could not load todos from {self.filename}. Starting fresh. Error: {e}")
            self._todos = {}
            self._next_id = 1

    def save_todos(self):
        """Saves current todos to a JSON file."""
        try:
            todos_to_save = [todo.to_dict() for todo in self._todos.values()]
            with open(self.filename, 'w') as f:
                json.dump(todos_to_save, f, indent=4)
        except IOError as e:
            print(f"Error: Could not save todos to {self.filename}. {e}")

    def add_todo(
        self,
        title: str,
        description: str = "",
        due_date: Optional[datetime] = None,
        priority: str = "medium"
    ) -> TodoItem:
        """Adds a new todo item to the manager.

        Args:
            title: The title of the todo item.
            description: An optional description for the todo item.
            due_date: An optional due date for the todo item.
            priority: The priority of the todo item (e.g., "high", "medium", "low").

        Returns:
            The newly created TodoItem.

        Raises:
            ValueError: If the title is empty or priority is invalid.
        """
        if not title:
            raise ValueError("Todo title cannot be empty.")
        if priority.lower() not in ["high", "medium", "low"]:
            raise ValueError("Priority must be 'high', 'medium', or 'low'.")

        new_todo = TodoItem(
            id=self._next_id,
            title=title,
            description=description,
            completed=False,
            creation_date=datetime.now(),
            due_date=due_date,
            priority=priority.lower()
        )
        self._todos[self._next_id] = new_todo
        self._next_id += 1
        self.save_todos()
        return new_todo

    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        """Retrieves a todo item by its ID."""
        return self._todos.get(todo_id)

    def get_all_todos(self) -> List[TodoItem]:
        """Retrieves all todo items."""
        # Sorting will be handled by the CLI based on user preference (e.g., due date)
        return list(self._todos.values())

    def update_todo(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[str] = None
    ) -> Optional[TodoItem]:
        """Updates an existing todo item."""
        todo = self.get_todo(todo_id)
        if todo:
            if title is not None:
                if not title:
                    raise ValueError("Todo title cannot be empty.")
                todo.title = title
            if description is not None:
                todo.description = description
            if completed is not None:
                todo.completed = completed
            if due_date is not None:
                todo.due_date = due_date
            if priority is not None:
                if priority.lower() not in ["high", "medium", "low"]:
                    raise ValueError("Priority must be 'high', 'medium', or 'low'.")
                todo.priority = priority.lower()
            
            self.save_todos()
            return todo
        return None

    def delete_todo(self, todo_id: int) -> bool:
        """Deletes a todo item by its ID."""
        if todo_id in self._todos:
            del self._todos[todo_id]
            self.save_todos()
            return True
        return False

    def mark_complete(self, todo_id: int) -> Optional[TodoItem]:
        """Marks a todo item as complete."""
        todo = self.get_todo(todo_id)
        if todo:
            todo.completed = True
            self.save_todos()
            return todo
        return None