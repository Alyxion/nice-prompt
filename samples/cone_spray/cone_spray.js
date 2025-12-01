// cone_spray.js - Three.js hollow cone nozzle spray visualization
// Demonstrates: particle physics, canvas textures, emission accumulator, WeakMap pattern

import SceneLib from "nicegui-scene";
const { THREE, OrbitControls } = SceneLib;

// Store Three.js objects outside Vue reactivity to avoid proxy conflicts
const threeState = new WeakMap();

export default {
  template: `<div ref="container" style="width: 100%; height: 100%;"></div>`,

  props: {
    inner_angle: { type: Number, default: 25 },
    outer_angle: { type: Number, default: 35 },
    flow_rate: { type: Number, default: 500 },
    particle_size: { type: Number, default: 0.02 },
    initial_velocity: { type: Number, default: 8 },
    gravity: { type: Number, default: 9.81 },
    air_resistance: { type: Number, default: 0.5 },
    spread_randomness: { type: Number, default: 0.15 },
    resource_path: String,
  },

  data() {
    return {
      animationId: null,
      isPaused: false,
    };
  },

  mounted() {
    threeState.set(this, {
      scene: null,
      camera: null,
      renderer: null,
      controls: null,
      clock: null,
      particles: [],
      particleGeometry: null,
      particleMaterial: null,
      particleMesh: null,
      nozzle: null,
      maxParticles: 15000,
      particleIndex: 0,
      positions: null,
      colors: null,
      sizes: null,
      velocities: [],
      lifetimes: [],
      ages: [],
      emitAccumulator: 0,
    });

    this.$nextTick(() => {
      this.initScene();
      this.createNozzle();
      this.createParticleSystem();
      this.animate();
    });
  },

  beforeUnmount() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    const state = this.getState();
    if (state) {
      if (state.renderer) {
        state.renderer.dispose();
      }
      if (state.particleGeometry) {
        state.particleGeometry.dispose();
      }
      if (state.particleMaterial) {
        state.particleMaterial.dispose();
      }
    }
  },

  watch: {
    inner_angle() { this.updateSprayParameters(); },
    outer_angle() { this.updateSprayParameters(); },
    flow_rate() { this.updateSprayParameters(); },
    particle_size() { this.updateParticleSize(); },
    initial_velocity() { this.updateSprayParameters(); },
  },

  methods: {
    getState() {
      return threeState.get(this);
    },

    initScene() {
      const state = this.getState();
      const container = this.$refs.container;

      // Scene
      state.scene = new THREE.Scene();
      state.scene.background = new THREE.Color(0x1a1a2e);
      state.scene.fog = new THREE.Fog(0x1a1a2e, 10, 50);

      // Camera - positioned to see the spray from the side
      const aspect = container.clientWidth / container.clientHeight;
      state.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
      state.camera.position.set(6, 0, 6);
      state.camera.lookAt(0, -2, 0);

      // Renderer
      state.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      state.renderer.setSize(container.clientWidth, container.clientHeight);
      state.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      state.renderer.shadowMap.enabled = true;
      state.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      container.appendChild(state.renderer.domElement);

      // Controls
      state.controls = new OrbitControls(state.camera, state.renderer.domElement);
      state.controls.enableDamping = true;
      state.controls.dampingFactor = 0.05;
      state.controls.target.set(0, -2, 0);

      // Clock
      state.clock = new THREE.Clock();

      // Lighting setup for metallic materials
      // Strong ambient light for base illumination
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
      state.scene.add(ambientLight);
      
      // Hemisphere light for natural sky/ground lighting
      const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1.0);
      hemiLight.position.set(0, 20, 0);
      state.scene.add(hemiLight);

      // Main key light
      const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
      directionalLight.position.set(5, 10, 5);
      directionalLight.castShadow = true;
      directionalLight.shadow.mapSize.width = 2048;
      directionalLight.shadow.mapSize.height = 2048;
      state.scene.add(directionalLight);
      
      // Fill light from opposite side
      const directionalLight2 = new THREE.DirectionalLight(0xffffff, 1.0);
      directionalLight2.position.set(-5, 8, -5);
      state.scene.add(directionalLight2);
      
      // Front fill light
      const directionalLight3 = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight3.position.set(0, 5, 10);
      state.scene.add(directionalLight3);

      // Rim/back light for edge highlights
      const backLight = new THREE.DirectionalLight(0xffffff, 0.6);
      backLight.position.set(0, 5, -10);
      state.scene.add(backLight);

      // Point lights for specular highlights
      const pointLight = new THREE.PointLight(0xffffff, 1.0, 30);
      pointLight.position.set(-3, 3, 3);
      state.scene.add(pointLight);
      
      const pointLight2 = new THREE.PointLight(0xffffff, 0.8, 30);
      pointLight2.position.set(3, 2, -3);
      state.scene.add(pointLight2);
      
      const pointLight3 = new THREE.PointLight(0xffffff, 0.6, 30);
      pointLight3.position.set(0, -2, 5);
      state.scene.add(pointLight3);

      // Ground plane
      const groundGeometry = new THREE.PlaneGeometry(20, 20);
      const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x2d2d44,
        roughness: 0.8,
        metalness: 0.2,
      });
      const ground = new THREE.Mesh(groundGeometry, groundMaterial);
      ground.rotation.x = -Math.PI / 2;
      ground.position.y = -5;
      ground.receiveShadow = true;
      state.scene.add(ground);

      // Grid helper
      const gridHelper = new THREE.GridHelper(20, 20, 0x444466, 0x333355);
      gridHelper.position.y = -4.99;
      state.scene.add(gridHelper);

      // Handle resize
      window.addEventListener('resize', this.onWindowResize.bind(this));
    },

    createNozzle() {
      const state = this.getState();
      
      // Material for all nozzle parts - realistic brushed stainless steel
      const steelMaterial = new THREE.MeshStandardMaterial({
        color: 0xd4d4d4,
        metalness: 0.85,
        roughness: 0.25,
      });

      // Create nozzle group
      const nozzleGroup = new THREE.Group();

      // Top hexagonal nut (6-sided cylinder)
      const hexNutGeometry = new THREE.CylinderGeometry(0.22, 0.22, 0.25, 6);
      const hexNut = new THREE.Mesh(hexNutGeometry, steelMaterial);
      hexNut.position.y = 0.45;
      hexNut.castShadow = true;
      nozzleGroup.add(hexNut);
      
      // Chamfered top edge
      const chamferTopGeometry = new THREE.CylinderGeometry(0.18, 0.22, 0.06, 6);
      const chamferTop = new THREE.Mesh(chamferTopGeometry, steelMaterial);
      chamferTop.position.y = 0.35;
      chamferTop.castShadow = true;
      nozzleGroup.add(chamferTop);

      // Middle cylindrical body
      const bodyGeometry = new THREE.CylinderGeometry(0.18, 0.18, 0.15, 32);
      const body = new THREE.Mesh(bodyGeometry, steelMaterial);
      body.position.y = 0.25;
      body.castShadow = true;
      nozzleGroup.add(body);
      
      // Transition ring
      const ringGeometry = new THREE.CylinderGeometry(0.2, 0.18, 0.04, 32);
      const transitionRing = new THREE.Mesh(ringGeometry, steelMaterial);
      transitionRing.position.y = 0.155;
      transitionRing.castShadow = true;
      nozzleGroup.add(transitionRing);

      // Conical tip section (outer)
      const coneOuterGeometry = new THREE.CylinderGeometry(0.2, 0.1, 0.25, 32);
      const coneOuter = new THREE.Mesh(coneOuterGeometry, steelMaterial);
      coneOuter.position.y = 0.01;
      coneOuter.castShadow = true;
      nozzleGroup.add(coneOuter);

      // Bottom flat ring around the orifice
      const bottomRingGeometry = new THREE.RingGeometry(0.04, 0.1, 32);
      const bottomRing = new THREE.Mesh(bottomRingGeometry, steelMaterial);
      bottomRing.rotation.x = -Math.PI / 2;
      bottomRing.position.y = -0.115;
      nozzleGroup.add(bottomRing);

      // Inner hole (dark)
      const holeMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a1a2e,
        metalness: 0.1,
        roughness: 0.9,
      });
      
      // Inner cone cavity
      const innerConeGeometry = new THREE.CylinderGeometry(0.04, 0.08, 0.15, 32);
      const innerCone = new THREE.Mesh(innerConeGeometry, holeMaterial);
      innerCone.position.y = -0.04;
      nozzleGroup.add(innerCone);

      state.scene.add(nozzleGroup);
      state.nozzle = nozzleGroup;
    },

    createParticleSystem() {
      const state = this.getState();
      const maxParticles = state.maxParticles;

      // Create geometry with buffer attributes
      state.particleGeometry = new THREE.BufferGeometry();
      state.positions = new Float32Array(maxParticles * 3);
      state.colors = new Float32Array(maxParticles * 3);
      state.sizes = new Float32Array(maxParticles);

      // Initialize all particles as invisible (at origin with size 0)
      for (let i = 0; i < maxParticles; i++) {
        state.positions[i * 3] = 0;
        state.positions[i * 3 + 1] = -100; // Below visible area
        state.positions[i * 3 + 2] = 0;
        state.colors[i * 3] = 0.3;
        state.colors[i * 3 + 1] = 0.7;
        state.colors[i * 3 + 2] = 1.0;
        state.sizes[i] = 0;
        state.velocities.push(new THREE.Vector3());
        state.lifetimes.push(0);
        state.ages.push(0);
      }

      state.particleGeometry.setAttribute('position', new THREE.BufferAttribute(state.positions, 3));
      state.particleGeometry.setAttribute('color', new THREE.BufferAttribute(state.colors, 3));
      state.particleGeometry.setAttribute('size', new THREE.BufferAttribute(state.sizes, 1));

      // Create circular sprite texture for round particles
      const canvas = document.createElement('canvas');
      canvas.width = 64;
      canvas.height = 64;
      const ctx = canvas.getContext('2d');
      
      // Draw a radial gradient circle (sphere-like)
      const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
      gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
      gradient.addColorStop(0.3, 'rgba(200, 230, 255, 0.8)');
      gradient.addColorStop(0.6, 'rgba(100, 180, 255, 0.5)');
      gradient.addColorStop(1, 'rgba(50, 150, 255, 0)');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(32, 32, 32, 0, Math.PI * 2);
      ctx.fill();
      
      const spriteTexture = new THREE.CanvasTexture(canvas);
      
      // Point material with sprite texture for round particles
      state.particleMaterial = new THREE.PointsMaterial({
        size: 0.15,
        map: spriteTexture,
        transparent: true,
        opacity: 0.9,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        sizeAttenuation: true,
        vertexColors: false,
      });

      state.particleMesh = new THREE.Points(state.particleGeometry, state.particleMaterial);
      state.particleMesh.frustumCulled = false;  // Prevent particles from disappearing
      state.scene.add(state.particleMesh);
      
      // Compute initial bounding sphere for frustum culling
      state.particleGeometry.computeBoundingSphere();
    },

    emitParticles(deltaTime) {
      const state = this.getState();
      if (!state.emitAccumulator) state.emitAccumulator = 0;
      
      // Use accumulator for smooth emission at any frame rate
      const flowRate = this.flow_rate || 500;
      state.emitAccumulator += flowRate * deltaTime;
      const particlesToEmit = Math.floor(state.emitAccumulator);
      state.emitAccumulator -= particlesToEmit;

      for (let i = 0; i < particlesToEmit; i++) {
        const idx = state.particleIndex % state.maxParticles;

        // Calculate hollow cone direction
        // Random angle around the cone
        const phi = Math.random() * Math.PI * 2;
        
        // Angle from vertical (between inner and outer cone angles)
        const innerRad = (this.inner_angle * Math.PI) / 180;
        const outerRad = (this.outer_angle * Math.PI) / 180;
        
        // Random angle between inner and outer cone with some spread
        let theta = innerRad + Math.random() * (outerRad - innerRad);
        
        // Add some randomness for more natural look
        theta += (Math.random() - 0.5) * this.spread_randomness * (outerRad - innerRad);
        theta = Math.max(innerRad * 0.8, Math.min(outerRad * 1.2, theta));

        // Direction vector (pointing downward)
        const direction = new THREE.Vector3(
          Math.sin(theta) * Math.cos(phi),
          -Math.cos(theta),
          Math.sin(theta) * Math.sin(phi)
        );

        // Add velocity variation
        const velocityMagnitude = this.initial_velocity * (0.9 + Math.random() * 0.2);
        
        // Set initial position (at nozzle tip)
        const startY = -0.12;
        state.positions[idx * 3] = direction.x * 0.04;
        state.positions[idx * 3 + 1] = startY;
        state.positions[idx * 3 + 2] = direction.z * 0.04;

        // Set velocity
        state.velocities[idx].copy(direction).multiplyScalar(velocityMagnitude);

        // Set color (water-like blue with variation)
        const hue = 0.55 + Math.random() * 0.1; // Blue range
        const saturation = 0.6 + Math.random() * 0.3;
        const lightness = 0.5 + Math.random() * 0.3;
        const color = new THREE.Color().setHSL(hue, saturation, lightness);
        state.colors[idx * 3] = color.r;
        state.colors[idx * 3 + 1] = color.g;
        state.colors[idx * 3 + 2] = color.b;

        // Set size
        state.sizes[idx] = 1.0;

        // Set lifetime (2-4 seconds)
        state.lifetimes[idx] = 2 + Math.random() * 2;
        state.ages[idx] = 0;

        state.particleIndex++;
      }
    },

    updateParticles(deltaTime) {
      const state = this.getState();
      const gravity = new THREE.Vector3(0, -this.gravity, 0);

      for (let i = 0; i < state.maxParticles; i++) {
        if (state.sizes[i] <= 0) continue;

        state.ages[i] += deltaTime;

        // Check if particle is dead
        if (state.ages[i] >= state.lifetimes[i] || state.positions[i * 3 + 1] < -5) {
          state.sizes[i] = 0;
          state.positions[i * 3 + 1] = -100;
          continue;
        }

        // Get current velocity
        const vel = state.velocities[i];

        // Apply gravity
        vel.add(gravity.clone().multiplyScalar(deltaTime));

        // Apply air resistance (drag)
        const speed = vel.length();
        if (speed > 0) {
          const dragForce = vel.clone().normalize().multiplyScalar(-this.air_resistance * speed * speed * deltaTime);
          vel.add(dragForce);
        }

        // Update position
        state.positions[i * 3] += vel.x * deltaTime;
        state.positions[i * 3 + 1] += vel.y * deltaTime;
        state.positions[i * 3 + 2] += vel.z * deltaTime;

        // Fade out near end of life
        const lifeRatio = state.ages[i] / state.lifetimes[i];
        if (lifeRatio > 0.7) {
          state.sizes[i] *= 0.98;
        }

        // Color shift as particle ages (becomes more transparent/white)
        if (lifeRatio > 0.5) {
          state.colors[i * 3] = Math.min(1, state.colors[i * 3] + deltaTime * 0.5);
          state.colors[i * 3 + 1] = Math.min(1, state.colors[i * 3 + 1] + deltaTime * 0.3);
        }
      }

      // Update buffer attributes - REQUIRED for dynamic geometry
      state.particleGeometry.attributes.position.needsUpdate = true;
      state.particleGeometry.attributes.color.needsUpdate = true;
      state.particleGeometry.attributes.size.needsUpdate = true;
    },

    animate() {
      const state = this.getState();
      if (!state || !state.renderer) return;

      this.animationId = requestAnimationFrame(() => this.animate());

      if (!state.clock) return;
      
      const deltaTime = Math.min(state.clock.getDelta(), 0.1);

      if (!this.isPaused) {
        // Emit new particles
        this.emitParticles(deltaTime);

        // Update existing particles
        this.updateParticles(deltaTime);
      }

      state.controls.update();
      state.renderer.render(state.scene, state.camera);
    },

    onWindowResize() {
      const state = this.getState();
      if (!state || !state.camera || !state.renderer) return;

      const container = this.$refs.container;
      if (!container) return;

      state.camera.aspect = container.clientWidth / container.clientHeight;
      state.camera.updateProjectionMatrix();
      state.renderer.setSize(container.clientWidth, container.clientHeight);
    },

    updateSprayParameters() {
      // Parameters are reactive and will be used in next emit cycle
    },

    updateParticleSize() {
      // Will affect newly emitted particles
    },

    // Methods callable from Python
    resetCamera() {
      const state = this.getState();
      if (state && state.camera && state.controls) {
        state.camera.position.set(3, 2, 5);
        state.controls.target.set(0, -2, 0);
        state.controls.update();
      }
    },

    togglePause() {
      this.isPaused = !this.isPaused;
      return this.isPaused;
    },

    clearParticles() {
      const state = this.getState();
      if (!state) return;

      for (let i = 0; i < state.maxParticles; i++) {
        state.sizes[i] = 0;
        state.positions[i * 3 + 1] = -100;
      }
      state.particleGeometry.attributes.position.needsUpdate = true;
      state.particleGeometry.attributes.size.needsUpdate = true;
    },
  },
};
