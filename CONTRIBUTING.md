# Contributing to AI Sales Helper

Thank you for considering contributing to AI Sales Helper! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python/Node version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear use case**
- **Expected behavior**
- **Why this would be useful**
- **Possible implementation approach**

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation

4. **Run tests**
   ```bash
   # Backend tests
   cd backend
   pytest tests/ -v
   
   # Frontend tests (if applicable)
   cd frontend
   npm test
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of your changes"
   ```
   
   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Test:` for test additions/updates
   - `Refactor:` for code refactoring

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Use a clear title
   - Reference related issues
   - Describe your changes
   - Include screenshots for UI changes

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run linter
npm run lint
```

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for classes and functions
- Maximum line length: 100 characters
- Use **meaningful variable names**

Example:
```python
def calculate_discount(
    product: Product,
    quantity: int,
    db: Session
) -> Dict[str, Any]:
    """
    Calculate applicable discount for a product.
    
    Args:
        product: Product instance
        quantity: Quantity being purchased
        db: Database session
        
    Returns:
        Dictionary with discount details
    """
    # Implementation
```

### TypeScript (Frontend)

- Use **TypeScript** for all files
- Follow **Airbnb style guide**
- Use **functional components** with hooks
- Write **prop types** for all components
- Use **meaningful component names**

Example:
```typescript
interface ProductCardProps {
  product: Product;
  onEdit: (product: Product) => void;
  onDelete: (id: number) => void;
}

export function ProductCard({ product, onEdit, onDelete }: ProductCardProps) {
  // Implementation
}
```

### Terraform

- Use **consistent naming conventions**
- Add **comments** for complex resources
- Use **variables** for configurable values
- Tag all resources appropriately

## Testing Guidelines

### Backend Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for setup
- Mock external services (OpenAI, Telegram)

```python
def test_calculate_discount(db):
    """Test discount calculation"""
    product = create_test_product(db)
    result = DiscountEngine.calculate_discount(product, 5, db)
    assert result["discount_applied"] > 0
```

### Frontend Tests

- Test user interactions
- Test API integrations
- Test error handling
- Use React Testing Library

## Documentation

- Update README.md for major changes
- Add JSDoc/docstrings for new functions
- Update API documentation
- Include examples in documentation

## Project Structure

When adding new features, follow the existing structure:

```
backend/app/
├── api/          # API endpoints (group by resource)
├── models/       # Database models
├── schemas/      # Pydantic schemas
├── services/     # Business logic
└── tests/        # Test files (mirror app structure)

frontend/src/
├── components/   # Reusable components
├── pages/        # Page components
├── lib/          # Utilities and API
├── store/        # State management
└── types/        # TypeScript types
```

## Review Process

1. **Automated checks** must pass (tests, linting)
2. **Code review** by at least one maintainer
3. **Documentation** must be updated
4. **Tests** must be included
5. **No merge conflicts** with main branch

## Questions?

- Open an issue for questions
- Join our discussions
- Email the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in the project README. Thank you for your contributions!
