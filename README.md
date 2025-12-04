# 🛡️ NaijaShield Backend

**NaijaShield** is a comprehensive agricultural marketplace platform connecting farmers, buyers, and cooperatives across Nigeria. This repository contains the Django REST Framework backend API that powers the NaijaShield ecosystem.

---

## 🌟 Features

### Core Functionality
- ✅ **User Authentication & Authorization** - JWT-based secure authentication
- 👥 **Multi-Role System** - Support for Farmers, Buyers, and Cooperatives
- 🏆 **Trust Badge System** - Gamified credibility and verification system
- 📍 **Location-Based Services** - PostGIS-powered proximity search
- 📊 **Role-Specific Dashboards** - Customized stats and quick actions
- 🔍 **Advanced User Search** - Filter by role, name, and location
- 📝 **Activity Logging** - Comprehensive audit trail for security
- ☁️ **Cloud Storage** - Cloudinary integration for profile photos

### User Roles

#### 🌾 Farmer
- Create and manage produce listings
- Track sales and revenue
- Set farm location and size
- Connect with buyers

#### 🛒 Buyer
- Search and filter produce
- Contact farmers and cooperatives
- Track purchase history
- Save favorite suppliers

#### 🤝 Cooperative
- Manage member farmers
- Create bulk listings
- Coordinate sales for members
- View aggregate reports

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ with PostGIS extension
- Redis (for caching - optional)
- Cloudinary account (for media storage)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/EmmanuelOnyekachi21/NaijaShield_Backend.git
   cd NaijaShield_Backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database (PostgreSQL with PostGIS)
   DB_NAME=naijashield_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432

   # Cloudinary (for media storage)
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret

   # JWT Settings (optional - defaults provided)
   JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
   JWT_REFRESH_TOKEN_LIFETIME=10080  # minutes (7 days)
   ```

5. **Set up PostgreSQL with PostGIS**
   ```bash
   # Install PostGIS extension (if not already installed)
   sudo apt-get install postgresql-14-postgis-3  # Ubuntu/Debian
   
   # Create database
   createdb naijashield_db
   
   # Enable PostGIS extension
   psql naijashield_db -c "CREATE EXTENSION postgis;"
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000/api/`

---

## 📚 API Documentation

Comprehensive API documentation is available in **[API_DOCS.md](./API_DOCS.md)**.

### Quick Reference

**Base URL:** `http://localhost:8000/api/`

#### Authentication Endpoints
- `POST /auth/register/` - Register new user
- `POST /auth/login/` - Login user
- `POST /auth/logout/` - Logout user
- `POST /auth/refresh/` - Refresh access token
- `GET /auth/me/` - Get current user profile
- `PATCH /auth/profile/` - Update user profile

#### User Endpoints
- `GET /users/` - List all users
- `GET /users/<public_id>/` - Get user by ID
- `GET /users/search/` - Search users with filters
- `GET /users/badge-status/` - Get badge status
- `GET /users/activity/` - Get user activity logs

#### Dashboard Endpoints
- `GET /dashboard/stats/` - Get role-specific dashboard stats

For detailed request/response examples, authentication requirements, and field descriptions, see **[API_DOCS.md](./API_DOCS.md)**.

---

## 🏗️ Project Structure

```
NaijaShield_Backend/
├── apps/
│   ├── auth/                 # Authentication app
│   │   ├── views/
│   │   │   ├── register.py   # User registration
│   │   │   ├── login.py      # User login
│   │   │   ├── logout.py     # User logout
│   │   │   ├── refresh.py    # Token refresh
│   │   │   └── profile.py    # User profile
│   │   ├── serializers/      # Auth serializers
│   │   └── urls.py           # Auth routes
│   │
│   ├── user/                 # User management app
│   │   ├── models.py         # User, TrustBadge, UserActivity models
│   │   ├── views.py          # User views (search, badge, activity)
│   │   ├── serializers.py    # User serializers
│   │   ├── utils.py          # Helper functions
│   │   └── urls.py           # User routes
│   │
│   ├── dashboard/            # Dashboard app
│   │   ├── views.py          # Dashboard stats
│   │   └── urls.py           # Dashboard routes
│   │
│   └── urls.py               # Main app URL router
│
├── config/                   # Django configuration
│   ├── settings.py           # Project settings
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI configuration
│
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .gitignore               # Git ignore rules
├── API_DOCS.md              # API documentation
└── README.md                # This file
```

---

## 🗄️ Database Models

### User Model
Core user model with role-based fields and location support.

