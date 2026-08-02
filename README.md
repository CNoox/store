# Store - Online Store Builder Platform

A modern, Python-based e-commerce platform designed for entrepreneurs and small businesses to create, manage, and scale their online stores. Store provides essential features for building professional storefronts with customer authentication, product management, and more.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

### Authentication & Account Management
- **OTP-Based Authentication** - Secure login using One-Time Passwords sent via email
- **Email Verification** - Verify user email addresses during registration
- **Account Management** - User profile management and account settings

### Coming Soon
- Product Management
- Shopping Cart & Checkout
- Order Management
- Payment Processing
- Customer Dashboard
- Admin Analytics

## Tech Stack

- **Language:** Python 3.8+
- **Backend Framework:** Django / Django REST Framework
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Email Service:** SMTP (Gmail, SendGrid, etc.)
- **Authentication:** OTP-based with Email
- **API Documentation:** OpenAPI 3.0 (Swagger/ReDoc)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker & Docker Compose (optional)
- PostgreSQL 12+ (or use Docker)
- Git

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/CNoox/store.git
   cd store
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables**
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@db:5432/store
   
   # Email Configuration (Gmail SMTP)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=noreply@store.example.com
   
   # Security
   SECRET_KEY=your_secret_key_here
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

4. **Start the application**
   ```bash
   docker-compose up -d
   ```

5. **Initialize database**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**
   - API: http://localhost:8000/api/
   - API Documentation: http://localhost:8000/api/schema/
   - Admin Panel: http://localhost:8000/admin/

### Local Development (Without Docker)

**Backend Setup**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Access local development server**
- API: http://localhost:8000/api/
- API Docs: http://localhost:8000/api/schema/

## Project Structure

```
store/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Local development setup
├── .env.example          # Environment variables template
│
├── store/                # Main Django project
│   ├── settings.py       # Django settings and configuration
│   ├── urls.py           # Main URL routing
│   ├── asgi.py           # ASGI application
│   └── wsgi.py           # WSGI application
│
├── account/              # Account management app
│   ├── models.py         # User and Account models
│   ├── views.py          # API views/endpoints
│   ├── serializers.py    # DRF serializers for validation
│   ├── urls.py           # Account app URLs
│   └── tests.py          # Unit tests
│
├── docs/                 # Documentation
│   └── API.md           # API documentation
│
├── tests/               # Test suite
└── scripts/             # Utility scripts
```

## API Documentation

Full interactive API documentation is available at `/api/schema/` (OpenAPI 3.0 format).

### Authentication Endpoints

All authentication requests use OTP (One-Time Password) flow for security.

#### 1. Send OTP Code (Login)

**Endpoint:** `POST /api/account/login/`

**Description:** Send an OTP code to the specified email address for login.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 - Success):**
```json
{
  "message": "OTP code sent successfully."
}
```

**Response (400 - Invalid Email):**
```json
{
  "error": "Invalid credentials"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:8000/api/account/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Example with Python (requests):**
```python
import requests

url = "http://localhost:8000/api/account/login/"
data = {"email": "user@example.com"}
response = requests.post(url, json=data)
print(response.json())
```

#### 2. Verify OTP Code

**Endpoint:** `POST /api/account/otp/`

**Description:** Verify the OTP code sent to email and obtain authentication token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response (200 - Success):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Response (400 - Invalid OTP):**
```json
{
  "error": "Invalid OTP code"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:8000/api/account/otp/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "otp": "123456"}'
```

### Account Schemas

#### EmailOTPRequest
```json
{
  "email": "user@example.com"
}
```
- `email` (string, required): User email address

#### EmailOTPResponse
```json
{
  "message": "OTP code is sent."
}
```
- `message` (string): Success message

#### EmailRequest
```json
{
  "email": "user@example.com"
}
```
- `email` (string, required): User email address

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test account

# Run tests with verbose output
python manage.py test -v 2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML coverage report
```

