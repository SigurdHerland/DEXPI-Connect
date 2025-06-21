import lxml
from lxml import etree
import os

class ParseLinesAndCircles:
    def __init__(self, root):
        self.x_extent = []
        self.y_extent = []
        self.circle_extent = []
        self.root = root

        # Extract data
        self.findLines()
        self.frameX, self.frameY = self.set_frame()
        self.findCircle()

    def findLines(self):
        """Extracts line extents from the XML."""
        for line in self.root.xpath(".//Line"):
            min_element, max_element = line.find(".//Min"), line.find(".//Max")
            if min_element is not None and max_element is not None:
                try:
                    min_x, min_y = float(min_element.get("X")), float(min_element.get("Y"))
                    max_x, max_y = float(max_element.get("X")), float(max_element.get("Y"))
                    self.x_extent.append([min_x, max_x])
                    self.y_extent.append([min_y, max_y])
                except (TypeError, ValueError):
                    print("Error parsing line coordinates.")

    def findCircle(self):
        """Extracts circle positions and radii from the XML."""
        for circle in self.root.xpath(".//Circle"):
            location = circle.find(".//Location")
            if location is not None:
                try:
                    radius = float(circle.get("Radius"))
                    locationX = float(location.get("X"))
                    locationY = float(location.get("Y"))
                    self.circle_extent.append((radius, locationX, locationY))
                except (TypeError, ValueError):
                    print("Error parsing circle attributes.")

    def set_frame(self):
        """Finds frame dimensions from the XML."""
        extent = self.root.find(".//Extent")
        if extent is not None:
            max_elem = extent.find("Max")
            if max_elem is not None:
                try:
                    return float(max_elem.get("X")), float(max_elem.get("Y"))
                except (TypeError, ValueError):
                    print("Error parsing frame dimensions.")
        return 100, 100  # Default frame size if missing

    def get_data(self):
        """Returns all parsed data."""
        return {
            "x_extent": self.x_extent,
            "y_extent": self.y_extent,
            "circle_extent": self.circle_extent,
            "frame": (self.frameX, self.frameY)
        }
