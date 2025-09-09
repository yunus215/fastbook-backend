# FastBook: A RESTful Book Management API 📚⚡

## ✨ Overview

Welcome to **FastBook**, a robust REST API designed for managing a modern book collection and review system. Built with Python, FastAPI, and PostgreSQL, this backend service provides a fast, scalable, and efficient foundation for a book management application. It follows modern API design principles with comprehensive authentication, asynchronous operations, and clean separation of concerns, making it highly maintainable and performant.

## 🔋 Key Features

- 🔐 **JWT Authentication** — Secure endpoints using JSON Web Tokens (JWT) with refresh token support, ensuring that only authenticated users can access protected resources.
- 🏗️ **Clean Architecture** — Organized into distinct layers (Routes, Services, Models) for a clear separation of concerns, making the codebase easy to understand, test, and scale.
- 📦 **Full CRUD Operations** — Comprehensive Create, Read, Update, and Delete functionality for all core entities:
  - **Users**: Complete user management with secure password hashing, email verification, and role-based access control.
  - **Books**: Manage book catalog with detailed information and user associations.
  - **Reviews**: Allow users to rate and review books with comment functionality.
  - **Tags**: Organize books with tagging system for better categorization.
- 📧 **Email System** — Integrated email functionality with Celery background tasks for:
  - Account verification emails
  - Password reset notifications
  - Welcome messages
- 🔄 **Background Tasks** — Asynchronous email processing using Celery and Redis for improved performance.
- 🛡️ **Request Validation** — Built-in validation using Pydantic models to ensure data integrity and type safety.
- 🐘 **PostgreSQL Integration** — Utilizes PostgreSQL with SQLModel (SQLAlchemy) for robust and reliable async data storage.
- 🚀 **High Performance** — Built on FastAPI for automatic API documentation, async support, and blazing-fast performance.
- 🔍 **Token Blacklisting** — Redis-based token blacklisting for secure logout functionality.
- 📊 **Database Migrations** — Alembic integration for database schema versioning and migrations.
- ⚙️ **Centralized Configuration** — Manages all environment-specific settings securely through environment variables.

## 🧑‍💻 How It Works

1.  **User registers** by sending their details to the `/signup` endpoint and receives an email verification link.
2.  **User verifies email** by clicking the verification link and can then **authenticate** via `/login` to receive JWT tokens.
3.  **The client includes the JWT** as a Bearer Token in the `Authorization` header for all subsequent requests to protected endpoints.
4.  **JWT Middleware** intercepts and validates tokens, checking against Redis blacklist for revoked tokens.
5.  **The Routes layer** receives requests, validates data using Pydantic schemas, and calls appropriate **Service layer** methods.
6.  **The Service layer** executes core business logic, handles exceptions, and coordinates with the **Models layer**.
7.  **The Models layer** manages database interactions using SQLModel and async SQLAlchemy sessions.
8.  **Background tasks** handle email sending asynchronously via Celery workers.
9.  **A structured JSON response** with comprehensive error handling is returned to the client.

## ⚙️ Tech Stack

- 🐍 **Python 3.12+**
- ⚡ **FastAPI** (Modern Web Framework)
- 🐘 **PostgreSQL** (Database)
- 🔗 **SQLModel** (ORM with SQLAlchemy)
- 🔐 **python-jose** (JWT Implementation)
- 🛡️ **passlib** (Password Hashing with bcrypt)
- ✅ **Pydantic** (Data Validation)
- 📧 **fastapi-mail** (Email Integration)
- 🔄 **Celery** (Background Task Processing)
- 🗄️ **Redis** (Token Blacklisting & Celery Broker)
- 🗃️ **Alembic** (Database Migrations)
- 🧪 **pytest** (Testing Framework)

## 📚 FastBook Insights

- 🌐 **Python Backend** : [View Code](https://github.com/LouisFernando1204/fastbook-backend)

## 🚀 Getting Started

Follow these steps to get FastBook up and running on your local machine.

### Prerequisites

- [Python](https://www.python.org/downloads/) (version 3.12 or higher)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Redis](https://redis.io/download) (for token blacklisting and Celery)
- A tool to interact with your database (e.g., TablePlus, DBeaver, or pgAdmin)

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/LouisFernando1204/fastbook-backend.git
    cd fastbook-backend
    ```

2.  **Create and activate virtual environment:**

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    - Create a `.env` file in the root directory.
    - Add the following configuration variables:

    ```env
    # Database Configuration
    DATABASE_URL="postgresql+asyncpg://username@localhost:5432/fastblog_db"

    # JWT Configuration
    JWT_SECRET="your_super_secret_jwt_key_here"
    JWT_ALGORITHM="HS256"

    # Redis Configuration
    REDIS_HORT="localhost"
    REDIS_PORT=6379
    REDIS_URL="redis://localhost:6379/0"

    # Email Configuration
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_app_password
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_FROM=your_email@gmail.com
    MAIL_FROM_NAME=FastBook Backend

    # Application Configuration
    DOMAIN=localhost:8000

    # PostgreSQL Configuration (Optional)
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_DB=
    ```

5.  **Set up the database:**

    - Start your PostgreSQL server.
    - Create a new database named `fastbook_db` (or as specified in your DATABASE_URL).
    - Run database migrations:

    ```bash
    alembic upgrade head
    ```

6.  **Start Redis server:**

    ```bash
    redis-server
    ```

7.  **Start Celery worker** (in a separate terminal):

    ```bash
    celery -A src.celery_tasks worker --loglevel=info
    ```

8.  **Run the application:**

    ```bash
    fastapi dev src/
    ```

    The server should now be running on `http://localhost:8000`.

9.  **Access API Documentation:**
    - Swagger UI: `http://localhost:8000/docs`
    - ReDoc: `http://localhost:8000/redoc`

## 📋 API Endpoints

### Authentication

- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/verify/{token}` - Verify email
- `POST /api/v1/auth/refresh-token` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user profile
- `POST /api/v1/auth/password-reset-request` - Request password reset
- `POST /api/v1/auth/password-reset-confirm/{token}` - Confirm password reset

### Books Management

- `GET /api/v1/books/` - Get all books
- `POST /api/v1/books/` - Create new book
- `GET /api/v1/books/{book_uid}` - Get book by ID
- `PATCH /api/v1/books/{book_uid}` - Update book
- `DELETE /api/v1/books/{book_uid}` - Delete book

### Reviews

- `POST /api/v1/books/{book_uid}/reviews` - Add review to book
- `DELETE /api/v1/books/{book_uid}/reviews/{review_uid}` - Delete review

### Tags

- `GET /api/v1/tags/` - Get all tags
- `POST /api/v1/tags/` - Create new tag
- `POST /api/v1/books/{book_uid}/tags` - Add tags to book
- `DELETE /api/v1/books/{book_uid}/tags/{tag_uid}` - Remove tag from book

## 🧪 Running Tests

```bash
pytest src/tests/ -v
```

## 🤝 Contributor

- 🧑‍💻 **Louis Fernando** : [@LouisFernando1204](https://github.com/LouisFernando1204)