### Code Style & Linting

```bash
# Install development tools
pip install flake8 black pylint

# Check code style
flake8 .
pylint account/

# Format code with black
black .
```

### Database Migrations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Revert to previous migration
python manage.py migrate account 0001
```

### Creating a Superuser (Admin)

```bash
python manage.py createsuperuser
# Follow the prompts to create admin account
# Access admin panel at: http://localhost:8000/admin/
```

### Shell Access

```bash
python manage.py shell
```

Access the Django shell to interact with your models:
```python
from account.models import User
user = User.objects.create_user(email='test@example.com')
user.save()
```

## Email Configuration

### Gmail Setup (Recommended for Development)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to myaccount.google.com
   - Security → App passwords
   - Select Mail and Other (custom)
   - Generate password
3. Add to `.env`:
   ```env
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=generated_app_password
   ```

### SendGrid Setup (For Production)

1. Create SendGrid account
2. Get API key from settings
3. Add to `.env`:
   ```env
   EMAIL_BACKEND=sendgrid_backend.SendgridBackend
   SENDGRID_API_KEY=your_api_key
   ```

### Other Email Providers

Configuration available for:
- AWS SES
- Mailgun
- Postmark
- SparkPost

## Deployment

### Docker Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U dbuser store > backup.sql
```

### Environment Variables for Production

```env
# Security
DEBUG=False
SECRET_KEY=your_very_secure_random_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/store

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# HTTPS/Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Cloud Deployment Options

**Heroku**
```bash
git push heroku main
heroku run python manage.py migrate
heroku config:set SECRET_KEY=your_secret_key
```

**PythonAnywhere**
- Upload code to PythonAnywhere
- Configure web app
- Set up virtualenv
- Reload web app

**AWS Elastic Beanstalk**
```bash
eb init
eb create
eb deploy
```

**Azure App Service**
- Deploy through Azure Portal
- Configure App Service settings
- Set environment variables

See [Deployment Guide](./docs/DEPLOYMENT.md) for detailed instructions.

## Configuration

### Django Settings

Key settings in `store/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# OTP Settings
OTP_LENGTH = 6
OTP_EXPIRATION_MINUTES = 5

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with clear, concise commits
4. **Write** tests for your changes
5. **Follow** PEP 8 code style guide
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Create** a Pull Request with detailed description

### Reporting Issues

- Check if issue already exists
- Provide detailed description
- Include steps to reproduce
- Include error logs/screenshots
- Specify Python and Django versions

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Support & Community

- **API Documentation:** [OpenAPI Docs](http://localhost:8000/api/schema/)
- **Issues:** [GitHub Issues](https://github.com/CNoox/store/issues)
- **Discussions:** [GitHub Discussions](https://github.com/CNoox/store/discussions)
- **Email Support:** support@store-example.com

## Roadmap

### Phase 1 (Current)
- [x] OTP-based authentication
- [x] Email verification
- [ ] User profile management

### Phase 2
- [ ] Product Management API
- [ ] Shopping Cart API
- [ ] Order Management

### Phase 3
- [ ] Payment Processing (Stripe/PayPal)
- [ ] Admin Dashboard
- [ ] Analytics

### Phase 4
- [ ] Multi-language Support
- [ ] Mobile App
- [ ] Advanced Features

## Security

- **OTP Protection:** 6-digit OTP with 5-minute expiration
- **Password Security:** Passwords hashed with Django's default algorithm
- **CORS:** Properly configured for security
- **CSRF Protection:** Django's built-in CSRF middleware
- **SQL Injection Protection:** Using ORM queries
- **Email Validation:** Input validation on all endpoints

## Performance Tips

- Use connection pooling for database
- Enable caching for static files
- Use CDN for media files
- Monitor with Django Debug Toolbar (development only)
- Regular database optimization

---

**Built with ❤️ by the Store Team**

*Last Updated: August 2024*
