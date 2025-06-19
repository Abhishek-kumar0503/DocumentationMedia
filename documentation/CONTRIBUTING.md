# Contributing to DocumentationMedia

Thank you for considering contributing to DocumentationMedia! This is an open source project and we appreciate any contributions that help improve the documentation and functionality.

## How to Contribute

### Reporting Issues

If you find any issues with the documentation or the application, please submit an issue on GitHub with the following information:

1. A clear, descriptive title
2. A detailed description of the issue
3. Steps to reproduce the issue
4. Expected behavior
5. Actual behavior
6. Screenshots (if applicable)
7. Environment details (browser, operating system, etc.)

### Submitting Changes

1. Fork the repository
2. Create a new branch for your feature or bugfix (`git checkout -b feature/your-feature-name`)
3. Make changes to the code/documentation
4. Add, commit, and push your changes to your fork
5. Submit a pull request to the main repository

### Pull Request Guidelines

- Follow the existing code style and formatting
- Include appropriate tests for your changes
- Update documentation if necessary
- Keep your pull request focused on a single topic

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Abhishek-kumar0503/DocumentationMedia.git
   ```

2. Navigate to the project directory:
   ```bash
   cd DocumentationMedia
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Make your changes and test them locally before submitting a pull request

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

- Follow PEP 8 guidelines for Python code
- Use 4 spaces for indentation (not tabs)
- Maximum line length of 100 characters
- Write descriptive variable and function names
- Include docstrings for all functions, classes, and modules

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

Thank you for your contributions!