**Fields:**
- `public_id` (UUID) - Primary key
- `first_name`, `last_name` - User name
- `email` - Unique email address
- `phone_number` - Unique phone (auto-formatted to +234)
- `role` - One of: `farmer`, `buyer`, `co-ops`
- `location` (PointField) - GPS coordinates (PostGIS)
- `location_text` - Human-readable address
- `farm_size` - Farm size in hectares (farmers only)
- `business_name` - Business name (buyers/co-ops only)
- `bio` - User/business description
- `profile_photo` - Cloudinary URL
- `profile_completion` - Calculated percentage (0-100)

### TrustBadge Model
Tracks user verification and badge level.

**Fields:**
- `user` (OneToOne) - Related user
- `badge_level` - One of: `new_user`, `bronze`, `silver`, `gold`, `diamond`
- `is_phone_verified` - Phone verification status
- `is_id_verified` - ID verification status
- `is_location_verified` - Location verification status
- `is_community_trusted` - Community trust status
- `transaction_count` - Total completed transactions
- `average_rating` - Average user rating (0-5)

**Badge Requirements:**
- **Bronze:** ≥5 transactions, ≥4.0 rating
- **Silver:** ≥20 transactions, ≥4.3 rating
- **Gold:** ≥50 transactions, ≥4.7 rating
- **Diamond:** ≥100 transactions, ≥4.8 rating

### UserActivity Model
Logs all user actions for audit and security.

**Fields:**
- `user` - Related user
- `action_type` - Type of action (login, profile_update, etc.)
- `description` - Action description
- `metadata` - JSON field for additional context
- `ip_address` - User's IP address
- `created_at` - Timestamp

---

## 🔐 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Token Blacklisting** - Invalidate refresh tokens on logout
- **Password Hashing** - Django's PBKDF2 algorithm
- **Activity Logging** - Track all user actions with IP addresses
- **Role-Based Access Control** - Enforce role-specific permissions
- **Input Validation** - Comprehensive serializer validation
- **CORS Configuration** - Controlled cross-origin access

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.auth
python manage.py test apps.user

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🚢 Deployment

### Environment Setup

1. **Set `DEBUG=False`** in production
2. **Configure `ALLOWED_HOSTS`** with your domain
3. **Set up production database** (PostgreSQL with PostGIS)
4. **Configure static files** serving
5. **Set up HTTPS** (required for production)

### Recommended Stack

- **Server:** Gunicorn + Nginx
- **Database:** PostgreSQL 14+ with PostGIS
- **Cache:** Redis
- **Storage:** Cloudinary (media files)
- **Hosting:** Railway, Heroku, AWS, or DigitalOcean

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up CI/CD pipeline

---

## 🛠️ Development

### Code Style

This project follows:
- **PEP 8** - Python style guide
- **Django Best Practices** - Django coding standards
- **DRF Conventions** - Django REST Framework patterns

### Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request

### Adding New Features

1. Create/update models in `apps/<app>/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Create serializers in `apps/<app>/serializers.py`
5. Create views in `apps/<app>/views.py`
6. Register URLs in `apps/<app>/urls.py`
7. Update API documentation in `API_DOCS.md`
8. Write tests in `apps/<app>/tests.py`

---

## 📦 Dependencies

### Core
- **Django 5.2** - Web framework
- **Django REST Framework** - API framework
- **djangorestframework-simplejwt** - JWT authentication
- **django-cors-headers** - CORS support

### Database
- **psycopg2-binary** - PostgreSQL adapter
- **django.contrib.gis** - GeoDjango for location features

### Storage
- **cloudinary** - Cloud media storage
- **Pillow** - Image processing

### Utilities
- **python-decouple** - Environment variable management
- **dj-database-url** - Database URL parsing

See `requirements.txt` for complete list.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation
- Follow existing code style
- Ensure all tests pass

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Emmanuel Onyekachi** - Lead Developer - [@EmmanuelOnyekachi21](https://github.com/EmmanuelOnyekachi21)

---

## 🙏 Acknowledgments

- Django and DRF communities
- PostGIS for geospatial capabilities
- Cloudinary for media storage
- All contributors and supporters

---

## 📞 Support

For support, questions, or feedback:

- **Email:** support@naijashield.com
- **GitHub Issues:** [Create an issue](https://github.com/EmmanuelOnyekachi21/NaijaShield_Backend/issues)
- **Documentation:** [API_DOCS.md](./API_DOCS.md)

---

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] User authentication and authorization
- [x] Multi-role system
- [x] Trust badge system
- [x] Location-based search
- [x] Activity logging
- [x] Profile management

### Phase 2 (Upcoming)
- [ ] Produce listing management
- [ ] Messaging system
- [ ] Transaction management
- [ ] Rating and review system
- [ ] Price tracking
- [ ] Notification system

### Phase 3 (Future)
- [ ] Payment integration
- [ ] Analytics dashboard
- [ ] Mobile app API optimization
- [ ] AI-powered recommendations
- [ ] Multi-language support
- [ ] Advanced reporting

---

**Built with ❤️ for Nigerian Agriculture**
