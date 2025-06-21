import matplotlib.pyplot as plt
import matplotlib.patches as patches
import lxml
from lxml import etree
import os

class VisualiseXML:
    def __init__(self, x_extent, y_extent, circle_extent, Frame, fileName,ProjectPath):
        self.frameX = Frame[0]
        self.frameY = Frame[1]
        self.x_extent = x_extent
        self.y_extent = y_extent
        self.circle_extent = circle_extent
        # Set up figure and axis
        fig, ax = plt.subplots(figsize=(150, 100))

        # Draw red frame
        frame_lines = [
            ([0, self.frameX], [0, 0]),
            ([self.frameX, self.frameX], [0, self.frameY]),
            ([self.frameX, 0], [self.frameY, self.frameY]),
            ([0, 0], [self.frameY, 0])
        ]
        for x_vals, y_vals in frame_lines:
            ax.plot(x_vals, y_vals, c="r", linewidth=20)

        # Draw lines and circles
        self.plotDiagram(ax)

        # Save figure
        fileName = fileName[:-3]
        plt.savefig(f"{ProjectPath}/Spagetti/VizulationOfFolder/{fileName}.png", dpi=100)  # Optimized DPI for clarity
        plt.close(fig)  # Close figure to free memory


    def plotDiagram(self, ax):
        """Plots extracted lines and circles on the given axis."""
        for x_vals, y_vals in zip(self.x_extent, self.y_extent):
            ax.plot(x_vals, y_vals, linewidth=3, color="black")
        
        for radius, center_x, center_y in self.circle_extent:
            circle = patches.Circle((center_x, center_y), radius, edgecolor="blue", facecolor="none", linewidth=2)
            ax.add_patch(circle)
