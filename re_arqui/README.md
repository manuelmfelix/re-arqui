# RE-ARQUI Project

A Django project with FastAPI integration for architecture project management.

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd re_arqui
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser for admin access
```bash
python manage.py createsuperuser
```

### 6. Generate auth token
```bash
python manage.py drf_create_token <your-username>
```

### 7. Start the server
```bash
python manage.py runserver
```

## API Usage

The API is protected with token-based authentication. To use the protected endpoints:

1. Get your token by logging in at `/api-token-auth/` with your username and password
2. Include the token in your request headers:
   ```
   Authorization: Token your-token-here
   ```

## API Endpoints

- `POST /api/project/` - Create a new project
- `POST /api/photos/` - Add a photo to a project
- `GET /api/projects/list/` - List all projects (public)
- `GET /api/projects/{project_id}/photos/` - List photos for a project (public)
- `PUT /api/projects/{project_id}/` - Update a project (protected)
- `DELETE /api/projects/delete/` - Delete all projects (protected)
- `DELETE /api/projects/delete/{project_id}/` - Delete a specific project (protected)

## Frontend

- Home: `/`
- Project Details: `/project/<project_id>/`
- About: `/about/` 