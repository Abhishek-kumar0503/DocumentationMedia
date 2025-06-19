# DocumentationMedia


DocumentationMedia is an open source platform for hosting, managing, and collaborating on technical documentation. The platform makes it easy to search, explore, and interact with documentation from various technologies.

## 📋 Features

- **Comprehensive Documentation Library**: Access docs for Python, JavaScript, Docker, Linux, and more
- **Interactive AI Chat Interface**: Ask questions about documentation using our AI-powered chat
- **Search Functionality**: Quickly find the information you need
- **Mobile-Friendly Interface**: Access documentation on any device

## 🚀 Quick Start

Follow these steps to get DocumentationMedia up and running on your local machine.

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Abhishek-kumar0503/DocumentationMedia.git
cd DocumentationMedia
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

#### Install PostgreSQL (if not already installed)

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

macOS (using Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

Windows: Download and install from [PostgreSQL Official Website](https://www.postgresql.org/download/windows/)

#### Create Database and User

```bash
# Access PostgreSQL command line
sudo -u postgres psql

# In PostgreSQL command line
CREATE DATABASE documents;
CREATE USER docuser WITH PASSWORD 'your_secure_password';
ALTER ROLE docuser SET client_encoding TO 'utf8';
ALTER ROLE docuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE docuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE documents TO docuser;
\q
```

### 5. Create Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following environment variables to the `.env` file:

```
DATABASE_URL=postgresql://docuser:your_secure_password@localhost:5432/documents
SECRET_KEY=your_secret_key
DEBUG=True
```

### 6. Run Database Migrations

```bash
# Run migrations to set up the database schema
python manage.py migrate
```

### 7. Start the Development Server

```bash
# Start the server
python manage.py runserver

# Access the application in your web browser
http://127.0.0.1:8000/
```

## Documentation

For detailed documentation on how to use DocumentationMedia, please refer to the [Documentation](documentation/docs).

## Contributing

We welcome contributions from the community! Please see our [CONTRIBUTING.md](documentation/CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
