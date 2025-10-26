# Sadqa Tracker Backend API

A FastAPI backend for the Sadqa Tracker application with Google OAuth authentication.

## Features

- 🔐 Google OAuth2 authentication
- 👤 User management with JWT tokens
- 📊 Sadqa (charity) entry CRUD operations
- 📈 Statistics and analytics
- 🔒 Secure API with rate limiting
- 📖 Auto-generated OpenAPI documentation
- 🗄️ PostgreSQL database with async SQLAlchemy
- 🔄 Database migrations with Alembic

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Google OAuth2 credentials

### Installation

1. **Create and activate virtual environment:**
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables:**
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. **Configure Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     - `http://localhost:8000/auth/google/callback` (for development)
     - Your production callback URL
   - Copy Client ID and Secret to `.env` file

5. **Setup database:**
```bash
# Create database (if not exists)
createdb sadqa_tracker_db

# Run migrations
alembic upgrade head
```

6. **Start the server:**
```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID | Required |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret | Required |
| `GOOGLE_OAUTH_REDIRECT_URI` | OAuth callback URL | `http://localhost:8000/auth/google/callback` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |
| `DEBUG` | Enable debug mode | `True` |

## API Endpoints

### Authentication
- `GET /api/v1/auth/google` - Get Google OAuth URL
- `POST /api/v1/auth/google/callback` - Handle OAuth callback
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete current user

### Sadqa Entries
- `POST /api/v1/sadqa/` - Create new sadqa entry
- `GET /api/v1/sadqa/` - Get sadqa entries (with filtering)
- `GET /api/v1/sadqa/recent` - Get recent entries
- `GET /api/v1/sadqa/stats` - Get statistics
- `GET /api/v1/sadqa/{id}` - Get specific entry
- `PUT /api/v1/sadqa/{id}` - Update entry
- `DELETE /api/v1/sadqa/{id}` - Delete entry

## Development

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

## Production Deployment

1. Set `DEBUG=False` in environment
2. Use a proper SECRET_KEY
3. Configure production database
4. Set up proper CORS origins
5. Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Security Notes

- JWT tokens expire after 30 minutes by default
- Rate limiting is applied to authentication endpoints
- CORS is configured for specified origins only
- All API endpoints require authentication except auth endpoints
- Google OAuth provides secure authentication without handling passwords

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository.

## URL for G-SSO auth
https://console.cloud.google.com/auth/clients?authuser=3&project=sadqa-tracker-475910&supportedpurview=project