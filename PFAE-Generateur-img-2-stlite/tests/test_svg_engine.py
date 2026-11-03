"""
Unit tests for the SVG Engine.

This module contains comprehensive unit tests for the SVGEngine class
and its associated utility functions.
"""

import unittest
from src.svg_engine import SVGEngine, create_circle_path, create_ellipse_path, \
    create_polygon_path, create_line_path


class TestSVGEngine(unittest.TestCase):
    """Test cases for the SVGEngine class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = SVGEngine(800, 600)
    
    def test_init(self):
        """Test SVG engine initialization."""
        self.assertEqual(self.engine.width, 800)
        self.assertEqual(self.engine.height, 600)
        self.assertEqual(len(self.engine.elements), 0)
    
    def test_add_rectangle(self):
        """Test adding a rectangle."""
        self.engine.add_rectangle(10, 20, 100, 50, fill='red', stroke='black')
        
        expected = '<rect x="10" y="20" width="100" height="50" fill="red" stroke="black" stroke-width="1" />'
        self.assertIn(expected, self.engine.elements)
    
    def test_add_circle(self):
        """Test adding a circle."""
        self.engine.add_circle(100, 150, 50, fill='blue', stroke='green')
        
        expected = '<circle cx="100" cy="150" r="50" fill="blue" stroke="green" stroke-width="1" />'
        self.assertIn(expected, self.engine.elements)
    
    def test_add_line(self):
        """Test adding a line."""
        self.engine.add_line(10, 20, 100, 150, stroke='red', stroke_width=2)
        
        expected = '<line x1="10" y1="20" x2="100" y2="150" stroke="red" stroke-width="2" />'
        self.assertIn(expected, self.engine.elements)
    
    def test_add_polygon(self):
        """Test adding a polygon."""
        points = [(10, 10), (50, 10), (30, 50)]
        self.engine.add_polygon(points, fill='yellow', stroke='black')
        
        expected = '<polygon points="10,10 50,10 30,50" fill="yellow" stroke="black" stroke-width="1" />'
        self.assertIn(expected, self.engine.elements)
    
    def test_add_path(self):
        """Test adding a path."""
        path_data = 'M 10 10 L 50 50'
        self.engine.add_path(path_data, fill='none', stroke='blue')
        
        expected = '<path d="M 10 10 L 50 50" fill="none" stroke="blue" stroke-width="1" />'
        self.assertIn(expected, self.engine.elements)
    
    def test_add_text(self):
        """Test adding text."""
        self.engine.add_text(100, 200, 'Hello World', font_size=16, fill='black')
        
        expected = '<text x="100" y="200" font-size="16" font-family="Arial" fill="black">Hello World</text>'
        self.assertIn(expected, self.engine.elements)
    
    def test_render(self):
        """Test rendering the complete SVG."""
        self.engine.add_rectangle(0, 0, 100, 100)
        svg_output = self.engine.render()
        
        self.assertTrue(svg_output.startswith('<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">'))
        self.assertTrue(svg_output.endswith('</svg>'))
        self.assertIn('<rect x="0" y="0" width="100" height="100" fill="none" stroke="black" stroke-width="1" />', svg_output)
    
    def test_clear(self):
        """Test clearing elements."""
        self.engine.add_rectangle(10, 20, 100, 50)
        self.engine.clear()
        
        self.assertEqual(len(self.engine.elements), 0)
    
    def test_transforms(self):
        """Test transformation methods."""
        # Test rotation
        rotate_transform = self.engine.rotate(45, 100, 100)
        self.assertEqual(rotate_transform, 'rotate(45, 100, 100)')
        
        # Test translation
        translate_transform = self.engine.translate(50, 50)
        self.assertEqual(translate_transform, 'translate(50, 50)')
        
        # Test scaling
        scale_transform = self.engine.scale(2.0, 1.5)
        self.assertEqual(scale_transform, 'scale(2.0, 1.5)')
        
        # Test matrix
        matrix_transform = self.engine.transform_matrix(1, 0, 0, 1, 10, 10)
        self.assertEqual(matrix_transform, 'matrix(1, 0, 0, 1, 10, 10)')
    
    def test_add_group(self):
        """Test adding a group of elements."""
        # Add some elements
        self.engine.add_rectangle(10, 10, 50, 50)
        self.engine.add_circle(100, 100, 25)
        
        # Create a group with transform
        group_elements = [
            '<rect x="10" y="10" width="50" height="50" fill="none" stroke="black" stroke-width="1" />',
            '<circle cx="100" cy="100" r="25" fill="none" stroke="black" stroke-width="1" />'
        ]
        self.engine.add_group(group_elements, transform='translate(10, 10)')
        
        # Check that group was added
        self.assertIn('<g transform="translate(10, 10)">', self.engine.elements)
        self.assertIn('</g>', self.engine.elements)


class TestSVGEngineUtilityFunctions(unittest.TestCase):
    """Test cases for SVG engine utility functions."""
    
    def test_create_circle_path(self):
        """Test creating circle path data."""
        path_data = create_circle_path(100, 100, 50)
        expected = 'M 100 100 m -50 0 a 50 50 0 1 0 100 0 a 50 50 0 1 0 -100 0 z'
        self.assertEqual(path_data, expected)
    
    def test_create_ellipse_path(self):
        """Test creating ellipse path data."""
        path_data = create_ellipse_path(100, 100, 50, 30)
        expected = 'M 100 100 m -50 0 a 50 30 0 1 0 100 0 a 50 30 0 1 0 -100 0 z'
        self.assertEqual(path_data, expected)
    
    def test_create_polygon_path(self):
        """Test creating polygon path data."""
        points = [(10, 10), (50, 10), (30, 50)]
        path_data = create_polygon_path(points)
        expected = 'M 10 10 L 50 10 L 30 50 Z'
        self.assertEqual(path_data, expected)
    
    def test_create_line_path(self):
        """Test creating line path data."""
        path_data = create_line_path(10, 20, 100, 150)
        expected = 'M 10 20 L 100 150'
        self.assertEqual(path_data, expected)


def run_tests():
    """Run all tests."""
    unittest.main()


if __name__ == '__main__':
    run_tests()