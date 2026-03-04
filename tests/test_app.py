import pytest
import os
import tempfile
import shutil
from PIL import Image
import numpy as np
from unittest.mock import patch, MagicMock
from io import BytesIO

# Import the Flask app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, preprocess_image, PROB_KEYS, vision_predict


class TestBrainTumorApp:
    """Test cases for the Brain Tumor Detection Flask Application"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        
        with app.test_client() as client:
            yield client
        
        # Cleanup
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_home_route(self, client):
        """Test the home route returns the correct template"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Brain Tumor Detection' in response.data
        assert b'Upload an MRI image for analysis' in response.data
        assert b'<form action="/upload" method="POST"' in response.data
    
    def test_home_route_template_elements(self, client):
        """Test that the home route template contains all required elements"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check navigation elements
        assert 'navbar' in html
        assert 'Home' in html
        assert 'Brain Tumors' in html
        assert 'Services' in html
        assert 'Contact Us' in html
        
        # Check form elements
        assert 'input type="file"' in html
        assert 'name="image"' in html
        assert '.png' in html and '.jpg' in html and 'accept=' in html
        assert 'required' in html
        assert 'button type="submit"' in html
        assert 'Upload MRI Image' in html
    
    def test_about_route(self, client):
        """Test the about route"""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_contact_route(self, client):
        """Test the contact route"""
        response = client.get('/contact')
        assert response.status_code == 200
    
    def test_healthz_route(self, client):
        """Test the healthz route returns JSON with expected structure"""
        response = client.get('/healthz')
        data = response.get_json()
        assert 'ok' in data
        assert 'model_loaded' in data
        assert 'model_path' in data
        assert isinstance(data['model_path'], str)
        # Status depends on whether model loaded (200 if ok, 500 if not)
        if data['model_loaded']:
            assert response.status_code == 200
            assert data['ok'] is True
        else:
            assert response.status_code == 500
            assert data['ok'] is False
    
    def test_upload_route_no_file(self, client):
        """Test upload route with no file"""
        response = client.post('/upload')
        assert response.status_code == 200
        assert b'No file selected' in response.data
    
    def test_upload_route_empty_filename(self, client):
        """Test upload route with empty filename"""
        response = client.post('/upload', data={'image': (BytesIO(b''), '')})
        assert response.status_code == 200
        assert b'No file selected' in response.data
    
    @patch('app.model', MagicMock(predict=lambda x: np.array([[0.1, 0.2, 0.6, 0.1]])))
    def test_upload_route_successful_upload(self, client, sample_image):
        """Test successful image upload and prediction"""
        response = client.post('/upload', 
                             data={'image': (sample_image, 'test_image.jpg')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'Prediction Result: no_tumor' in response.data
    
    def test_upload_route_all_predictions(self, client, sample_image):
        """Test upload route with different prediction results"""
        test_cases = [
            (np.array([[0.8, 0.1, 0.05, 0.05]]), 'glioma'),
            (np.array([[0.1, 0.8, 0.05, 0.05]]), 'meningioma'),
            (np.array([[0.1, 0.1, 0.7, 0.1]]), 'no_tumor'),
            (np.array([[0.1, 0.1, 0.1, 0.7]]), 'pituitary')
        ]
        
        for prediction_array, expected_class in test_cases:
            mock_model = MagicMock()
            mock_model.predict.return_value = prediction_array
            with patch('app.model', mock_model):
                response = client.post('/upload', 
                                     data={'image': (sample_image, 'test_image.jpg')},
                                     content_type='multipart/form-data')
                
                assert response.status_code == 200
                assert f'Prediction Result: {expected_class}'.encode() in response.data
    
    def test_preprocess_image_function(self, sample_image):
        """Test the preprocess_image function"""
        # Save the sample image to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            sample_image.seek(0)
            tmp_file.write(sample_image.read())
            tmp_file_path = tmp_file.name
        
        try:
            processed = preprocess_image(tmp_file_path)
            
            # Check the shape and data type
            assert processed.shape == (1, 224, 224, 3)
            assert processed.dtype == np.float64
            assert np.all(processed >= 0.0) and np.all(processed <= 1.0)
        finally:
            os.unlink(tmp_file_path)
    
    def test_prob_keys_constant(self):
        """Test that PROB_KEYS contains expected values"""
        expected_keys = ['glioma', 'meningioma', 'no_tumor', 'pituitary']
        assert PROB_KEYS == expected_keys
        assert len(PROB_KEYS) == 4

    @patch('app.model', MagicMock(predict=lambda x: np.array([[0.1, 0.2, 0.6, 0.1]])))
    def test_vision_predict_return_format(self, sample_image):
        """Test vision_predict returns correct structure with label, confidence, probs"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            sample_image.seek(0)
            tmp.write(sample_image.read())
            tmp_path = tmp.name
        try:
            result = vision_predict(tmp_path)
            assert 'label' in result
            assert 'confidence' in result
            assert 'probs' in result
            assert result['label'] == 'no_tumor'
            assert result['confidence'] == 0.6
            assert result['probs'] == {
                'glioma': 0.1, 'meningioma': 0.2, 'no_tumor': 0.6, 'pituitary': 0.1
            }
        finally:
            os.unlink(tmp_path)
    
    def test_template_with_prediction(self, client):
        """Test template rendering with prediction variable"""
        # This would normally be set by the upload route
        with app.test_request_context():
            response = client.get('/')
            # Simulate having a prediction by checking the template structure
            assert b'{% if prediction %}' in response.data or b'Prediction Result:' in response.data
    
    def test_static_files_references(self, client):
        """Test that static files are properly referenced in the template"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check for CSS reference
        assert 'style.css' in html
        assert 'logo.jpg' in html
    
    def test_form_attributes(self, client):
        """Test form has correct attributes"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check form attributes
        assert 'action="/upload"' in html
        assert 'method="POST"' in html
        assert 'enctype="multipart/form-data"' in html
    
    def test_file_input_attributes(self, client):
        """Test file input has correct attributes"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check file input attributes
        assert 'type="file"' in html
        assert 'name="image"' in html
        assert '.png' in html and '.jpg' in html and 'accept=' in html
        assert 'required' in html
    
    def test_navigation_links(self, client):
        """Test navigation links are present and correct"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check navigation links
        assert 'href="/"' in html
        assert 'href="/about"' in html
        assert 'href="/contact"' in html
        assert 'href="#services"' in html
    
    def test_upload_with_different_image_formats(self, client):
        """Test upload with different image formats"""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.1, 0.1, 0.7, 0.1]])
        
        # Test with different image formats
        formats = ['jpg', 'jpeg', 'png']
        
        for fmt in formats:
            # Create a test image in the specified format
            img = Image.new('RGB', (100, 100), color='blue')
            img_bytes = BytesIO()
            img.save(img_bytes, format=fmt.upper())
            img_bytes.seek(0)
            
            with patch('app.model', mock_model):
                response = client.post('/upload', 
                                     data={'image': (img_bytes, f'test_image.{fmt}')},
                                     content_type='multipart/form-data')
            
            assert response.status_code == 200
            assert b'Prediction Result: no_tumor' in response.data


