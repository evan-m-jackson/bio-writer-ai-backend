# Bio Writer AI Backend

This is the backend server for the Bio Writer AI application built with Django.

## Setup Instructions

### 1. Install Dependencies
First, ensure you have Python installed on your system. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Database Setup
Initialize the database with Django migrations:

```bash
python manage.py migrate
```

### 3. Running the Development Server
Start the Django development server:

```bash
python manage.py runserver
```

### 4. Running Tests
Run Pytest

```bash
pytest api/tests.py -v
```

The server will start at `http://localhost:8000`

### Additional Commands

- Create database migrations after model changes:
  ```bash
  python manage.py makemigrations
  ```

- Create a superuser (admin account):
  ```bash
  python manage.py createsuperuser
  ```

- Access the Django admin interface at:
  `http://localhost:8000/admin`
