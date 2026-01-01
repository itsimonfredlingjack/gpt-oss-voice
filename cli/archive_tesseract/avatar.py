"""Tesseract Engine - 4D Hypercube Projection.

A real-time 3D wireframe renderer.
"""

from rich.text import Text
import math
import time
import random

class TesseractAvatar:
    """3D Wireframe Cube with dynamic state transformations.
    
    States:
    - IDLE: Slow 3-axis rotation.
    - THINKING: Fast rotation + Vertex Wobble.
    - TALKING: Audio-sync Pulse (Scale modulation).
    """

    def __init__(self, width: int = 40, height: int = 20):
        self.width = width
        self.height = height
        
        # Cube Geometry (Vertices of a unit cube centered at 0,0,0)
        self.vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        
        # Edges (Indices of connected vertices)
        self.edges = [
            (0,1), (1,2), (2,3), (3,0), # Back face
            (4,5), (5,6), (6,7), (7,4), # Front face
            (0,4), (1,5), (2,6), (3,7)  # Connecting edges
        ]
        
        self.center_x = width // 2
        self.center_y = height // 2
        self.scale = 6.0 # Base scale factor
        
        # Animation State
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0

    def _rotate_vertex(self, v, ax, ay, az):
        """Apply 3D rotation matrix."""
        x, y, z = v
        
        # Rotate X
        cos_x, sin_x = math.cos(ax), math.sin(ax)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        
        # Rotate Y
        cos_y, sin_y = math.cos(ay), math.sin(ay)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
        
        # Rotate Z
        cos_z, sin_z = math.cos(az), math.sin(az)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
        
        return [x, y, z]

    def render(self, state: str) -> Text:
        """Render the 3D cube frame."""
        t = time.time()
        
        # State Logic
        wobble = 0.0
        scale_mod = 1.0
        
        if state == "THINKING":
            # Fast Rotation
            speed = 0.15
            wobble = 0.2
            style_vertex = "avatar.wobble"
            style_edge = "avatar.wobble"
        elif state == "TALKING":
            # Pulse
            speed = 0.02
            pulse = math.sin(t * 10) * 0.3
            scale_mod = 1.0 + pulse
            style_vertex = "avatar.pulse"
            style_edge = "avatar.pulse"
        else:
            # Idle
            speed = 0.01
            style_vertex = "avatar.vertex"
            style_edge = "avatar.edge"

        self.angle_x += speed
        self.angle_y += speed * 0.6
        self.angle_z += speed * 0.3
        
        # Project Vertices
        projected = []
        for v in self.vertices:
            # Apply Rotation
            rv = self._rotate_vertex(v, self.angle_x, self.angle_y, self.angle_z)
            
            # Apply Wobble (Thinking)
            if wobble > 0:
                rv[0] += random.uniform(-wobble, wobble)
                rv[1] += random.uniform(-wobble, wobble)
                rv[2] += random.uniform(-wobble, wobble)
            
            # Perspective Projection
            # z = 1 / (distance - rv[2])
            dist = 4.0
            z = 1.0 / (dist - rv[2])
            
            px = int(rv[0] * z * self.scale * scale_mod * 2.0 + self.center_x) # *2 for aspect ratio
            py = int(rv[1] * z * self.scale * scale_mod + self.center_y)
            
            projected.append((px, py))

        # Draw Grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw Edges (Simple line drawing algorithm)
        for i, j in self.edges:
            x1, y1 = projected[i]
            x2, y2 = projected[j]
            self._draw_line(grid, x1, y1, x2, y2, "·")
            
        # Draw Vertices (Dots)
        for x, y in projected:
            if 0 <= y < self.height and 0 <= x < self.width:
                grid[y][x] = "■" if state == "THINKING" else "●"

        # Convert to Rich Text
        text = Text()
        for row in grid:
            line_str = "".join(row)
            # Apply styling per character would be expensive in pure Python for lines
            # So we apply base style to whole line, complex styling handled by regex in Rich?
            # For now, let's keep it simple: Monocolor wireframe based on state
            text.append(line_str + "\n", style=style_vertex)
            
        return text

    def _draw_line(self, grid, x1, y1, x2, y2, char):
        """Bresenham's Line Algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                if 0 <= y < self.height and 0 <= x < self.width:
                    if grid[y][x] == " ": # Don't overwrite vertices
                        grid[y][x] = char
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                if 0 <= y < self.height and 0 <= x < self.width:
                    if grid[y][x] == " ":
                        grid[y][x] = char
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

# Alias for compatibility
AIAvatar = TesseractAvatar
AntigravityAvatar = TesseractAvatar # Backward compat for imports
