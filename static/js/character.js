// Character Playground — 2D arcade controller
// Uses the 9 expression sprites from /img/character/expr_*.png

(function () {
  "use strict";

  const EXPRESSIONS = [
    "neutral", "surprised", "happy",
    "sad",     "angry",     "in_love",
    "sleepy",  "scared",    "smug",
  ];

  // Display labels in 中文
  const LABELS = {
    neutral:   "平靜",
    surprised: "驚訝",
    happy:     "開心",
    sad:       "難過",
    angry:     "生氣",
    in_love:   "戀愛",
    sleepy:    "想睡",
    scared:    "害怕",
    smug:      "得意",
  };

  // Which sprite to use for which state
  const IDLE_SPRITE   = "neutral";
  const WALK_SPRITES  = ["neutral", "smug", "neutral", "scared"]; // 2-frame pseudo walk
  const JUMP_SPRITE   = "surprised";
  const FALL_SPRITE   = "scared";

  const STAGE = document.querySelector(".character-playground .stage");
  const CHAR  = document.querySelector(".character-playground .character");
  const SPRITE = document.querySelector(".character-playground .sprite");
  const PICKER = document.querySelector(".character-playground .picker");
  const STATUS = {
    expr:  document.querySelector(".character-playground [data-status='expr']"),
    state: document.querySelector(".character-playground [data-status='state']"),
    pos:   document.querySelector(".character-playground [data-status='pos']"),
  };

  if (!STAGE || !CHAR || !SPRITE) return;

  // ---- Game state ----
  const state = {
    x: STAGE.clientWidth / 2,        // center of character in stage px
    y: 0,                             // 0 = on ground, positive = above
    vx: 0,                            // velocity x
    vy: 0,                            // velocity y
    facing: 1,                        // 1 = right, -1 = left
    onGround: true,
    currentExpression: IDLE_SPRITE,
    walkFrame: 0,
    walkTimer: 0,
  };

  const KEYS = new Set();
  const SPEED = 280;        // px/sec
  const JUMP_V = 620;       // initial jump velocity (px/sec)
  const GRAVITY = 1800;     // px/sec^2
  const CHAR_W = 160;       // CSS width, must match .character CSS
  const GROUND_OFFSET = 80; // matches .ground height

  // ---- Sprite switching ----
  function setSprite(name) {
    if (state.currentExpression === name) return;
    state.currentExpression = name;
    SPRITE.src = `/img/character/expr_${name}.png`;
    if (STATUS.expr) STATUS.expr.textContent = LABELS[name] || name;
  }

  function setExpression(name) {
    EXPRESSIONS.forEach((n) => {
      const btn = PICKER.querySelector(`[data-expr="${n}"]`);
      if (btn) btn.classList.toggle("active", n === name);
    });
    setSprite(name);
  }

  function cycleExpression() {
    const i = EXPRESSIONS.indexOf(state.currentExpression);
    const next = EXPRESSIONS[(i + 1) % EXPRESSIONS.length];
    setExpression(next);
  }

  // ---- Build picker ----
  EXPRESSIONS.forEach((name) => {
    const btn = document.createElement("button");
    btn.dataset.expr = name;
    btn.innerHTML = `
      <img src="/img/character/expr_${name}.png" alt="${name}" loading="lazy">
      <span>${LABELS[name] || name}</span>
    `;
    btn.addEventListener("click", () => setExpression(name));
    PICKER.appendChild(btn);
  });
  setExpression(IDLE_SPRITE);

  // ---- Character on stage ----
  function applyTransform() {
    const minX = CHAR_W / 2;
    const maxX = STAGE.clientWidth - CHAR_W / 2;
    state.x = Math.max(minX, Math.min(maxX, state.x));

    CHAR.style.left = `${state.x}px`;
    CHAR.style.bottom = `${GROUND_OFFSET + state.y}px`;
    CHAR.classList.toggle("flip", state.facing === -1);
    CHAR.classList.toggle("jumping", !state.onGround);
    CHAR.classList.toggle("idle", state.onGround && Math.abs(state.vx) < 1);
    CHAR.classList.toggle("walking", state.onGround && Math.abs(state.vx) > 1);

    if (STATUS.pos) {
      STATUS.pos.textContent = `${Math.round(state.x)}, ${Math.round(state.y)}`;
    }
  }

  // ---- Dust particles ----
  function spawnDust() {
    for (let i = 0; i < 4; i++) {
      const d = document.createElement("div");
      d.className = "dust";
      d.style.left = `${state.x + (Math.random() - 0.5) * 60}px`;
      d.style.setProperty("--dx", `${(Math.random() * 30 + 15) * (i % 2 === 0 ? 1 : -1)}px`);
      d.style.animation = `dust-puff ${0.4 + Math.random() * 0.3}s ease-out forwards`;
      STAGE.appendChild(d);
      setTimeout(() => d.remove(), 800);
    }
  }

  // ---- Animation loop ----
  let lastT = performance.now();
  function tick(now) {
    const dt = Math.min(0.05, (now - lastT) / 1000);
    lastT = now;

    // input → velocity
    let ax = 0;
    if (KEYS.has("ArrowLeft") || KEYS.has("a") || KEYS.has("A")) ax -= 1;
    if (KEYS.has("ArrowRight") || KEYS.has("d") || KEYS.has("D")) ax += 1;
    state.vx = ax * SPEED;
    if (ax !== 0) state.facing = ax;

    // jump
    if ((KEYS.has(" ") || KEYS.has("Space")) && state.onGround) {
      state.vy = JUMP_V;
      state.onGround = false;
    }

    // physics
    state.vy -= GRAVITY * dt;
    state.y += state.vy * dt;

    if (state.y <= 0) {
      // landed
      if (!state.onGround) {
        CHAR.classList.remove("landed");
        // force reflow to restart animation
        void CHAR.offsetWidth;
        CHAR.classList.add("landed");
        spawnDust();
      }
      state.y = 0;
      state.vy = 0;
      state.onGround = true;
    }

    state.x += state.vx * dt;

    // sprite choice by state
    if (!state.onGround) {
      // jumping up vs falling
      setSprite(state.vy > 0 ? JUMP_SPRITE : FALL_SPRITE);
      if (STATUS.state) STATUS.state.textContent = state.vy > 0 ? "跳" : "落";
    } else if (Math.abs(state.vx) > 1) {
      // walk frame cycle
      state.walkTimer += dt;
      if (state.walkTimer > 0.11) {
        state.walkTimer = 0;
        state.walkFrame = (state.walkFrame + 1) % WALK_SPRITES.length;
      }
      setSprite(WALK_SPRITES[state.walkFrame]);
      if (STATUS.state) STATUS.state.textContent = "走";
    } else {
      // idle — return to current chosen expression after a brief neutral
      if (state.currentExpression !== IDLE_SPRITE && Math.random() < 0.5) {
        setSprite(state.currentExpression);
      }
      if (STATUS.state) STATUS.state.textContent = "停";
    }

    applyTransform();
    requestAnimationFrame(tick);
  }

  // ---- Event listeners ----
  window.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    KEYS.add(e.key);
    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " "].includes(e.key)) {
      e.preventDefault();
    }
  });
  window.addEventListener("keyup", (e) => KEYS.delete(e.key));
  window.addEventListener("blur", () => KEYS.clear());

  // click stage to cycle expression
  STAGE.addEventListener("click", (e) => {
    if (e.target.closest("button")) return; // ignore picker clicks
    cycleExpression();
  });

  // touch: tap to cycle; swipe to move
  let touchStartX = null;
  STAGE.addEventListener("touchstart", (e) => {
    if (e.touches.length === 1) touchStartX = e.touches[0].clientX;
  }, { passive: true });
  STAGE.addEventListener("touchend", (e) => {
    if (touchStartX === null) return;
    const dx = (e.changedTouches[0].clientX - touchStartX);
    touchStartX = null;
    if (Math.abs(dx) < 12) {
      cycleExpression();
    } else {
      state.facing = dx > 0 ? 1 : -1;
      state.vx = state.facing * SPEED;
      setTimeout(() => { state.vx = 0; }, 220);
    }
  }, { passive: true });

  // handle resize / theme-aware
  window.addEventListener("resize", () => {
    // keep character in bounds
    const minX = CHAR_W / 2;
    const maxX = STAGE.clientWidth - CHAR_W / 2;
    if (state.x < minX) state.x = minX;
    if (state.x > maxX) state.x = maxX;
  });

  requestAnimationFrame((t) => { lastT = t; tick(t); });
})();
