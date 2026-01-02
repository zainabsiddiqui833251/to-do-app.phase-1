import argparse
import sys
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any

# Add the parent directory of 'src' (i.e., the project root) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- ANSI Color Codes ---
class Colors:
    """Utility class for ANSI color codes."""
    HEADER = '\033[95m'  # Magenta
    OKBLUE = '\033[94m'  # Blue
    OKCYAN = '\033[96m'  # Cyan
    OKGREEN = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    FAIL = '\033[91m'  # Red
    ENDC = '\033[0m'  # Reset color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Applies a color to the given text."""
        return f"{color}{text}{Colors.ENDC}"

    @staticmethod
    def bold(text: str) -> str:
        """Makes text bold."""
        return f"{Colors.BOLD}{text}{Colors.ENDC}"
        
    @staticmethod
    def dim(text: str) -> str:
        """Makes text dim."""
        return f"{Colors.DIM}{text}{Colors.ENDC}"

    @staticmethod
    def error(text: str) -> str:
        """Formats text as an error message (red, bold)."""
        return Colors.colorize(Colors.bold(text), Colors.FAIL)

    @staticmethod
    def success(text: str) -> str:
        """Formats text as a success message (green)."""
        return Colors.colorize(text, Colors.OKGREEN)

    @staticmethod
    def warning(text: str) -> str:
        """Formats text as a warning message (yellow)."""
        return Colors.colorize(text, Colors.WARNING)

    @staticmethod
    def info(text: str) -> str:
        """Formats text as informational (blue)."""
        return Colors.colorize(text, Colors.OKBLUE)

    @staticmethod
    def highlight(text: str) -> str:
        """Formats text as highlighted (cyan)."""
        return Colors.colorize(text, Colors.OKCYAN)

    @staticmethod
    def priority_color(priority: str) -> str:
        """Returns color based on priority."""
        p_lower = priority.lower()
        if p_lower == "high":
            return Colors.FAIL # Red for high
        elif p_lower == "medium":
            return Colors.WARNING # Yellow for medium
        elif p_lower == "low":
            return Colors.DIM # Dim for low
        else:
            return Colors.ENDC # Default if priority is unknown

# --- Add src directory to Python path ---
# This is to ensure that 'from src.todo import ...' works when the script is run from the project root.
try:
    from src.todo import TodoManager, TodoItem
except ModuleNotFoundError:
    print(Colors.error("Error: Could not import TodoManager. Ensure 'src/todo.py' exists and is correctly located."))
    sys.exit(1)

# --- Helper Functions ---

def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """Parses a date string 'YYYY-MM-DD' into a datetime object."""
    if not date_str:
        return None
    try:
        # We only care about the date part for user input, time is implicitly midnight
        return datetime.combine(date.fromisoformat(date_str), datetime.min.time())
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Please use YYYY-MM-DD.")

def format_datetime(dt: Optional[datetime]) -> str:
    """Formats a datetime object into 'YYYY-MM-DD' string, or returns placeholder."""
    if dt:
        return dt.strftime("%Y-%m-%d")
    return Colors.dim("N/A") # Placeholder for no date

def format_priority(priority: str) -> str:
    """Formats priority with color."""
    return Colors.colorize(priority.capitalize(), Colors.priority_color(priority))

def display_header():
    """Displays a stylized, colorful header for the Todo App."""
    title = "TODO APP"
    tagline = "Manage your tasks efficiently."
    
    app_name_colored = Colors.colorize(Colors.bold(title), Colors.HEADER)
    tagline_colored = Colors.info(tagline)

    # Centering text in CLI
    # Estimate terminal width or use a fixed width. 80 is a common standard.
    max_width = 80
    title_padded = app_name_colored.center(max_width)
    tagline_padded = tagline_colored.center(max_width)

    separator = Colors.colorize("=" * max_width, Colors.OKCYAN)

    print(separator)
    print(title_padded)
    print(tagline_padded)
    print(separator)

# --- Command Handlers ---

