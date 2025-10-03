# Test Suite for Brain Tumor Detection Flask App

This directory contains comprehensive unit tests for the Brain Tumor Detection Flask application.

## Test Files

### `test_app.py`
Main test file containing:
- **Flask Route Tests**: Tests for all routes (/, /upload, /about, /contact)
- **Template Rendering Tests**: Tests for template rendering and context variables
- **Form Functionality Tests**: Tests for form submission and file upload handling
- **Image Processing Tests**: Tests for the `preprocess_image` function
- **Model Integration Tests**: Tests for model prediction functionality

### `test_template_content.py`
Template-specific tests containing:
- **HTML Structure Tests**: Tests for proper HTML structure and DOCTYPE
- **Meta Tags Tests**: Tests for meta tags and viewport settings
- **Navigation Tests**: Tests for navigation bar structure and links
- **Form Structure Tests**: Tests for form attributes and input elements
- **Jinja2 Template Tests**: Tests for proper template syntax
- **Accessibility Tests**: Tests for accessibility elements

## Running Tests

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_app.py
pytest tests/test_template_content.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=app
```

## Test Coverage

The test suite covers:

1. **Flask Application Routes**
   - Home route (`/`)
   - Upload route (`/upload`)
   - About route (`/about`)
   - Contact route (`/contact`)

2. **Template Rendering**
   - HTML structure validation
   - Jinja2 template syntax
   - Static file references
   - Form elements and attributes

3. **File Upload Functionality**
   - File upload handling
   - Image preprocessing
   - Model prediction integration
   - Error handling for invalid uploads

4. **Image Processing**
   - Image resizing and normalization
   - Different image format support
   - Batch dimension handling

5. **Model Integration**
   - Prediction result handling
   - Class label validation
   - Mock model testing

## Test Fixtures

- `client`: Flask test client
- `sample_image`: Test image for upload tests
- Mocked model predictions for isolated testing

## Mocking

The tests use `unittest.mock` to mock:
- TensorFlow model predictions
- File system operations
- Image processing functions

This ensures tests run quickly and don't require the actual model file.

## Test Data

Tests use temporary files and in-memory image data to avoid dependencies on external files while maintaining realistic test scenarios.
