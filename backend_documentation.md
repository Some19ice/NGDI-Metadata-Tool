# NGDI Metadata Tool - Backend Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Database Models](#database-models)
5. [API Endpoints](#api-endpoints)
6. [Authentication](#authentication)
7. [Development Setup](#development-setup)

## Project Overview
The NGDI Metadata Tool is a Django-based backend system designed to manage and store metadata information for geospatial data. It provides a comprehensive API for creating, updating, and managing metadata records with various components like identification information, point of contact details, resource constraints, and more.

## Technology Stack
- **Framework**: Django 4.2.16
- **API Framework**: Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt 5.3.1)
- **Database**: SQLite (Development)
- **Documentation**: drf_yasg (Swagger/OpenAPI)
- **Development Tools**:
  - django-extensions
  - django-silk (Performance Profiling)
  - pytest (Testing)
  - pylint (Code Quality)

## Project Structure
```
.
├── api/                    # Main API application
│   ├── models.py          # Database models
│   ├── views.py           # API views and logic
│   ├── serializers.py     # Data serializers
│   ├── urls.py            # API routing
│   ├── admin.py           # Admin interface configuration
│   └── tests.py           # Test cases
├── ngdi_metadata_tool/    # Project configuration
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies
```

## Database Models

### Core Models

#### User
- Custom user model extending Django's AbstractUser
- Fields:
  - email (unique)
  - name
  - role (ADMIN/USER)
  - organization (optional)

#### Metadata
Base model for metadata records with status tracking:
- status (DRAFT/PUBLISHED/ARCHIVED)
- user (Foreign Key)
- metadata_linkage
- metadata_standard

#### IdentificationInfo
Detailed information about the data:
- title
- production_date
- edition_date
- abstract
- spatial_rep_type (RASTER/VECTOR)
- equivalent_scale
- geographic_bounding_box (JSON)
- update_frequency
- keywords (JSON)

### Supporting Models

#### PointOfContact
Contact information for the data resource:
- name
- organization
- email
- phone (optional)
- address (optional)
- role

#### ResourceConstraints
Access and usage restrictions:
- access_constraints
- use_constraints
- other_constraints

#### Distribution
Distribution information:
- name
- address
- phone_no
- weblink
- format
- distributor_email
- order_process

#### ResourceLineage
Data processing history:
- statement
- hierarchy_level
- process_software
- process_date

#### ReferenceSystem
Coordinate system information:
- identifier
- code

#### DataQuality
Quality assessment information:
- completeness_report
- accuracy_report
- process_description
- process_date

#### TemporalExtent
Time-related information:
- start_date
- end_date
- frequency

### Common Features
All models inherit from BaseModel which provides:
- UUID primary key
- created_at timestamp
- updated_at timestamp
- Automatic ordering by creation date

## Authentication
The system uses JWT (JSON Web Token) authentication with the following features:
- Token-based authentication using djangorestframework-simplejwt
- Access and refresh token mechanism
- Role-based access control (ADMIN/USER)

## Development Setup

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Installation Steps
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv ngdi_env
   source ngdi_env/bin/activate  # On Unix/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Environment Variables
Create a `.env` file in the project root with the following variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Running Tests
```bash
pytest
```

## API Documentation
The API documentation is available through Swagger UI when the server is running:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/` 

## API Endpoints

### Authentication Endpoints
- `POST /api/token/`: Obtain JWT access and refresh tokens
- `POST /api/token/refresh/`: Refresh JWT access token
- `GET /api/auth/`: Django REST framework authentication views

### Core API Endpoints
- `/api/users/`: User management endpoints
  - `GET /`: List all users (Admin only)
  - `POST /`: Create new user
  - `GET /{id}/`: Retrieve user details
  - `PUT /{id}/`: Update user
  - `DELETE /{id}/`: Delete user (Admin only)

- `/api/metadata/`: Metadata management endpoints
  - `GET /`: List all metadata records
  - `POST /`: Create new metadata record
  - `GET /{id}/`: Retrieve metadata details
  - `PUT /{id}/`: Update metadata record
  - `DELETE /{id}/`: Delete metadata record
  - `PATCH /{id}/`: Partial update of metadata record

### API Documentation
- `GET /swagger/`: Swagger UI documentation
- `GET /redoc/`: ReDoc documentation
- `GET /swagger.json`: OpenAPI specification in JSON format
- `GET /swagger.yaml`: OpenAPI specification in YAML format 