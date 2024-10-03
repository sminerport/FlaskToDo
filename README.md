# Flask To-Do List Application

This is a simple Flask-based To-Do List application that I worked on a while back, basing it off a tutorial from Digital Ocean. It allows users to create, update, and manage tasks with features like task categorization and marking tasks as completed.

## Features

- Create and manage tasks
- Task categorization by lists
- Mark tasks as completed or undo them
- User-friendly interface for productivity

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flask-todo-app.git
   cd flask-todo-app
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv-todo
   source venv-todo/bin/activate  # On Windows, use `venv-todo\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file:
   ```bash
   SECRET_KEY=your_secret_key_here
   ```

5. Set up the database:
   ```bash
   sqlite3 database.db < schema.sql
   ```

6. Run the Flask app:
   ```bash
   flask run
   ```

## License

This project is licensed under the MIT License.