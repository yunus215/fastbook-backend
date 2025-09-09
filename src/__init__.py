from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware


# ini akan otomatis menjalankan pembuatan database dan tabel (jika ada tabel yang baru ditambahkan sebagai SQLModel), kalau mau pakai alembic ini bisa dihapus
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server is shutting down...")


description = """
A comprehensive REST API for a modern book review and management platform.

## 📚 Overview
FastBook Backend provides a robust and scalable solution for managing books, user reviews, and content organization through a tag-based system. Built with FastAPI, this API offers high performance, automatic documentation, and enterprise-grade features.

## 🚀 Key Features
### 📖 Book Management
- **Complete CRUD operations** for books (Create, Read, Update, Delete)
- **Advanced book filtering** and search capabilities
- **User-specific book collections** and submissions
- **Detailed book metadata** including author, publication date, genres, and descriptions
### ⭐ Review System
- **User reviews and ratings** for books
- **Review management** (create, read, update, delete)
- **User-specific review history** and moderation
- **Rating aggregation** and analytics
### 🏷️ Tag Management
- **Flexible tagging system** for content organization
- **Tag creation and management** with CRUD operations
- **Book-tag associations** for improved discoverability
- **Tag-based filtering** and categorization
### 🔐 Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Role-based access control** (User, Admin)
- **Email verification** and account activation
- **Password reset** functionality with secure token-based flow
- **Session management** with token blacklisting
### 📧 Communication Features
- **Email notifications** for account verification
- **Password reset emails** with secure links
- **Background task processing** using Celery for improved performance
- **Asynchronous email delivery** for better user experience

## 🛠️ Technical Stack
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT tokens with Redis-based blacklisting
- **Email Service**: Asynchronous email processing with Celery
- **Database Migrations**: Alembic for schema management
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

## 🔧 API Capabilities
### Core Operations
- ✅ **RESTful design** following industry standards
- ✅ **Comprehensive error handling** with custom exceptions
- ✅ **Data validation** using Pydantic models
- ✅ **Automatic API documentation** with interactive Swagger UI
- ✅ **Database transactions** and connection pooling
- ✅ **Background task processing** for non-blocking operations
### Security Features
- 🔒 **Secure password hashing** using industry-standard algorithms
- 🔒 **Token-based authentication** with expiration handling
- 🔒 **Input validation** and sanitization
- 🔒 **SQL injection protection** through ORM usage
- 🔒 **CORS configuration** for cross-origin requests

## 📖 Documentation
This API provides comprehensive documentation including:
- **Interactive API exploration** via Swagger UI
- **Detailed endpoint descriptions** with examples
- **Request/Response schemas** with validation rules
- **Authentication requirements** for each endpoint
- **Error code references** and troubleshooting guides

Perfect for developers building book-related applications, content management systems, or educational platforms requiring robust book and review management capabilities.
"""

version = "v1"
version_prefix = f"/api/{version}"

app = FastAPI(
    title="FastBook Backend",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Louis Fernando",
        "url": "https://github.com/LouisFernando1204",
        "email": "fernandolouis55@gmail.com",
    },
    terms_of_service="httpS://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
    lifespan=lifespan,
)

register_all_errors(app)
register_middleware(app)


@app.get("/", tags=["root"])
async def read_root():
    """
    Root endpoint for FastBook Backend API.

    This endpoint provides basic information about the API and quick links
    to access documentation and available endpoints.

    Returns:
        dict: Welcome message with API information and useful links
    """
    return {
        "message": "Welcome to FastBook Backend API! 📚",
        "description": "A comprehensive REST API for book review and management platform.",
        "version": version,
        "status": "healthy",
        "documentation": {
            "swagger_ui": f"{version_prefix}/docs",
            "redoc": f"{version_prefix}/redoc",
            "openapi_schema": f"{version_prefix}/openapi.json",
        },
        "endpoints": {
            "authentication": f"{version_prefix}/auth",
            "books": f"{version_prefix}/books",
            "reviews": f"{version_prefix}/reviews",
            "tags": f"{version_prefix}/tags",
        },
        "features": [
            "🔐 JWT Authentication & Authorization",
            "📖 Complete Book Management CRUD",
            "⭐ Review & Rating System",
            "🏷️ Flexible Tag Management",
            "📧 Email Notifications",
            "📊 Auto-generated Documentation",
        ],
        "developer": {
            "name": "Louis Fernando",
            "github": "https://github.com/LouisFernando1204",
            "email": "fernandolouis55@gmail.com",
        },
    }


app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])