def handle_add(manager: TodoManager, title: str, description: str, due_date: Optional[datetime], priority: str):
    """Handles the 'add' command."""
    try:
        new_todo = manager.add_todo(title, description, due_date=due_date, priority=priority)
        print(Colors.success(f"Successfully added todo with ID: {Colors.bold(str(new_todo.id))}."))
        print(f"  Title: {new_todo.title}")
        if new_todo.description:
            print(f"  Description: {new_todo.description}")
        print(f"  Due: {format_datetime(new_todo.due_date)}")
        print(f"  Priority: {format_priority(new_todo.priority)}")
    except ValueError as e:
        print(Colors.error(f"Error adding todo: {e}"))

def handle_view(manager: TodoManager, sort_by: str):
    """Handles the 'view' command with sorting options."""
    todos = manager.get_all_todos()
    if not todos:
        print(Colors.info("No todos found."))
        return

    # Sorting logic
    if sort_by == "creation_date":
        todos.sort(key=lambda todo: todo.creation_date)
    elif sort_by == "due_date":
        # Sort by due_date, handling None values (put None last)
        todos.sort(key=lambda todo: (todo.due_date is None, todo.due_date))
    elif sort_by == "priority":
        priority_order = {"high": 1, "medium": 2, "low": 3}
        todos.sort(key=lambda todo: priority_order.get(todo.priority, 4)) # Unknown priorities last
    elif sort_by == "status":
        todos.sort(key=lambda todo: todo.completed) # False (pending) first, then True (completed)
    elif sort_by == "title":
        todos.sort(key=lambda todo: todo.title.lower())
    elif sort_by == "id": # Default sort
        todos.sort(key=lambda todo: todo.id)
    
    print(Colors.bold(Colors.info("\n--- Your Todos ---")))
    
    # Table formatting
    max_title_len = max(len(todo.title) for todo in todos) if todos else len("Task")
    max_id_len = max(len(str(todo.id)) for todo in todos) if todos else len("ID")
    max_desc_len = max(len(todo.description) for todo in todos) if todos else len("Description")
    
    col_id_width = max(max_id_len, len("ID")) + 2
    col_status_width = len("[X]") + 2
    col_title_width = max(max_title_len, len("Task")) + 2
    col_desc_width = min(max(max_desc_len, len("Description")), 40) + 2 # Truncate description
    col_due_width = max(len("YYYY-MM-DD"), len("Due Date")) + 2
    col_created_width = max(len("YYYY-MM-DD"), len("Created On")) + 2
    col_prio_width = max(len("Priority"), 6) + 2 

    # Header
    header = (
        f"{'ID':<{col_id_width}}{'Status':<{col_status_width}}{'Task':<{col_title_width}}"
        f"{'Description':<{col_desc_width}}{'Due Date':<{col_due_width}}"
        f"{'Created On':<{col_created_width}}{'Priority':<{col_prio_width}}"
    )
    
    print(Colors.colorize(Colors.bold(header), Colors.OKCYAN))
    print(Colors.colorize("=" * len(header), Colors.OKCYAN))

    for todo in todos:
        status_str = Colors.success("[X]") if todo.completed else Colors.warning("[ ]")
        todo_id_str = Colors.highlight(str(todo.id))
        title_str = Colors.bold(todo.title)
        
        # Truncate description for display
        desc_str = todo.description
        if len(desc_str) > col_desc_width - 2:
            desc_str = desc_str[:col_desc_width - 5] + "..."

        due_date_str = format_datetime(todo.due_date)
        creation_date_str = Colors.dim(format_datetime(todo.creation_date))
        priority_str = format_priority(todo.priority)

        row = (
            f"{todo_id_str:<{col_id_width}}{status_str:<{col_status_width}}{title_str:<{col_title_width}}"
            f"{desc_str:<{col_desc_width}}{due_date_str:<{col_due_width}}"
            f"{creation_date_str:<{col_created_width}}{priority_str:<{col_prio_width}}"
        )
        print(row)
    
    print(Colors.colorize("=" * len(header), Colors.OKCYAN))

