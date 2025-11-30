"""Animated Image Component - Custom NiceGUI element with JS/Python communication.

This component demonstrates:
- Custom JavaScript/Vue component integration
- High-frequency Python→JS image updates (up to 30 fps)
- JS→Python event-driven frame requests
- PIL-based server-side rendering
"""

from typing import Callable

from nicegui.element import Element
from nicegui.events import GenericEventArguments, handle_event


class AnimatedImage(Element, component='animated_image.js'):
    """A custom component that displays images at high frame rates.
    
    The JavaScript side requests frames via events, and Python responds
    with base64-encoded PNG images rendered using PIL.
    
    This pull-based approach ensures:
    - No frame buildup if client is slow
    - Automatic frame rate adaptation
    - Clean separation of concerns
    """
    
    def __init__(
        self,
        width: int = 400,
        height: int = 300,
        show_fps: bool = True,
        target_fps: int = 30,
        on_frame_request: Callable[[], bytes | None] | None = None,
    ) -> None:
        """Initialize the animated image component.
        
        Args:
            width: Display width in pixels
            height: Display height in pixels
            show_fps: Whether to show FPS counter overlay
            target_fps: Target frames per second (max 30)
            on_frame_request: Callback that returns PNG bytes for each frame
        """
        super().__init__()
        self._props['width'] = width
        self._props['height'] = height
        self._props['showFps'] = show_fps
        self._props['targetFps'] = min(target_fps, 30)
        
        self._frame_callback = on_frame_request
        
        # Register handler for frame requests from JS
        self.on('frame-request', self._handle_frame_request)
    
    def _handle_frame_request(self, _e: GenericEventArguments) -> None:
        """Handle frame request from JavaScript."""
        if self._frame_callback is None:
            return
        
        # Get frame data from callback
        frame_data = self._frame_callback()
        if frame_data is not None:
            # Send base64-encoded image to JS
            import base64
            base64_data = base64.b64encode(frame_data).decode('ascii')
            self.run_method('updateFrame', base64_data)
    
    def on_frame_request(self, callback: Callable[[], bytes | None]) -> 'AnimatedImage':
        """Set the callback for frame requests.
        
        The callback should return PNG image bytes, or None to skip the frame.
        
        Args:
            callback: Function that returns PNG bytes
            
        Returns:
            Self for method chaining
        """
        self._frame_callback = callback
        return self
    
    def start(self) -> None:
        """Start the animation."""
        self.run_method('setRunning', True)
    
    def stop(self) -> None:
        """Stop the animation."""
        self.run_method('setRunning', False)
    
    async def get_fps(self) -> float:
        """Get the current frames per second.
        
        Returns:
            Current FPS as measured by the client
        """
        return await self.run_method('getFps')
