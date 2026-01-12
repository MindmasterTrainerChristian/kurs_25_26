import tkinter as tk
import random
import math
import time
from dataclasses import dataclass

# -----------------------------
# Config
# -----------------------------
W, H = 900, 600
FPS = 60
GRAVITY = 280.0      # px/s^2
AIR_DRAG = 0.985     # per frame-ish (applied with dt)
TRAIL_LEN = 18

SHAPES = ["circle", "star", "heart", "spiral"]
PALETTE = ["#ff4d4d", "#ffd24d", "#7cff4d", "#4dd2ff", "#b84dff", "#ffffff"]

def clamp(x, a, b): return a if x < a else b if x > b else x

# -----------------------------
# Physics objects
# -----------------------------
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: str
    r: float

@dataclass
class Rocket:
    x: float
    y: float
    vx: float
    vy: float
    explode_y: float
    color: str
    shape: str
    trail: list

# -----------------------------
# Shape generators (unit vectors)
# -----------------------------
def shape_vectors(shape: str, n: int):
    """Return list of (dx, dy) roughly unit directions for particle emission."""
    vecs = []

    if shape == "circle":
        for i in range(n):
            a = 2 * math.pi * i / n
            vecs.append((math.cos(a), math.sin(a)))

    elif shape == "star":
        # Emit along alternating radii directions (gives star-like spokes)
        spikes = max(5, n // 10)
        for i in range(n):
            a = 2 * math.pi * (i / n)
            # add a bit of "spikiness" by snapping angles to spike directions sometimes
            if i % 2 == 0:
                a = 2 * math.pi * (round(a / (2 * math.pi / spikes)) / spikes)
            vecs.append((math.cos(a), math.sin(a)))

    elif shape == "heart":
        # Parametric heart curve; convert points to directions
        # x = 16 sin^3 t; y = 13 cos t - 5 cos 2t - 2 cos 3t - cos 4t
        # We want directions from origin => normalize (x, -y) (flip y up)
        for i in range(n):
            t = 2 * math.pi * i / n
            x = 16 * (math.sin(t) ** 3)
            y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            dx, dy = x, -y
            norm = math.hypot(dx, dy) + 1e-9
            vecs.append((dx / norm, dy / norm))

    elif shape == "spiral":
        # Directions that rotate while radius grows; looks like spiral burst
        for i in range(n):
            t = 6 * math.pi * (i / n)   # how many turns
            r = 0.2 + 0.8 * (i / (n - 1 if n > 1 else 1))
            dx = r * math.cos(t)
            dy = r * math.sin(t)
            norm = math.hypot(dx, dy) + 1e-9
            vecs.append((dx / norm, dy / norm))

    else:
        # fallback
        for _ in range(n):
            a = random.random() * 2 * math.pi
            vecs.append((math.cos(a), math.sin(a)))

    return vecs

# -----------------------------
# Show / Engine
# -----------------------------
class FireworksApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Tkinter Fireworks Starter")

        # UI layout
        self.canvas = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        panel = tk.Frame(root)
        panel.grid(row=0, column=1, sticky="ns", padx=8, pady=8)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.shape_var = tk.StringVar(value="circle")
        tk.Label(panel, text="Shape").pack(anchor="w")
        tk.OptionMenu(panel, self.shape_var, *SHAPES).pack(fill="x")

        self.count_var = tk.IntVar(value=140)
        tk.Label(panel, text="Particles").pack(anchor="w", pady=(10,0))
        tk.Scale(panel, from_=40, to=300, orient="horizontal", variable=self.count_var).pack(fill="x")

        self.speed_var = tk.DoubleVar(value=210.0)
        tk.Label(panel, text="Explosion speed").pack(anchor="w", pady=(10,0))
        tk.Scale(panel, from_=80, to=420, resolution=10, orient="horizontal", variable=self.speed_var).pack(fill="x")

        tk.Button(panel, text="Launch (center)", command=lambda: self.launch(W*0.5)).pack(fill="x", pady=(12,4))
        tk.Button(panel, text="Run demo sequence", command=self.start_demo).pack(fill="x", pady=4)
        tk.Button(panel, text="Stop sequence", command=self.stop_sequence).pack(fill="x", pady=4)
        tk.Button(panel, text="Clear", command=self.clear).pack(fill="x", pady=(18,4))

        self.info = tk.Label(panel, text="Click on canvas to launch.", justify="left")
        self.info.pack(anchor="w", pady=(12,0))

        # Bindings
        self.canvas.bind("<Button-1>", self.on_click)

        # State
        self.rockets: list[Rocket] = []
        self.particles: list[Particle] = []

        self.sequence = []       # list of events: {"t": seconds, "x":..., "shape":..., "color":..., "count":..., "speed":...}
        self.seq_running = False
        self.seq_t0 = 0.0
        self.seq_i = 0

        self.last_t = time.perf_counter()
        self.loop()

    def clear(self):
        self.rockets.clear()
        self.particles.clear()

    def on_click(self, e):
        self.launch(e.x)

    def rand_color(self):
        return random.choice(PALETTE)

    def launch(self, x, shape=None, color=None, count=None, speed=None):
        shape = shape or self.shape_var.get()
        color = color or self.rand_color()
        count = int(count if count is not None else self.count_var.get())
        speed = float(speed if speed is not None else self.speed_var.get())

        # Rocket initial conditions
        y0 = H + 10
        vx = random.uniform(-20, 20)
        vy = -random.uniform(360, 520)
        explode_y = random.uniform(H*0.18, H*0.45)

        r = Rocket(x=x, y=y0, vx=vx, vy=vy, explode_y=explode_y, color=color, shape=shape, trail=[])
        # store per-rocket explosion params by embedding in trail (quick hack) or keep dict; let's keep dict:
        r._count = count
        r._speed = speed
        self.rockets.append(r)

    def explode(self, rocket: Rocket):
        n = rocket._count
        base_speed = rocket._speed

        vecs = shape_vectors(rocket.shape, n)

        for (dx, dy) in vecs:
            # speed jitter + inherit some rocket velocity
            s = random.uniform(0.75, 1.15) * base_speed
            vx = dx * s + 0.20 * rocket.vx
            vy = dy * s + 0.20 * rocket.vy

            life = random.uniform(1.0, 1.8)
            rad = random.uniform(1.5, 2.6)
            self.particles.append(Particle(
                x=rocket.x, y=rocket.y,
                vx=vx, vy=vy,
                life=life,
                color=rocket.color,
                r=rad
            ))

        # optional flash
        self.canvas.create_oval(rocket.x-8, rocket.y-8, rocket.x+8, rocket.y+8,
                                outline="", fill="white", tags="draw")

    # -----------------------------
    # Sequence / show
    # -----------------------------
    def start_demo(self):
        # A simple "show" - tweak freely
        self.sequence = []
        t = 0.0
        for k in range(24):
            self.sequence.append({
                "t": t,
                "x": random.uniform(W*0.15, W*0.85),
                "shape": random.choice(SHAPES),
                "color": random.choice(PALETTE),
                "count": random.choice([90, 120, 160, 200]),
                "speed": random.choice([160, 200, 240, 300]),
            })
            # small rhythm variations
            t += random.choice([0.18, 0.22, 0.28, 0.35])

        # finale
        t += 0.8
        for x in [W*0.2, W*0.35, W*0.5, W*0.65, W*0.8]:
            self.sequence.append({"t": t, "x": x, "shape": "star", "color": "white", "count": 240, "speed": 320})
        self.sequence.sort(key=lambda e: e["t"])

        self.seq_running = True
        self.seq_t0 = time.perf_counter()
        self.seq_i = 0

    def stop_sequence(self):
        self.seq_running = False

    def update_sequence(self):
        if not self.seq_running:
            return
        now = time.perf_counter()
        t = now - self.seq_t0

        while self.seq_i < len(self.sequence) and t >= self.sequence[self.seq_i]["t"]:
            e = self.sequence[self.seq_i]
            self.launch(
                e["x"],
                shape=e.get("shape"),
                color=e.get("color"),
                count=e.get("count"),
                speed=e.get("speed"),
            )
            self.seq_i += 1

        if self.seq_i >= len(self.sequence):
            self.seq_running = False

    # -----------------------------
    # Main loop
    # -----------------------------
    def loop(self):
        now = time.perf_counter()
        dt = clamp(now - self.last_t, 0.0, 1/20)  # avoid huge jumps
        self.last_t = now

        self.update_sequence()
        self.step_physics(dt)
        self.draw()

        self.root.after(int(1000 / FPS), self.loop)

    def step_physics(self, dt: float):
        # Rockets
        alive_rockets = []
        for r in self.rockets:
            r.vy += GRAVITY * dt
            r.vx *= AIR_DRAG ** (dt * FPS)
            r.vy *= AIR_DRAG ** (dt * FPS)

            r.x += r.vx * dt
            r.y += r.vy * dt

            # trail
            r.trail.append((r.x, r.y))
            if len(r.trail) > TRAIL_LEN:
                r.trail.pop(0)

            if r.y <= r.explode_y:
                self.explode(r)
            else:
                alive_rockets.append(r)

        self.rockets = alive_rockets

        # Particles
        alive_particles = []
        for p in self.particles:
            p.vy += GRAVITY * dt
            p.vx *= AIR_DRAG ** (dt * FPS)
            p.vy *= AIR_DRAG ** (dt * FPS)

            p.x += p.vx * dt
            p.y += p.vy * dt
            p.life -= dt

            if p.life > 0 and -50 < p.x < W + 50 and -50 < p.y < H + 80:
                alive_particles.append(p)

        self.particles = alive_particles

    def draw(self):
        self.canvas.delete("draw")

        # draw rockets & trails
        for r in self.rockets:
            # trail
            if len(r.trail) >= 2:
                for i in range(len(r.trail) - 1):
                    x1, y1 = r.trail[i]
                    x2, y2 = r.trail[i + 1]
                    self.canvas.create_line(x1, y1, x2, y2, fill=r.color, width=2, tags="draw")

            # rocket head
            self.canvas.create_oval(r.x-3, r.y-3, r.x+3, r.y+3, fill=r.color, outline="", tags="draw")

        # draw particles
        for p in self.particles:
            rr = p.r
            self.canvas.create_oval(p.x-rr, p.y-rr, p.x+rr, p.y+rr, fill=p.color, outline="", tags="draw")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FireworksApp(root)
    root.mainloop()