def handle_update(manager: TodoManager, todo_id: int, field: str, value: str, due_date_str: Optional[str], priority: Optional[str]):
    """Handles the 'update' command."""
    update_kwargs = {}
    try:
        if field == "completed":
            if value.lower() in ["true", "yes", "1"]:
                completed_status = True
            elif value.lower() in ["false", "no", "0"]:
                completed_status = False
            else:
                print(Colors.error("Invalid value for 'completed'. Use true/false, yes/no, or 1/0."))
                return
            update_kwargs['completed'] = completed_status
        elif field == "title":
            if not value:
                raise ValueError("Todo title cannot be empty.")
            update_kwargs['title'] = value
        elif field == "description":
            update_kwargs['description'] = value
        elif field == "due_date": # Specific handling for due_date if passed as 'field'
            update_kwargs['due_date'] = parse_datetime(value)
        elif field == "priority": # Specific handling for priority if passed as 'field'
            update_kwargs['priority'] = value
        else:
            print(Colors.error(f"Unknown field '{field}'. Use title, description, completed, due_date, or priority."))
            return
            
        # Handle optional due_date and priority if they are provided via their specific flags
        if due_date_str: # This flag is for --due-date, not 'value' if field is 'due_date'
            update_kwargs['due_date'] = parse_datetime(due_date_str)
        if priority: # This flag is for --priority, not 'value' if field is 'priority'
            update_kwargs['priority'] = priority

        updated_todo = manager.update_todo(todo_id, **update_kwargs)

        if updated_todo:
            print(Colors.success(f"Successfully updated todo ID {Colors.bold(str(todo_id))}."))
        else:
            print(Colors.error(f"Todo with ID {Colors.bold(str(todo_id))} not found."))
    except ValueError as e:
        print(Colors.error(f"Error updating todo: {e}"))
    except Exception as e:
        print(Colors.error(f"An unexpected error occurred during update: {e}"))


def handle_delete(manager: TodoManager, todo_id: int):
    """Handles the 'delete' command when an ID is provided directly."""
    if manager.delete_todo(todo_id):
        print(Colors.success(f"Successfully deleted todo ID {Colors.bold(str(todo_id))}."))
    else:
        print(Colors.error(f"Todo with ID {Colors.bold(str(todo_id))} not found."))

def handle_complete(manager: TodoManager, todo_id: int):
    """Handles the 'complete' command."""
    updated_todo = manager.mark_complete(todo_id)
    if updated_todo:
        print(Colors.success(f"Marked todo ID {Colors.bold(str(todo_id))} as complete."))
    else:
        print(Colors.error(f"Todo with ID {Colors.bold(str(todo_id))} not found."))

# --- ADDED: Search Command Handler ---
def handle_search(manager: TodoManager, todo_id: Optional[int], due_date_str: Optional[str]):
    """Handles the 'search' command."""
    todos = manager.get_all_todos()
    filtered_todos = []

    search_date = None
    if due_date_str:
        try:
            search_date = parse_datetime(due_date_str)
        except ValueError as e:
            print(Colors.error(f"Invalid date format for search: {e}"))
            return

    for todo in todos:
        match_id = True
        match_date = True

        if todo_id is not None and todo.id != todo_id:
            match_id = False
        
        if search_date and todo.due_date != search_date:
            match_date = False
        
        if match_id and match_date:
            filtered_todos.append(todo)

    if not filtered_todos:
        print(Colors.info("No todos found matching your search criteria."))
        return
    
    # Display results using the same table formatting as handle_view
    print(Colors.bold(Colors.info("\n--- Search Results ---")))
    
    max_title_len = max(len(todo.title) for todo in filtered_todos) if filtered_todos else len("Task")
    max_id_len = max(len(str(todo.id)) for todo in filtered_todos) if filtered_todos else len("ID")
    
    col_id_width = max(max_id_len, len("ID")) + 2
    col_status_width = len("[X]") + 2
    col_title_width = max(max_title_len, len("Task")) + 2
    col_due_width = max(len("YYYY-MM-DD"), len("Due Date")) + 2
    col_created_width = max(len("YYYY-MM-DD"), len("Created On")) + 2
    col_prio_width = max(len("Priority"), 6) + 2 

    header = (
        f"{{ 'ID':<{col_id_width}}}"
        f"{{ 'Status':<{col_status_width}}}"
        f"{{ 'Task':<{col_title_width}}}"
        f"{{ 'Due Date':<{col_due_width}}}"
        f"{{ 'Created On':<{col_created_width}}}"
        f"{{ 'Priority':<{col_prio_width}}}"
    )
    print(Colors.colorize(Colors.bold(header), Colors.OKCYAN))
    print(Colors.colorize("-" * len(header), Colors.OKCYAN))

    for todo in filtered_todos:
        status_str = Colors.success("[X]") if todo.completed else Colors.warning("[ ]")
        todo_id_str = Colors.highlight(str(todo.id))
        title_str = Colors.bold(todo.title)
        due_date_str = format_datetime(todo.due_date)
        creation_date_str = Colors.dim(format_datetime(todo.creation_date))
        priority_str = format_priority(todo.priority)

        row = (
            f"{{todo_id_str:<{{col_id_width}}}}"
            f"{{status_str:<{{col_status_width}}}}"
            f"{{title_str:<{{col_title_width}}}}"
            f"{{due_date_str:<{{col_due_width}}}}"
            f"{{creation_date_str:<{{col_created_width}}}}"
            f"{{priority_str:<{{col_prio_width}}}}"
        )
        print(row)
    print("------------------")


