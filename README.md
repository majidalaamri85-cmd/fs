# Food Safety System v11

A Django-based web application for managing food safety inspections and evaluations.

## Features

- **Inspection Management**: Create, edit, and delete food safety evaluations
- **Multi-Section Evaluation**: Evaluate multiple inspection sections with different statuses
- **Image Support**: Attach multiple images to evaluations
- **Compliance Status**: Track compliance status (Compliant/Non-Compliant/Not Applicable)
- **Report Generation**: Generate Word reports (.docx) for inspections
- **Data Seeding**: Pre-populate database with 100+ food items
- **Governorate Management**: Organize evaluations by governorate/region

## Tech Stack

- **Django** 5.2+
- **Python** 3.8+
- **SQLite** (default database)
- **python-docx** (Word document generation)
- **Pillow** (Image processing)
- **WhiteNoise** (Static file serving)

## Setup Instructions

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/food-safety-system.git
cd food_safety_system_v11_complete

# Create and activate virtual environment
python -m venv .venv

# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional - defaults are provided)
```

### 3. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Seed the database with sample items (100+ food items)
python manage.py seed_items

# Optional: Seed governorates
python manage.py seed_governorates
```

### 4. Run Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Project Structure

```
food_safety_system_v11_complete/
├── food_safety_system/          # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── inspections/                 # Main Django app
│   ├── models.py               # Database models
│   ├── views.py                # View controllers
│   ├── urls.py                 # URL routes
│   ├── admin.py                # Admin configuration
│   ├── management/
│   │   └── commands/           # Custom management commands
│   │       ├── seed_items.py
│   │       └── seed_governorates.py
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS and static files
│   └── migrations/             # Database migrations
├── media/                       # User-uploaded files (images)
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── db.sqlite3                   # Database (auto-created)
```

## Database Models

- **Evaluation**: Main inspection record with status and classification
- **EvaluationItem**: Individual items within an evaluation
- **Photo**: Images attached to evaluations
- **Governorate**: Region/district information

## Usage

### Create an Inspection

1. Navigate to http://127.0.0.1:8000/
2. Click "Add Inspection" to create a new evaluation
3. Fill in the details and select items
4. Add compliance status for each item
5. Attach photos as needed
6. Submit the form

### Generate Reports

- Click "Download Report" on any inspection to generate a Word document
- The report includes all inspection details and attached images

### Manage Data

- View all inspections in the list view
- Edit or delete existing inspections
- Filter by governorate and classification

## Admin Panel

Access the Django admin panel at: **http://127.0.0.1:8000/admin/**

Default credentials can be created with:
```bash
python manage.py createsuperuser
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in your `.env`
2. Update `ALLOWED_HOSTS` in settings
3. Collect static files: `python manage.py collectstatic`
4. Use a production WSGI server like Gunicorn:

```bash
gunicorn food_safety_system.wsgi:application
```

## Troubleshooting

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py seed_items
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Specify your license here]

## Language Support

- 🇸🇦 العربية (Arabic) - See `README_AR.txt` for Arabic instructions
- 🇬🇧 English - This README

---

**Version**: 11  
**Last Updated**: May 2026
