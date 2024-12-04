# NGDI Metadata Tool

A Django-based RESTful API service for managing NGDI (National Geospatial Data Infrastructure) metadata. This tool provides a comprehensive solution for storing, managing, and retrieving geospatial metadata following international standards.

## Features

- RESTful API for metadata management
- User authentication and authorization
- Support for multiple metadata standards
- Geospatial data validation
- Performance monitoring with Silk profiler
- Comprehensive metadata management with nested relationships
- Filtering capabilities by status and date range
- Comprehensive API with Swagger/OpenAPI documentation
- Automated testing suite

## Prerequisites

- Python 3.x
- pip (Python package installer)
- Git
- Virtual environment (recommended)

## API Endpoints

### Main Endpoints

- `/api/users/` - User management
- `/api/metadata/` - Metadata records management

### Authentication Endpoints

- `/api/auth/` - DRF authentication
- `/api/token-auth/` - Token authentication

### Documentation

- `/api/swagger/` - Swagger UI
- `/api/redoc/` - ReDoc UI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Some19ice/NGDI-Metadata-Tool.git
cd NGDI-Metadata-Tool
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
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python manage.py migrate
```

6. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

7. (Optional) Populate database with sample data:
```bash
python manage.py populate_db
```

8. Run the development server:
```bash
python manage.py runserver
```


## Development

### Project Structure
```
NGDI_Metadat_Tool/
├── api/                    # API application
├── ngdi_metadata_tool/     # Main project directory
├── manage.py              # Django management script
├── requirements.txt       # Project dependencies
└── .env                  # Environment variables
```

### Running Tests
```bash
pytest
```

### Code Quality
```bash
pylint api ngdi_metadata_tool
```

### Performance Monitoring
The project includes Silk for performance profiling. Access the Silk interface at:
```
http://localhost:8000/silk/
```

## Contributing

1. Fork the repository
2. Create your feature branch:
```bash
git checkout -b feature/your-feature-name
```
3. Commit your changes:
```bash
git commit -m "Add some feature"
```
4. Push to the branch:
```bash
git push origin feature/your-feature-name
```
5. Submit a pull request:
   - Go to the repository on GitHub
   - Click "Pull requests" and then "New pull request"
   - Select your feature branch to merge into main
   - Add a description of your changes
   - Click "Create pull request"


## License

MIT License

Copyright (c) 2024 National Space Research And Development Agency (NASRDA)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Support

For any questions or issues:
1. Check the [documentation](docs/)
2. Create an issue in the repository
3. Contact the development team

## Authors

National Space Research And Development Agency (NASRDA) &copy; 2024