# --- Interactive Input Functions ---

def interactive_add(manager: TodoManager):
    """Handles the 'add' command interactively."""
    print(Colors.info("\n--- Add New Todo ---"))
    title = input("Enter task title: ").strip()
    if not title:
        print(Colors.error("Title cannot be empty. Aborting add operation."))
        return

    description = input("Enter task description (optional, press Enter to skip): ").strip()
    
    due_date = None
    while True:
        due_date_str = input("Enter due date (YYYY-MM-DD, optional, press Enter to skip): ").strip()
        if not due_date_str:
            break
        try:
            due_date = parse_datetime(due_date_str)
            break
        except ValueError as e:
            print(Colors.error(f"Invalid date format: {e}"))

    priority = "medium" # Default priority
    while True:
        priority_input = input("Enter priority (high, medium, low, press Enter for medium): ").strip().lower()
        if not priority_input:
            break
        if priority_input in ["high", "medium", "low"]:
            priority = priority_input
            break
        else:
            print(Colors.error("Invalid priority. Please enter 'high', 'medium', or 'low'."))
    
    try:
        new_todo = manager.add_todo(title, description, due_date=due_date, priority=priority)
        print(Colors.success(f"Successfully added todo with ID: {Colors.bold(str(new_todo.id))}."))
        print(f"  Title: {new_todo.title}")
        if new_todo.description:
            print(f"  Description: {new_todo.description}")
        print(f"  Due: {format_datetime(new_todo.due_date)}")
        print(f"  Priority: {format_priority(new_todo.priority)}")
    except ValueError as e:
        print(Colors.error(f"Error adding todo: {e}"))


def interactive_update(manager: TodoManager, todo_id: int):
    """Handles the 'update' command interactively."""
    print(Colors.info(f"\n--- Update Todo ID: {Colors.bold(str(todo_id))} ---"))
    
    todo_item = manager.get_todo(todo_id)
    if not todo_item:
        print(Colors.error(f"Todo with ID {Colors.bold(str(todo_id))} not found."))
        return

    print("Fields available for update: title, description, completed, due_date, priority")
    field_to_update = input("Enter the field you want to update: ").strip().lower()

    new_value = None
    updated_kwargs = {}

    try:
        if field_to_update == "title":
            new_value = input("Enter new title: ").strip()
            if not new_value:
                print(Colors.error("Title cannot be empty. Update aborted."))
                return
            updated_kwargs['title'] = new_value
        elif field_to_update == "description":
            new_value = input("Enter new description (press Enter to clear): ").strip()
            updated_kwargs['description'] = new_value # Allows clearing description
        elif field_to_update == "completed":
            while True:
                comp_input = input("Set to completed? (yes/no): ").strip().lower()
                if comp_input in ["yes", "y", "true", "1"]:
                    updated_kwargs['completed'] = True
                    break
                elif comp_input in ["no", "n", "false", "0"]:
                    updated_kwargs['completed'] = False
                    break
                else:
                    print(Colors.error("Invalid input. Please enter 'yes' or 'no'."))
        elif field_to_update == "due_date":
            while True:
                due_date_str = input("Enter new due date (YYYY-MM-DD, press Enter to clear): ").strip()
                if not due_date_str:
                    updated_kwargs['due_date'] = None
                    break
                try:
                    updated_kwargs['due_date'] = parse_datetime(due_date_str)
                    break
                except ValueError as e:
                    print(Colors.error(f"Invalid date format: {e}"))
        elif field_to_update == "priority":
            while True:
                priority_input = input("Enter new priority (high, medium, low): ").strip().lower()
                if priority_input in ["high", "medium", "low"]:
                    updated_kwargs['priority'] = priority_input
                    break
                else:
                    print(Colors.error("Invalid priority. Please enter 'high', 'medium', or 'low'."))
        else:
            print(Colors.error(f"Unknown field '{field_to_update}'. Please choose from: title, description, completed, due_date, priority."))
            return

        updated_todo = manager.update_todo(todo_id, **updated_kwargs)

        if updated_todo:
            print(Colors.success(f"Successfully updated todo ID {Colors.bold(str(todo_id))}."))
        else:
            # This case should ideally not be reached if get_todo() passed
            print(Colors.error(f"Todo with ID {Colors.bold(str(todo_id))} not found (unexpected error)."))

    except ValueError as e:
        print(Colors.error(f"Error during update input: {e}"))
    except Exception as e:
        print(Colors.error(f"An unexpected error occurred: {e}"))

