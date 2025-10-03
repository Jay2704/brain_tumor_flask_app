import pytest
import os
import sys
from bs4 import BeautifulSoup

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app


class TestTemplateContent:
    """Test cases specifically for HTML template content and structure"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_html_structure(self, client):
        """Test basic HTML structure and DOCTYPE"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check HTML structure
        assert '<!DOCTYPE html>' in html
        assert '<html lang="en">' in html
        assert '<head>' in html
        assert '<body>' in html
        assert '</html>' in html
    
    def test_meta_tags(self, client):
        """Test meta tags are present"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check meta tags
        assert '<meta charset="UTF-8">' in html
        assert 'viewport' in html
        assert 'width=device-width, initial-scale=1.0' in html
    
    def test_title_tag(self, client):
        """Test page title"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert '<title>Brain Tumor Detection</title>' in html
    
    def test_css_link(self, client):
        """Test CSS file is linked correctly"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert 'style.css' in html
        assert 'stylesheet' in html
    
    def test_navigation_structure(self, client):
        """Test navigation bar structure"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check navigation elements
        assert 'navbar' in html
        assert 'navbar-container' in html
        assert 'navbar-logo' in html
        assert 'navbar-links' in html
        assert 'nav-link' in html
    
    def test_logo_image(self, client):
        """Test logo image is present"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert 'logo.jpg' in html
        assert 'Site Logo' in html
        assert 'alt=' in html
    
    def test_navigation_links_content(self, client):
        """Test navigation links have correct text and hrefs"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check link texts
        assert 'Home' in html
        assert 'Brain Tumors' in html
        assert 'Services' in html
        assert 'Contact Us' in html
        
        # Check href attributes
        assert 'href="/"' in html
        assert 'href="/about"' in html
        assert 'href="/contact"' in html
        assert 'href="#services"' in html
    
    def test_main_content_structure(self, client):
        """Test main content area structure"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check main content elements
        assert 'container' in html
        assert 'Brain Tumor Detection' in html
        assert 'Upload an MRI image for analysis' in html
    
    def test_form_structure(self, client):
        """Test form structure and attributes"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check form attributes
        assert 'action="/upload"' in html
        assert 'method="POST"' in html
        assert 'enctype="multipart/form-data"' in html
    
    def test_file_input_structure(self, client):
        """Test file input structure and attributes"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check file input attributes
        assert 'type="file"' in html
        assert 'name="image"' in html
        assert 'accept="image/*"' in html
        assert 'required' in html
    
    def test_submit_button(self, client):
        """Test submit button structure"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check submit button
        assert 'button type="submit"' in html
        assert 'Upload MRI Image' in html
    
    def test_prediction_section_structure(self, client):
        """Test prediction result section structure"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check prediction section template logic
        assert '{% if prediction %}' in html or 'Prediction Result:' in html
        assert '{{ prediction }}' in html
    
    def test_jinja_template_syntax(self, client):
        """Test Jinja2 template syntax is correct"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check for proper Jinja2 syntax
        assert '{{ url_for(' in html
        assert '{{ prediction }}' in html
        assert '{% if prediction %}' in html
        assert '{% endif %}' in html
    
    def test_static_file_references(self, client):
        """Test static file references use url_for"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check url_for usage for static files
        assert "url_for('static', filename='style.css')" in html
        assert "url_for('static', filename='logo.jpg')" in html
    
    def test_responsive_design_elements(self, client):
        """Test responsive design elements"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check for responsive design elements
        assert 'width=device-width' in html
        assert 'initial-scale=1.0' in html
    
    def test_accessibility_elements(self, client):
        """Test accessibility elements"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check for accessibility elements
        assert 'alt=' in html  # Alt text for images
        assert 'lang="en"' in html  # Language declaration
    
    def test_semantic_html_structure(self, client):
        """Test semantic HTML structure"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check for semantic elements
        assert '<nav' in html
        assert '<h1>' in html
        assert '<h2>' in html
        assert '<p>' in html
        assert '<form>' in html
        assert '<input' in html
        assert '<button>' in html
    
    def test_no_prediction_initial_state(self, client):
        """Test template when no prediction is available"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Should not show prediction result initially
        assert 'Prediction Result:' not in html or '{% if prediction %}' in html
    
    def test_template_rendering_with_prediction(self, client):
        """Test template rendering when prediction is provided"""
        # This test would require mocking the upload route
        # For now, we'll test the template structure supports predictions
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check that the template has the structure to display predictions
        assert '{{ prediction }}' in html
        assert '{% if prediction %}' in html
        assert '{% endif %}' in html


if __name__ == '__main__':
    pytest.main([__file__])
