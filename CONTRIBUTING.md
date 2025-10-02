# Contributing to Code Safe

Thank you for your interest in contributing to Code Safe! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Security Considerations](#security-considerations)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- **Be Respectful**: Treat all community members with respect and kindness
- **Be Inclusive**: Welcome newcomers and help them get started
- **Be Collaborative**: Work together to improve the project
- **Be Professional**: Maintain professional communication in all interactions

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.11 or higher
- Node.js 18 or higher
- Git
- Docker (for containerized development)
- OpenAI API key (for testing)
- Anthropic API key (for testing)

### Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/code-safe.git
   cd code-safe
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -e .
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports**: Help us identify and fix issues
2. **Feature Requests**: Suggest new features or improvements
3. **Code Contributions**: Submit bug fixes or new features
4. **Documentation**: Improve or add documentation
5. **Testing**: Add or improve test coverage
6. **Security**: Report security vulnerabilities responsibly

### Before You Start

1. **Check Existing Issues**: Look for existing issues or discussions
2. **Create an Issue**: For significant changes, create an issue first
3. **Discuss**: Engage with maintainers and community members
4. **Plan**: Outline your approach before starting development

## Development Setup

### Project Structure

```
code-safe/
├── backend/                 # Python backend
│   ├── __init__.py
│   ├── server.py           # FastAPI server
│   ├── LLMs.py            # LLM integrations
│   ├── prompts.py         # AI prompts
│   ├── symbol_finder.py   # Code analysis
│   └── tests/             # Backend tests
├── frontend/               # Next.js frontend
│   ├── app/               # App router
│   ├── components/        # React components
│   ├── types/            # TypeScript types
│   └── tests/            # Frontend tests
├── .github/               # GitHub workflows
├── docs/                  # Documentation
└── scripts/              # Utility scripts
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# AI API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Custom model configurations
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Development settings
DEBUG=true
LOG_LEVEL=INFO
```

### Running the Application

1. **Backend**
   ```bash
   # Development server
   python -m backend.server
   
   # Or using the script
   ./start-backend.sh
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Full Stack (Docker)**
   ```bash
   docker-compose up --build
   ```

## Pull Request Process

### 1. Preparation

- Ensure your fork is up to date with the main repository
- Create a feature branch from `main`
- Follow the naming convention: `feature/description` or `fix/description`

### 2. Development

- Write clean, well-documented code
- Follow coding standards (see below)
- Add appropriate tests
- Update documentation as needed

### 3. Testing

- Run all tests locally
- Ensure pre-commit hooks pass
- Test your changes thoroughly

### 4. Submission

- Create a clear, descriptive pull request
- Reference related issues
- Provide detailed description of changes
- Include screenshots for UI changes

### 5. Review Process

- Maintainers will review your PR
- Address feedback promptly
- Be open to suggestions and changes
- Maintain a collaborative attitude

## Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8 with Black formatting
- **Line Length**: 88 characters maximum
- **Imports**: Use isort for import organization
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings

```python
def analyze_code(file_path: str, llm_choice: str = "gpt") -> VulnerabilityResult:
    """Analyze code for security vulnerabilities.
    
    Args:
        file_path: Path to the file to analyze
        llm_choice: LLM to use for analysis ("gpt" or "claude")
        
    Returns:
        VulnerabilityResult containing analysis results
        
    Raises:
        FileNotFoundError: If file_path doesn't exist
        ValueError: If llm_choice is invalid
    """
    pass
```

### TypeScript (Frontend)

- **Style**: Use Prettier for formatting
- **Linting**: Follow ESLint configuration
- **Types**: Use strict TypeScript settings
- **Components**: Use functional components with hooks
- **Naming**: Use PascalCase for components, camelCase for functions

```typescript
interface VulnerabilityReportProps {
  results: VulnerabilityResult
  onReset: () => void
}

export default function VulnerabilityReport({ 
  results, 
  onReset 
}: VulnerabilityReportProps): JSX.Element {
  // Component implementation
}
```

### General Guidelines

- **Comments**: Write clear, concise comments
- **Functions**: Keep functions small and focused
- **Variables**: Use descriptive variable names
- **Error Handling**: Implement proper error handling
- **Security**: Follow security best practices

## Testing Guidelines

### Backend Testing

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and workflows
- **Security Tests**: Test security controls and validations

```python
import pytest
from backend.server import analyze_code

def test_analyze_code_with_valid_file():
    """Test code analysis with a valid Python file."""
    result = analyze_code("test_files/sample.py", "gpt")
    assert result.total_vulnerabilities >= 0
    assert result.project_name is not None

def test_analyze_code_with_invalid_file():
    """Test code analysis with non-existent file."""
    with pytest.raises(FileNotFoundError):
        analyze_code("nonexistent.py", "gpt")
```

### Frontend Testing

- **Component Tests**: Test React components
- **Integration Tests**: Test user workflows
- **E2E Tests**: Test complete user journeys

```typescript
import { render, screen } from '@testing-library/react'
import VulnerabilityReport from '@/components/VulnerabilityReport'

describe('VulnerabilityReport', () => {
  it('displays vulnerability count correctly', () => {
    const mockResults = {
      total_vulnerabilities: 5,
      // ... other properties
    }
    
    render(<VulnerabilityReport results={mockResults} onReset={() => {}} />)
    expect(screen.getByText('5 vulnerabilities found')).toBeInTheDocument()
  })
})
```

### Test Coverage

- Maintain minimum 80% test coverage
- Focus on critical paths and edge cases
- Include both positive and negative test cases

## Security Considerations

### Secure Development Practices

1. **Input Validation**: Validate all user inputs
2. **Output Encoding**: Properly encode outputs
3. **Authentication**: Implement secure authentication
4. **Authorization**: Use proper access controls
5. **Secrets Management**: Never commit secrets to code

### Security Testing

- Run security scans before submitting PRs
- Test for common vulnerabilities (OWASP Top 10)
- Validate security controls and error handling

### Reporting Security Issues

- **DO NOT** create public issues for security vulnerabilities
- Email security@codesafe.dev with details
- Follow responsible disclosure practices

## Documentation

### Code Documentation

- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Document security considerations

### User Documentation

- Update README.md for user-facing changes
- Add or update API documentation
- Include configuration examples
- Provide troubleshooting guides

### Architecture Documentation

- Document design decisions
- Explain system architecture
- Include deployment guides
- Document security architecture

## Release Process

### Version Management

- Follow Semantic Versioning (SemVer)
- Update CHANGELOG.md for each release
- Tag releases appropriately

### Release Checklist

- [ ] All tests pass
- [ ] Security scans complete
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Release notes prepared

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General discussions and questions
- **Email**: security@codesafe.dev for security issues

### Getting Help

- Check existing documentation
- Search GitHub issues
- Create a new issue with detailed information
- Be patient and respectful when asking for help

## Recognition

We appreciate all contributions and will recognize contributors in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Social media acknowledgments

## License

By contributing to Code Safe, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to Code Safe! Your efforts help make the software development ecosystem more secure for everyone.