# --- ADDED: Interactive Delete Function ---
def interactive_delete(manager: TodoManager):
    """Handles the 'delete' command interactively."""
    print(Colors.info("\n--- Delete Todo ---"))
    identifier = input("Enter the ID or title of the task to delete: ").strip()

    if not identifier:
        print(Colors.error("Input cannot be empty. Aborting delete operation."))
        return

    todo_id_to_delete = None
    
    try:
        # Try to parse as ID first
        todo_id_to_delete = int(identifier)
        if manager.delete_todo(todo_id_to_delete):
            print(Colors.success(f"Successfully deleted todo with ID {Colors.bold(str(todo_id_to_delete))}."))
        else:
            print(Colors.error(f"Todo with ID {Colors.bold(str(todo_id_to_delete))} not found."))
            
    except ValueError:
        # If not an integer, treat as a title
        found_todos = [todo for todo in manager.get_all_todos() if todo.title.lower() == identifier.lower()]

        if not found_todos:
            print(Colors.error(f"No todo found with title '{Colors.bold(identifier)}'."))
            return
        elif len(found_todos) == 1:
            todo_id_to_delete = found_todos[0].id
            if manager.delete_todo(todo_id_to_delete):
                print(Colors.success(f"Successfully deleted todo with title '{Colors.bold(identifier)}' (ID: {todo_id_to_delete})."))
        else:
            # Multiple todos found with the same title
            print(Colors.warning(f"Multiple todos found with the title '{Colors.bold(identifier)}':"))
            for i, todo in enumerate(found_todos):
                print(f"  {i+1}. ID: {Colors.highlight(str(todo.id))}, Title: {Colors.bold(todo.title)}")
            
            while True:
                choice = input("Enter the number of the todo to delete, or 'cancel' to abort: ").strip()
                if choice.lower() == 'cancel':
                    print(Colors.info("Delete operation cancelled."))
                    return
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(found_todos):
                        todo_id_to_delete = found_todos[choice_index].id
                        if manager.delete_todo(todo_id_to_delete):
                            print(Colors.success(f"Successfully deleted todo with ID {Colors.bold(str(todo_id_to_delete))}."))
                        else:
                            # Should not happen if found_todos is populated correctly
                            print(Colors.error(f"Error deleting todo with ID {Colors.bold(str(todo_id_to_delete))}. Please try again."))
                        break
                    else:
                        print(Colors.error("Invalid choice number. Please try again."))
                except ValueError:
                    print(Colors.error("Invalid input. Please enter a number or 'cancel'."))


# --- Main Application Logic ---

def display_header():
    """Displays a stylized, colorful header for the Todo App."""
    title = "TODO APP"
    tagline = "Manage your tasks efficiently."
    
    app_name_colored = Colors.colorize(Colors.bold(title), Colors.HEADER)
    tagline_colored = Colors.info(tagline)

    max_width = 80
    title_padded = app_name_colored.center(max_width)
    tagline_padded = tagline_colored.center(max_width)

    separator = Colors.colorize("=" * max_width, Colors.OKCYAN)

    print(separator)
    print(title_padded)
    print(tagline_padded)
    print(separator)