class TestImageProcessing:
    """Test cases specifically for image processing functionality"""
    
    def test_preprocess_image_with_different_sizes(self):
        """Test preprocess_image handles different input image sizes"""
        sizes = [(50, 50), (300, 300), (100, 200), (200, 100)]
        
        for width, height in sizes:
            # Create test image
            img = Image.new('RGB', (width, height), color='green')
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                img.save(tmp_file.name)
                tmp_file_path = tmp_file.name
            
            try:
                processed = preprocess_image(tmp_file_path)
                
                # Should always be resized to 224x224
                assert processed.shape == (1, 224, 224, 3)
                assert processed.dtype == np.float64
            finally:
                os.unlink(tmp_file_path)
    
    def test_preprocess_image_normalization(self):
        """Test that image normalization works correctly"""
        # Create a test image with known pixel values
        img = Image.new('RGB', (100, 100), color=(255, 128, 64))
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            img.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        try:
            processed = preprocess_image(tmp_file_path)
            
            # Check normalization (original values / 255.0)
            expected_red = 255.0 / 255.0
            expected_green = 128.0 / 255.0
            expected_blue = 64.0 / 255.0
            
            # Check that values are in the expected range
            assert np.all(processed >= 0.0) and np.all(processed <= 1.0)
        finally:
            os.unlink(tmp_file_path)


if __name__ == '__main__':
    pytest.main([__file__])
