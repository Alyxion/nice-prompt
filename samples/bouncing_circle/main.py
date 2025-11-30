"""Bouncing Circle Animation Sample.

This sample demonstrates:
- Custom JavaScript/Vue component with Python backend
- High-frequency image updates (up to 30 fps)
- PIL-based server-side rendering
- JS→Python event-driven frame requests (pull model)
- Per-user animation state via app.storage.client

The animation shows a circle bouncing around the canvas,
rendered entirely in Python using PIL and displayed via
a custom NiceGUI component.
"""

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageDraw

from nicegui import app, ui

from animated_image import AnimatedImage


# --- Animation State ---

@dataclass
class BallState:
    """State for the bouncing ball animation.
    
    Each user gets their own ball state via app.storage.client.
    """
    x: float = 200.0
    y: float = 150.0
    vx: float = 5.0  # Velocity X
    vy: float = 3.0  # Velocity Y
    radius: float = 30.0
    color: tuple = (66, 133, 244)  # Google Blue
    
    @classmethod
    def get_current(cls) -> 'BallState':
        """Get or create BallState for the current user."""
        if 'ball_state' not in app.storage.client:
            app.storage.client['ball_state'] = cls()
        return app.storage.client['ball_state']


# --- Rendering ---

def render_frame(width: int, height: int, ball: BallState) -> bytes:
    """Render a single frame of the animation using PIL.
    
    Args:
        width: Canvas width in pixels
        height: Canvas height in pixels
        ball: Current ball state
        
    Returns:
        PNG image as bytes
    """
    # Update ball position
    ball.x += ball.vx
    ball.y += ball.vy
    
    # Bounce off walls
    if ball.x - ball.radius <= 0 or ball.x + ball.radius >= width:
        ball.vx = -ball.vx
        ball.x = max(ball.radius, min(width - ball.radius, ball.x))
    
    if ball.y - ball.radius <= 0 or ball.y + ball.radius >= height:
        ball.vy = -ball.vy
        ball.y = max(ball.radius, min(height - ball.radius, ball.y))
    
    # Create image
    img = Image.new('RGB', (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    
    # Draw ball with gradient effect (simple highlight)
    # Main circle
    draw.ellipse(
        [ball.x - ball.radius, ball.y - ball.radius,
         ball.x + ball.radius, ball.y + ball.radius],
        fill=ball.color
    )
    
    # Highlight (smaller, offset circle)
    highlight_radius = ball.radius * 0.3
    highlight_offset = ball.radius * 0.3
    highlight_color = tuple(min(255, c + 80) for c in ball.color)
    draw.ellipse(
        [ball.x - highlight_offset - highlight_radius,
         ball.y - highlight_offset - highlight_radius,
         ball.x - highlight_offset + highlight_radius,
         ball.y - highlight_offset + highlight_radius],
        fill=highlight_color
    )
    
    # Draw trail effect (previous positions as fading circles)
    # This is a simple visual enhancement
    
    # Convert to PNG bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG', optimize=False)
    return buffer.getvalue()


# --- UI ---

@ui.page('/')
def index():
    """Main page with bouncing circle animation."""
    ball = BallState.get_current()
    
    # Canvas dimensions
    canvas_width = 600
    canvas_height = 400
    
    # Header
    with ui.header().classes('bg-indigo-600 text-white'):
        ui.label('Bouncing Circle Animation').classes('text-xl font-bold')
        ui.label('PIL rendering + Custom JS Component').classes('text-sm opacity-75')
    
    with ui.column().classes('p-8 items-center'):
        ui.markdown('''
        This demo shows a **custom NiceGUI component** that:
        - Renders images server-side using **PIL**
        - Displays them at up to **30 FPS** via a Vue.js component
        - Uses a **pull model**: JS requests frames, Python responds
        ''').classes('max-w-xl mb-4')
        
        # The animated image component
        def get_frame() -> bytes:
            return render_frame(canvas_width, canvas_height, ball)
        
        animated = AnimatedImage(
            width=canvas_width,
            height=canvas_height,
            show_fps=True,
            on_frame_request=get_frame,
        ).classes('rounded-lg shadow-lg')
        
        # Controls
        with ui.row().classes('mt-4 gap-4'):
            ui.button('Stop', on_click=lambda: animated.stop()).props('outline')
            ui.button('Start', on_click=lambda: animated.start()).props('color=primary')
            
            def reset_ball():
                ball.x = canvas_width / 2
                ball.y = canvas_height / 2
                ball.vx = 5.0
                ball.vy = 3.0
            
            ui.button('Reset Position', on_click=reset_ball).props('flat')
        
        # Ball customization
        with ui.card().classes('mt-6 w-96'):
            ui.label('Ball Settings').classes('font-semibold')
            
            def update_radius(e):
                ball.radius = e.value
            
            ui.slider(min=10, max=80, value=ball.radius).on_value_change(update_radius)
            ui.label().bind_text_from(ball, 'radius', lambda r: f'Radius: {r:.0f}px')
            
            def update_speed(e):
                speed_factor = e.value / 5.0
                ball.vx = 5.0 * speed_factor * (1 if ball.vx > 0 else -1)
                ball.vy = 3.0 * speed_factor * (1 if ball.vy > 0 else -1)
            
            ui.slider(min=1, max=15, value=5).on_value_change(update_speed)
            ui.label('Speed')
            
            # Color picker
            def update_color(e):
                # Convert hex to RGB tuple
                hex_color = e.value.lstrip('#')
                ball.color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            ui.color_input('Ball Color', value='#4285f4').on_value_change(update_color)
    
    # Footer
    with ui.footer().classes('bg-gray-100'):
        ui.label('NiceGUI Custom Component Sample').classes('text-gray-500 text-sm')


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        show=False,
        title='Bouncing Circle',
        reload=True,
        uvicorn_reload_includes='*.py,*.js',  # Watch JS files too
    )