def main():
    """Main function to run the Todo CLI application interactively."""
    parser = argparse.ArgumentParser(
        description=Colors.bold(Colors.info("A professional CLI Todo application.")),
        formatter_class=argparse.RawDescriptionHelpFormatter

    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # --- Add Command ---
    parser_add = subparsers.add_parser("add", help="Add a new todo item.")
    # These arguments are now handled by interactive_add function.
    # They are kept here to provide basic help text for the command itself.
    parser_add.add_argument("title", type=str, nargs="?", default=None, help="The title of the todo item (will be prompted if not provided).")
    parser_add.add_argument("description", type=str, nargs="?", default=None, help="An optional description for the todo item (will be prompted).")
    parser_add.add_argument("--due-date", type=str, help="Due date in YYYY-MM-DD format (will be prompted).")
    parser_add.add_argument("--priority", type=str, choices=["high", "medium", "low"], default=None, help="Priority level (high, medium, low) (will be prompted).")

    # --- View Command ---
    parser_view = subparsers.add_parser("view", help="View all todo items.")
    parser_view.add_argument("--sort", type=str, 
                             choices=["id", "creation_date", "due_date", "priority", "status", "title"], 
                             default="creation_date", 
                             help="Sort order for displaying todos.")

    # --- Update Command ---
    parser_update = subparsers.add_parser("update", help="Update an existing todo item.")
    parser_update.add_argument("id", type=int, help="The ID of the todo item to update.")
    # Field and value are now handled interactively by interactive_update function.
    parser_update.add_argument("field", type=str, nargs="?", default=None, choices=["title", "description", "completed", "due_date", "priority"], help="The field to update (will be prompted).")
    parser_update.add_argument("value", type=str, nargs="?", default=None, help="The new value for the field (will be prompted).")


    # --- Delete Command ---
    parser_delete = subparsers.add_parser("delete", help="Delete a todo item.")
    # The 'id' argument is removed here as deletion will be handled interactively.

    # --- Complete Command ---
    parser_complete = subparsers.add_parser("complete", help="Mark a todo item as complete.")
    parser_complete.add_argument("id", type=int, help="The ID of the todo item to mark as complete.")

    # --- Search Command ---
    parser_search = subparsers.add_parser("search", help="Search for todo items by ID or due date.")
    parser_search.add_argument("--id", type=int, help="Filter by todo item ID.")
    parser_search.add_argument("--due-date", type=str, help="Filter by due date in YYYY-MM-DD format.")


    # Initialize manager with persistence file
    manager = TodoManager("todos.json") 
    
    display_header()

    print(Colors.info("Type 'help' for available commands or 'exit' to quit."))

    while True:
        try:
            command_line = input(Colors.highlight("\nEnter command: ")).strip()
            if not command_line:
                continue

            if command_line.lower() == "exit":
                print(Colors.success("Exiting application. Goodbye!"))
                manager.save_todos() 
                sys.exit(0)
            
            try:
                # Use a temporary list to hold parsed args, which might be incomplete for interactive commands
                # We'll then decide whether to call the interactive handler or the direct handler
                args = parser.parse_args(command_line.split())
                
                # Dispatch command to handler
                if args.command == "add":
                    # Check if essential arguments were provided for direct command, otherwise go interactive
                    if args.title is not None: # If title is provided, assume direct command
                        parsed_due_date = parse_datetime(args.due_date) if args.due_date else None
                        handle_add(manager, args.title, args.description or "", parsed_due_date, args.priority or "medium")
                    else:
                        interactive_add(manager) # Go interactive if no title was provided
                elif args.command == "view":
                    handle_view(manager, args.sort)
                elif args.command == "update":
                    # Check if ID was provided. If not, update will fail and error will be shown.
                    # If ID is provided, proceed with interactive update regardless of other args.
                    interactive_update(manager, args.id)
                elif args.command == "delete":
                    # Call the interactive delete handler
                    interactive_delete(manager)
                elif args.command == "complete":
                    handle_complete(manager, args.id)
                elif args.command == "search":
                    handle_search(manager, args.id, args.due_date)

            except SystemExit: # Ignore SystemExit from argparse (e.g., on invalid command or --help)
                pass 
            except Exception as e:
                 print(Colors.error(f"Error processing command: {e}"))

        except KeyboardInterrupt:
            print(Colors.warning("\nOperation interrupted. Exiting."))
            manager.save_todos()
            sys.exit(1)
        except Exception as e:
            print(Colors.error(f"An unhandled exception occurred: {e}"))
            manager.save_todos()
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Colors.error(f"A critical error occurred: {e}"))
        sys.exit(1)