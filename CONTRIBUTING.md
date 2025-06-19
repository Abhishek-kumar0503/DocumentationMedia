# Contributing to DocumentationMedia

Thank you for considering contributing to DocumentationMedia! This is an open source project and we appreciate any contributions that help improve the documentation and functionality.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Documentation Contributions](#documentation-contributions)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Contact](#contact)

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community for all contributors.

## Getting Started

Before you begin:

1. Ensure you have a [GitHub account](https://github.com/signup)
2. Fork the repository on GitHub
3. Familiarize yourself with the project structure and documentation

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Abhishek-kumar0503/DocumentationMedia.git
   ```

2. Navigate to the project directory:
   ```bash
   cd DocumentationMedia
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up the database:
   ```bash
   # Create .env file with database credentials
   python manage.py migrate
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Submitting Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes to the code/documentation
   
3. Add and commit your changes:
   ```bash
   git add .
   git commit -m "Add detailed description of your changes"
   ```

4. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Submit a pull request on GitHub

## Pull Request Guidelines

- Follow the existing code style and formatting
- Include appropriate tests for your changes
- Update documentation if necessary
- Keep your pull request focused on a single topic
- Reference any relevant issues in your PR description

## Documentation Contributions

If you're adding or modifying documentation:

1. Make sure it's clear and concise
2. Follow the existing documentation format
3. Add appropriate examples where necessary
4. For code snippets, use proper syntax highlighting:
   ```python
   def example_function():
       """Example docstring for demonstration."""
       return "This is an example function"
   ```

## Code Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines for Python code
- Use 4 spaces for indentation (not tabs)
- Maximum line length of 100 characters
- Write descriptive variable and function names
- Include docstrings for all functions, classes, and modules
- Use meaningful commit messages

## Testing

Before submitting a pull request, make sure your changes pass all tests:

```bash
python manage.py test
```

If you're adding new functionality, please include appropriate tests.

## Contact

If you have any questions or need help, feel free to:
- Open an issue on GitHub
- Contact the maintainers directly

Thank you for contributing to DocumentationMedia!
