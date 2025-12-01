# Hollow Cone Nozzle Spray

<!-- animated -->

A NiceGUI application using Three.js to visualize a hollow cone nozzle spraying particles with realistic physics.

![Animation](animated.gif)

## Features

- **Hollow cone spray pattern** with adjustable inner/outer angles
- **Particle physics** with gravity and air resistance
- **Real-time controls** for all spray parameters
- **Metallic nozzle** with proper lighting for MeshStandardMaterial
- **Round particles** using canvas texture (not square points)
- **Frame-rate independent** emission using accumulator pattern

## Patterns Demonstrated

### Three.js Integration
- WeakMap pattern for Vue/Three.js reactivity isolation
- Canvas texture for round/spherical particles
- Multi-directional lighting for metallic materials
- `frustumCulled = false` for dynamic particle systems
- `needsUpdate = true` for BufferGeometry attributes

### Particle System
- Emission accumulator for smooth, frame-rate-independent emission
- Hollow cone geometry with configurable angles
- Physics simulation (gravity, air resistance/drag)
- Particle lifecycle management (spawn, update, death)

### NiceGUI Patterns
- Custom Element with `component='cone_spray.js'`
- Props for Python → JavaScript communication
- `run_method()` for calling JS methods from Python
- Real-time slider controls with immediate feedback

## Running

```bash
cd samples/cone_spray
python main.py
```

Then open http://localhost:8080

## Controls

- **Cone Angle**: Inner and outer spray cone angles
- **Flow Rate**: Particles emitted per second
- **Velocity**: Initial spray velocity
- **Droplet Size**: Particle size
- **Spread**: Randomness in spray direction
- **Gravity**: Downward acceleration
- **Air Resistance**: Drag coefficient

Mouse controls:
- Left-click + drag: Rotate view
- Right-click + drag: Pan
- Scroll: Zoom
