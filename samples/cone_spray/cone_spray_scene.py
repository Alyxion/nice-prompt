"""Custom Three.js Cone Spray Scene Component."""

from typing_extensions import Self

from nicegui.element import Element


class ConeSprayScene(Element, component='cone_spray.js'):
    """A Three.js hollow cone nozzle spray visualization component.
    
    This component renders a realistic hollow cone spray pattern with
    particle physics including gravity and air resistance.
    """

    def __init__(
        self,
        *,
        inner_angle: float = 25.0,
        outer_angle: float = 35.0,
        flow_rate: int = 500,
        particle_size: float = 0.02,
        initial_velocity: float = 8.0,
        gravity: float = 9.81,
        air_resistance: float = 0.5,
        spread_randomness: float = 0.15,
    ) -> None:
        """Initialize the cone spray scene.
        
        :param inner_angle: Inner cone angle in degrees
        :param outer_angle: Outer cone angle in degrees
        :param flow_rate: Particles emitted per second
        :param particle_size: Base particle size
        :param initial_velocity: Initial spray velocity
        :param gravity: Gravity strength (m/s²)
        :param air_resistance: Air resistance coefficient
        :param spread_randomness: Random spread factor (0-1)
        """
        super().__init__()
        self._props['inner_angle'] = inner_angle
        self._props['outer_angle'] = outer_angle
        self._props['flow_rate'] = flow_rate
        self._props['particle_size'] = particle_size
        self._props['initial_velocity'] = initial_velocity
        self._props['gravity'] = gravity
        self._props['air_resistance'] = air_resistance
        self._props['spread_randomness'] = spread_randomness

    def set_inner_angle(self, angle: float) -> Self:
        """Set the inner cone angle."""
        self._props['inner_angle'] = angle
        self.update()
        return self

    def set_outer_angle(self, angle: float) -> Self:
        """Set the outer cone angle."""
        self._props['outer_angle'] = angle
        self.update()
        return self

    def set_flow_rate(self, rate: int) -> Self:
        """Set the particle flow rate."""
        self._props['flow_rate'] = rate
        self.update()
        return self

    def set_particle_size(self, size: float) -> Self:
        """Set the particle size."""
        self._props['particle_size'] = size
        self.update()
        return self

    def set_initial_velocity(self, velocity: float) -> Self:
        """Set the initial spray velocity."""
        self._props['initial_velocity'] = velocity
        self.update()
        return self

    def set_gravity(self, gravity: float) -> Self:
        """Set the gravity strength."""
        self._props['gravity'] = gravity
        self.update()
        return self

    def set_air_resistance(self, resistance: float) -> Self:
        """Set the air resistance coefficient."""
        self._props['air_resistance'] = resistance
        self.update()
        return self

    def set_spread_randomness(self, randomness: float) -> Self:
        """Set the spread randomness factor."""
        self._props['spread_randomness'] = randomness
        self.update()
        return self

    def reset_camera(self) -> None:
        """Reset the camera to default position."""
        self.run_method('resetCamera')

    def toggle_pause(self) -> None:
        """Toggle pause state of the simulation."""
        self.run_method('togglePause')

    def clear_particles(self) -> None:
        """Clear all particles from the scene."""
        self.run_method('clearParticles')
