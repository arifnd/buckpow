# Contributing

Guidelines for contributing to BuckPow.

---

## Welcome

Contributions are welcome! Bug reports, feature requests, documentation improvements, and pull requests are greatly appreciated.

Please open an issue before submitting large changes to discuss the proposed implementation.

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js (for frontend tooling, optional)
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/arifnd/buckpow.git
cd buckpow

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
fastapi dev app/main.py --port 8000
```

### Running Tests

```bash
python -m pytest tests/ -v
```

### Sending Dummy Data

```bash
python scripts/send_dummy.py --interval 1
```

## Project Structure

```
buckpow/
├── app/
│   ├── api/           # REST API routes
│   ├── dashboard/     # Server-rendered pages
│   ├── middleware/     # ASGI middleware
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── templates/     # Jinja2 templates
│   ├── static/        # CSS, JS
│   └── utils/         # Utility functions
├── firmware/          # Arduino sketches
├── migrations/        # Alembic migrations
├── scripts/           # Helper scripts
└── tests/             # Test suite
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bugfix
```

### 2. Make Changes

Follow the existing code style and patterns:

- **Services** — Business logic goes in `app/services/`
- **Routes** — API routes go in `app/api/`, dashboard routes in `app/dashboard/`
- **Models** — SQLAlchemy models in `app/models/`
- **Schemas** — Pydantic schemas in `app/schemas/`

### 3. Run Tests

```bash
python -m pytest tests/ -v
```

### 4. Commit

Write clear, concise commit messages:

```bash
git add .
git commit -m "feat: add device toggle endpoint"
```

### 5. Push and Create PR

```bash
git push origin feature/my-feature
```

Then open a Pull Request on GitHub.

## Code Style

### Python

- Follow PEP 8
- Use type hints where appropriate
- Keep functions focused and concise
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes

### Services

All business logic lives in the service layer:

```python
class DeviceService:
    @staticmethod
    def get_all(db: Session):
        return db.query(Device).all()

    @staticmethod
    def get_by_id(db: Session, device_id: int):
        return db.query(Device).filter(Device.id == device_id).first()
```

### Routes

API routes use dependency injection:

```python
@router.get('/devices')
def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    devices = DeviceService.get_all(db)
    return devices
```

### Templates

- Extend `base.html`
- Use Tailwind CSS classes
- Use HTMX for interactivity
- Use `<iconify-icon>` for icons

## Testing

### Test Structure

Tests are in the `tests/` directory, organized by module:

```
tests/
├── test_devices.py
├── test_sessions.py
├── test_measurements.py
├── ...
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_devices.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### Writing Tests

Follow existing patterns:

```python
def test_create_device(client, auth_headers):
    response = client.post(
        '/api/v1/devices',
        json={'device_id': 'test-01', 'name': 'Test Device'},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data['device_id'] == 'test-01'
```

## Documentation

Documentation is built with MkDocs Material:

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

### Adding Pages

1. Create markdown file in `docs/`
2. Add to `mkdocs.yml` nav
3. Use `##` for sections, `###` for subsections

## Reporting Issues

### Bug Reports

Include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, browser)

### Feature Requests

Include:

- Use case
- Proposed solution
- Alternatives considered

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
