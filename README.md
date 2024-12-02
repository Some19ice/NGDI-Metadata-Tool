# NGDI Metadata Tool

A Django-based tool for managing NGDI metadata.

## Prerequisites

- Python 3.x
- pip (Python package installer)
- Virtual environment (recommended)

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd NGDI_Metadat_Tool
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv ngdi_env

# Activate virtual environment
# On Windows:
ngdi_env\Scripts\activate
# On macOS/Linux:
source ngdi_env/bin/activate
```

3. Install dependencies:
```bash
pip install django
# Add any additional requirements here
```

## Configuration

1. Database setup:
```bash
python manage.py migrate
```

2. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Access the application:
- Main application: http://localhost:8000
- Admin interface: http://localhost:8000/admin

## Project Structure

```
NGDI_Metadat_Tool/
├── api/                    # API application
├── ngdi_metadata_tool/     # Main project directory
├── ngdi_env/              # Virtual environment
├── manage.py              # Django management script
├── db.sqlite3             # SQLite database
└── settings.py            # Project settings
```

## Development

- The project uses Django's built-in development server
- SQLite is used as the default database
- API endpoints are available in the `api/` directory

## Contributing

1. Create a new branch for your feature:
```bash
# Ensure you're on the main branch and up-to-date
git checkout main
git pull origin main

# Create and switch to a new feature branch
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
# Add your changes
git add .

# Commit with a descriptive message
git commit -m "Description of your changes"

# Push your branch to the remote repository
git push origin feature/your-feature-name
```

3. Submit a pull request:
   - Go to the repository on GitHub
   - Click "Pull requests" and then "New pull request"
   - Select your feature branch to merge into main
   - Add a description of your changes
   - Click "Create pull request"

## License

[Add your license information here]

## Support

For any questions or issues, please [create an issue](repository-issues-url) or contact the development team. 