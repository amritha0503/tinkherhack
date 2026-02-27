# SkillSync Backend

SkillSync is a backend implementation for a skill matching platform that connects users based on their skills and preferences. This project is built using FastAPI, SQLite, and integrates functionalities from Google Gemini AI.

## Project Structure

```
skillsync-backend
├── src
│   ├── main.py                # Entry point of the FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database setup and session management
│   ├── models                  # Data models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── skill.py           # Skill model
│   │   └── match.py           # Match model
│   ├── schemas                 # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user.py            # User schemas
│   │   ├── skill.py           # Skill schemas
│   │   └── match.py           # Match schemas
│   ├── routers                 # Route handlers
│   │   ├── __init__.py
│   │   ├── users.py           # User-related endpoints
│   │   ├── skills.py          # Skill-related endpoints
│   │   ├── matches.py         # Match-related endpoints
│   │   └── ai.py              # AI functionalities endpoints
│   ├── services                # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py     # User operations
│   │   ├── skill_service.py    # Skill operations
│   │   ├── match_service.py    # Matching logic
│   │   └── gemini_service.py   # Google Gemini AI interactions
│   ├── repositories            # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py   # User CRUD operations
│   │   ├── skill_repository.py  # Skill CRUD operations
│   │   └── match_repository.py  # Match CRUD operations
│   └── utils                   # Utility functions
│       ├── __init__.py
│       ├── auth.py            # Authentication functions
│       └── helpers.py         # Helper functions
├── tests                       # Unit tests
│   ├── __init__.py
│   ├── test_users.py          # User tests
│   ├── test_skills.py         # Skill tests
│   ├── test_matches.py        # Match tests
│   └── test_gemini.py         # AI tests
├── .env                        # Environment variables
├── .gitignore                  # Git ignore file
├── requirements.txt            # Project dependencies
├── pyproject.toml              # Project metadata
└── README.md                   # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd skillsync-backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables in the `.env` file.

## Running the Application

To start the FastAPI application, run:
```
uvicorn src.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to access the interactive API documentation.

## Testing

To run the tests, use:
```
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.