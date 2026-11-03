"""
SVG Engine for rendering vector graphics.

This module provides a comprehensive SVG rendering engine with support for
various shapes, transformations, and styling options.
"""

from typing import List, Tuple, Optional, Union
import math


class SVGEngine:
    """Main SVG engine class for rendering vector graphics."""
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the SVG engine with specified dimensions.
        
        Args:
            width (int): Width of the SVG canvas
            height (int): Height of the SVG canvas
        """
        self.width = width
        self.height = height
        self.elements = []
    
    def _create_svg_tag(self) -> str:
        """Create the opening SVG tag with dimensions."""
        return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">'
    
    def _create_close_tag(self) -> str:
        """Create the closing SVG tag."""
        return '</svg>'
    
    def add_rectangle(self, x: float, y: float, width: float, height: float, 
                     fill: str = 'none', stroke: str = 'black', stroke_width: int = 1,
                     transform: Optional[str] = None) -> None:
        """
        Add a rectangle to the SVG.
        
        Args:
            x (float): X coordinate of top-left corner
            y (float): Y coordinate of top-left corner
            width (float): Width of rectangle
            height (float): Height of rectangle
            fill (str): Fill color
            stroke (str): Stroke color
            stroke_width (int): Width of stroke
            transform (str, optional): SVG transform attribute
        """
        attrs = [
            f'x="{x}"',
            f'y="{y}"',
            f'width="{width}"',
            f'height="{height}"',
            f'fill="{fill}"',
            f'stroke="{stroke}"',
            f'stroke-width="{stroke_width}"'
        ]
        
        if transform:
            attrs.append(f'transform="{transform}"')
            
        self.elements.append(f'<rect {" ".join(attrs)} />')
    
    def add_circle(self, cx: float, cy: float, r: float, 
                  fill: str = 'none', stroke: str = 'black', stroke_width: int = 1,
                  transform: Optional[str] = None) -> None:
        """
        Add a circle to the SVG.
        
        Args:
            cx (float): X coordinate of center
            cy (float): Y coordinate of center
            r (float): Radius
            fill (str): Fill color
            stroke (str): Stroke color
            stroke_width (int): Width of stroke
            transform (str, optional): SVG transform attribute
        """
        attrs = [
            f'cx="{cx}"',
            f'cy="{cy}"',
            f'r="{r}"',
            f'fill="{fill}"',
            f'stroke="{stroke}"',
            f'stroke-width="{stroke_width}"'
        ]
        
        if transform:
            attrs.append(f'transform="{transform}"')
            
        self.elements.append(f'<circle {" ".join(attrs)} />')
    
    def add_line(self, x1: float, y1: float, x2: float, y2: float,
                stroke: str = 'black', stroke_width: int = 1,
                transform: Optional[str] = None) -> None:
        """
        Add a line to the SVG.
        
        Args:
            x1 (float): X coordinate of start point
            y1 (float): Y coordinate of start point
            x2 (float): X coordinate of end point
            y2 (float): Y coordinate of end point
            stroke (str): Stroke color
            stroke_width (int): Width of stroke
            transform (str, optional): SVG transform attribute
        """
        attrs = [
            f'x1="{x1}"',
            f'y1="{y1}"',
            f'x2="{x2}"',
            f'y2="{y2}"',
            f'stroke="{stroke}"',
            f'stroke-width="{stroke_width}"'
        ]
        
        if transform:
            attrs.append(f'transform="{transform}"')
            
        self.elements.append(f'<line {" ".join(attrs)} />')
    
    def add_polygon(self, points: List[Tuple[float, float]], 
                   fill: str = 'none', stroke: str = 'black', stroke_width: int = 1,
                   transform: Optional[str] = None) -> None:
        """
        Add a polygon to the SVG.
        
        Args:
            points (List[Tuple[float, float]]): List of (x, y) coordinates
            fill (str): Fill color
            stroke (str): Stroke color
            stroke_width (int): Width of stroke
            transform (str, optional): SVG transform attribute
        """
        point_str = ' '.join([f'{x},{y}' for x, y in points])
        
        attrs = [
            f'points="{point_str}"',
            f'fill="{fill}"',
            f'stroke="{stroke}"',
            f'stroke-width="{stroke_width}"'
        ]
        
        if transform:
            attrs.append(f'transform="{transform}"')
            
        self.elements.append(f'<polygon {" ".join(attrs)} />')
    
    def add_path(self, d: str, fill: str = 'none', stroke: str = 'black', 
                stroke_width: int = 1, transform: Optional[str] = None) -> None:
        """
        Add a path to the SVG.
        
        Args:
            d (str): Path data
            fill (str): Fill color
            stroke (str): Stroke color
            stroke_width (int): Width of stroke
            transform (str, optional): SVG transform attribute
        """
        attrs = [
            f'd="{d}"',
            f'fill="{fill}"',
            f'stroke="{stroke}"',
            f'stroke-width="{stroke_width}"'
        ]
        
        if transform:
            attrs.append(f'transform="{transform}"')
            
        self.elements.append(f'<path {" ".join(attrs)} />')
    
    def add_text(self, x: float, y: float, text: str, 
                font_size: int = 16, font_family: str = 'Arial',
                fill: str = 'black', transform: Optional[str] = None) -> None:
        """
        Add text to the SVG.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            text (str): Text content
            font_size (int): Font size
            font_family (str): Font family
            fill (str): Fill color
            transform (str, optional): SVG transform attribute
        """
        attrs = [
            f'x="{x}"',
            f'y="{y}"',
            f'font-size="{font_size}"',
            f'font-family="{font_family}"',
            f'fill="{fill}"'
        ]
        
        if transform:
            attrs.append(f'transform="{transform}"')
            
        self.elements.append(f'<text {" ".join(attrs)}>{text}</text>')
    
    def add_group(self, elements: List[str], transform: Optional[str] = None) -> None:
        """
        Add a group of elements to the SVG.
        
        Args:
            elements (List[str]): List of SVG element strings
            transform (str, optional): SVG transform attribute
        """
        attrs = []
        if transform:
            attrs.append(f'transform="{transform}"')
            
        group_attrs = " ".join(attrs) if attrs else ""
        self.elements.append(f'<g {group_attrs}>')
        for element in elements:
            self.elements.append(element)
        self.elements.append('</g>')
    
    def render(self) -> str:
        """
        Render the complete SVG document.
        
        Returns:
            str: Complete SVG document as string
        """
        svg_content = [self._create_svg_tag()]
        svg_content.extend(self.elements)
        svg_content.append(self._create_close_tag())
        return '\n'.join(svg_content)
    
    def clear(self) -> None:
        """Clear all elements from the SVG."""
        self.elements = []
    
    def rotate(self, angle: float, cx: float = 0, cy: float = 0) -> str:
        """
        Create a rotation transform string.
        
        Args:
            angle (float): Rotation angle in degrees
            cx (float): X coordinate of center point
            cy (float): Y coordinate of center point
            
        Returns:
            str: Transform attribute string for rotation
        """
        return f'rotate({angle}, {cx}, {cy})'
    
    def translate(self, tx: float, ty: float) -> str:
        """
        Create a translation transform string.
        
        Args:
            tx (float): X translation
            ty (float): Y translation
            
        Returns:
            str: Transform attribute string for translation
        """
        return f'translate({tx}, {ty})'
    
    def scale(self, sx: float, sy: float = None) -> str:
        """
        Create a scaling transform string.
        
        Args:
            sx (float): X scale factor
            sy (float, optional): Y scale factor (defaults to sx if not provided)
            
        Returns:
            str: Transform attribute string for scaling
        """
        if sy is None:
            sy = sx
        return f'scale({sx}, {sy})'
    
    def transform_matrix(self, a: float, b: float, c: float, d: float, e: float, f: float) -> str:
        """
        Create a matrix transform string.
        
        Args:
            a (float): Matrix element a
            b (float): Matrix element b
            c (float): Matrix element c
            d (float): Matrix element d
            e (float): Matrix element e
            f (float): Matrix element f
            
        Returns:
            str: Transform attribute string for matrix transformation
        """
        return f'matrix({a}, {b}, {c}, {d}, {e}, {f})'


# Utility functions for common shapes and transformations
def create_circle_path(cx: float, cy: float, r: float) -> str:
    """
    Create SVG path data for a circle.
    
    Args:
        cx (float): X coordinate of center
        cy (float): Y coordinate of center
        r (float): Radius
        
    Returns:
        str: Path data string
    """
    return f'M {cx} {cy} m -{r} 0 a {r} {r} 0 1 0 {r*2} 0 a {r} {r} 0 1 0 -{r*2} 0 z'


def create_ellipse_path(cx: float, cy: float, rx: float, ry: float) -> str:
    """
    Create SVG path data for an ellipse.
    
    Args:
        cx (float): X coordinate of center
        cy (float): Y coordinate of center
        rx (float): X radius
        ry (float): Y radius
        
    Returns:
        str: Path data string
    """
    return f'M {cx} {cy} m -{rx} 0 a {rx} {ry} 0 1 0 {rx*2} 0 a {rx} {ry} 0 1 0 -{rx*2} 0 z'


def create_polygon_path(points: List[Tuple[float, float]]) -> str:
    """
    Create SVG path data for a polygon.
    
    Args:
        points (List[Tuple[float, float]]): List of (x, y) coordinates
        
    Returns:
        str: Path data string
    """
    if not points:
        return ''
    
    path_data = f'M {points[0][0]} {points[0][1]}'
    for point in points[1:]:
        path_data += f' L {point[0]} {point[1]}'
    path_data += ' Z'
    
    return path_data


def create_line_path(x1: float, y1: float, x2: float, y2: float) -> str:
    """
    Create SVG path data for a line.
    
    Args:
        x1 (float): X coordinate of start point
        y1 (float): Y coordinate of start point
        x2 (float): X coordinate of end point
        y2 (float): Y coordinate of end point
        
    Returns:
        str: Path data string
    """
    return f'M {x1} {y1} L {x2} {y2}'


# Example usage function
def example_usage():
    """Example showing how to use the SVG engine."""
    # Create engine
    engine = SVGEngine(800, 600)
    
    # Add some elements
    engine.add_rectangle(50, 50, 200, 150, fill='lightblue', stroke='black')
    engine.add_circle(400, 300, 100, fill='yellow', stroke='orange', stroke_width=3)
    engine.add_line(100, 100, 700, 500, stroke='red', stroke_width=2)
    
    # Add text
    engine.add_text(100, 50, "Hello SVG!", font_size=24, fill='black')
    
    # Render the SVG
    svg_output = engine.render()
    print(svg_output)


if __name__ == "__main__":
    example_usage()