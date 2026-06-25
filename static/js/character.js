// Character Playground — 2D arcade with star-collect mini-game
// Uses the 9 expression sprites from img/character/expr_*.png
//
// Features:
//   - WASD/arrows move, Space jump (gravity + squash/stretch)
//   - 9 expression picker + click character to cycle
//   - Idle bob / walk wiggle / land squash CSS animations
//   - Walking dust trail + landing burst + screen shake
//   - Falling stars (+score) and bombs (-score) mini-game
//   - Web Audio synthesized SFX (jump/land/click/score/hit)
//   - Best score persisted to localStorage

(function () {
  "use strict";

  const EXPRESSIONS = [
    "neutral", "surprised", "happy",
    "sad",     "angry",     "in_love",
    "sleepy",  "scared",    "smug",
  ];
  const LABELS = {
    neutral: "平靜", surprised: "驚訝", happy: "開心",
    sad: "難過", angry: "生氣", in_love: "戀愛",
    sleepy: "想睡", scared: "害怕", smug: "得意",
  };
  const IDLE_SPRITE  = "neutral";
  const WALK_SPRITES = ["neutral", "smug", "neutral", "scared"];
  const JUMP_SPRITE  = "surprised";
  const FALL_SPRITE  = "scared";

  // -------- base path (injected by Hugo shortcode) --------
  const BASE = (typeof window.CHAR_BASE === "string" && window.CHAR_BASE) || "/";

  // -------- DOM refs --------
  const STAGE    = document.querySelector(".character-playground .stage");
  const CHAR     = document.querySelector(".character-playground .character");
  const SPRITE   = document.querySelector(".character-playground .sprite");
  const PICKER   = document.querySelector(".character-playground .picker");
  const STATUS = {
    expr:  document.querySelector(".character-playground [data-status='expr']"),
    state: document.querySelector(".character-playground [data-status='state']"),
    pos:   document.querySelector(".character-playground [data-status='pos']"),
  };
  if (!STAGE || !CHAR || !SPRITE) return;

  // -------- game state --------
  const state = {
    x: STAGE.clientWidth / 2,
    y: 0,
    vx: 0,
    vy: 0,
    facing: 1,
    onGround: true,
    currentExpression: IDLE_SPRITE,
    walkFrame: 0,
    walkTimer: 0,
    runDustTimer: 0,
    score: 0,
    best: 0,
    starSpawnTimer: 0,
    starSpawnInterval: 1.4,
  };
  const KEYS = new Set();
  const SPEED = 280;
  const JUMP_V = 620;
  const GRAVITY = 1800;
  const CHAR_W = 160;
  const GROUND_OFFSET = 80;
  const STARS = []; // {el, x, y, vx, vy, type:'star'|'bomb', alive}

  try { state.best = parseInt(localStorage.getItem("cscs-playground-best") || "0", 10) || 0; }
  catch (_) {}

  // -------- Web Audio SFX --------
  let audioCtx = null;
  let muted = false;
  try { muted = localStorage.getItem("cscs-playground-muted") === "1"; } catch (_) {}

  function ensureAudio() {
    if (audioCtx) return audioCtx;
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (Ctx) audioCtx = new Ctx();
    } catch (_) { audioCtx = null; }
    return audioCtx;
  }

  function play(type) {
    if (muted) return;
    const ctx = ensureAudio();
    if (!ctx) return;
    const t0 = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    switch (type) {
      case "jump":
        osc.type = "square";
        osc.frequency.setValueAtTime(280, t0);
        osc.frequency.exponentialRampToValueAtTime(560, t0 + 0.12);
        gain.gain.setValueAtTime(0.06, t0);
        gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.15);
        osc.start(t0); osc.stop(t0 + 0.16);
        break;
      case "land":
        osc.type = "sine";
        osc.frequency.setValueAtTime(160, t0);
        osc.frequency.exponentialRampToValueAtTime(70, t0 + 0.1);
        gain.gain.setValueAtTime(0.10, t0);
        gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.14);
        osc.start(t0); osc.stop(t0 + 0.15);
        break;
      case "click":
        osc.type = "triangle";
        osc.frequency.setValueAtTime(700, t0);
        osc.frequency.exponentialRampToValueAtTime(500, t0 + 0.08);
        gain.gain.setValueAtTime(0.05, t0);
        gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.1);
        osc.start(t0); osc.stop(t0 + 0.11);
        break;
      case "score":
        osc.type = "triangle";
        osc.frequency.setValueAtTime(660, t0);
        osc.frequency.setValueAtTime(880, t0 + 0.06);
        osc.frequency.setValueAtTime(1100, t0 + 0.12);
        gain.gain.setValueAtTime(0.07, t0);
        gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.22);
        osc.start(t0); osc.stop(t0 + 0.23);
        break;
      case "hit":
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(220, t0);
        osc.frequency.exponentialRampToValueAtTime(60, t0 + 0.25);
        gain.gain.setValueAtTime(0.08, t0);
        gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.3);
        osc.start(t0); osc.stop(t0 + 0.31);
        break;
    }
  }

  // First user gesture unlocks audio (browser policy)
  window.addEventListener("keydown", ensureAudio, { once: true });
  STAGE.addEventListener("click", ensureAudio, { once: true });

  // -------- sprite switching --------
  function setSprite(name) {
    if (state.currentExpression === name) return;
    state.currentExpression = name;
    SPRITE.src = `${BASE}img/character/expr_${name}.png`;
    if (STATUS.expr) STATUS.expr.textContent = LABELS[name] || name;
  }

  function setExpression(name) {
    EXPRESSIONS.forEach((n) => {
      const btn = PICKER.querySelector(`[data-expr="${n}"]`);
      if (btn) btn.classList.toggle("active", n === name);
    });
    setSprite(name);
    play("click");
  }

  function cycleExpression() {
    const i = EXPRESSIONS.indexOf(state.currentExpression);
    setExpression(EXPRESSIONS[(i + 1) % EXPRESSIONS.length]);
  }

  // -------- build picker --------
  EXPRESSIONS.forEach((name) => {
    const btn = document.createElement("button");
    btn.dataset.expr = name;
    btn.innerHTML = `
      <img src="${BASE}img/character/expr_${name}.png" alt="${name}" loading="lazy">
      <span>${LABELS[name] || name}</span>
    `;
    btn.addEventListener("click", () => setExpression(name));
    PICKER.appendChild(btn);
  });
  setExpression(IDLE_SPRITE);

  // -------- HUD additions (score + sound toggle) --------
  const hudRight = document.createElement("div");
  hudRight.className = "hud-right";
  hudRight.innerHTML = `
    <div class="score-panel">
      分數<span class="big" id="score-val">0</span>
      <span class="best">最高 <span id="best-val">${state.best}</span></span>
    </div>
    <button class="sound-toggle ${muted ? "muted" : ""}" id="sound-btn" aria-label="音效開關" title="音效開關">${muted ? "🔇" : "🔊"}</button>
  `;
  STAGE.appendChild(hudRight);

  const SCORE_EL = document.getElementById("score-val");
  const BEST_EL  = document.getElementById("best-val");
  const SOUND_BTN = document.getElementById("sound-btn");

  function setScore(n) {
    state.score = Math.max(0, n | 0);
    SCORE_EL.textContent = state.score;
    if (state.score > state.best) {
      state.best = state.score;
      BEST_EL.textContent = state.best;
      try { localStorage.setItem("cscs-playground-best", String(state.best)); } catch (_) {}
    }
  }

  SOUND_BTN.addEventListener("click", () => {
    muted = !muted;
    SOUND_BTN.textContent = muted ? "🔇" : "🔊";
    SOUND_BTN.classList.toggle("muted", muted);
    try { localStorage.setItem("cscs-playground-muted", muted ? "1" : "0"); } catch (_) {}
    if (!muted) play("click");
  });

  // -------- visual feedback: floating score text --------
  function popScore(x, y, amount, isLoss) {
    const el = document.createElement("div");
    el.className = "score-pop " + (isLoss ? "lose" : "gain");
    el.textContent = (isLoss ? "" : "+") + amount;
    el.style.left = `${x}px`;
    el.style.top  = `${y}px`;
    STAGE.appendChild(el);
    setTimeout(() => el.remove(), 900);
  }

  // -------- screen shake --------
  function shake(ms) {
    STAGE.classList.remove("shake");
    void STAGE.offsetWidth;
    STAGE.classList.add("shake");
    setTimeout(() => STAGE.classList.remove("shake"), ms);
  }

  // -------- dust particles (continuous when running + burst on land) --------
  function spawnDust(burst) {
    if (burst) {
      for (let i = 0; i < 5; i++) {
        const d = document.createElement("div");
        d.className = "dust";
        d.style.left = `${state.x + (Math.random() - 0.5) * 60}px`;
        d.style.setProperty("--dx", `${(Math.random() * 30 + 15) * (i % 2 === 0 ? 1 : -1)}px`);
        d.style.animation = `dust-puff ${0.4 + Math.random() * 0.3}s ease-out forwards`;
        STAGE.appendChild(d);
        setTimeout(() => d.remove(), 800);
      }
    } else {
      // continuous trail — single small dust
      const d = document.createElement("div");
      d.className = "dust";
      const dir = state.facing;
      d.style.left = `${state.x + (Math.random() * 20 - 10) - dir * 30}px`;
      d.style.setProperty("--dx", `${-dir * (15 + Math.random() * 15)}px`);
      d.style.animation = `dust-puff ${0.35 + Math.random() * 0.2}s ease-out forwards`;
      d.style.opacity = "0.6";
      STAGE.appendChild(d);
      setTimeout(() => d.remove(), 600);
    }
  }

  // -------- falling stars / bombs --------
  function spawnStar() {
    const isBomb = Math.random() < 0.25;
    const el = document.createElement("div");
    el.className = isBomb ? "bomb" : "star";
    if (isBomb) {
      el.innerHTML = '<div class="body"></div><div class="fuse"></div><div class="spark"></div>';
    }
    const w = STAGE.clientWidth;
    STAGE.appendChild(el);
    STARS.push({
      el,
      x: 40 + Math.random() * (w - 80),
      y: -30,
      vx: (Math.random() - 0.5) * 60,
      vy: 0,
      type: isBomb ? "bomb" : "star",
      alive: true,
    });
  }

  function stepStars(dt) {
    for (const s of STARS) {
      if (!s.alive) continue;
      s.vy += GRAVITY * 0.5 * dt;
      s.x += s.vx * dt;
      s.y += s.vy * dt;
      s.el.style.left = `${s.x}px`;
      s.el.style.top  = `${s.y}px`;

      // Catch collision — character's mouth area roughly at state.x, ground+state.y + 80
      const cx = state.x;
      const cy = GROUND_OFFSET + state.y + CHAR_W * 0.4; // body center
      const dx = s.x - cx;
      const dy = s.y - cy;
      const hit = (dx * dx + dy * dy) < (CHAR_W * 0.5) * (CHAR_W * 0.5);
      if (hit) {
        s.alive = false;
        s.el.remove();
        if (s.type === "star") {
          setScore(state.score + 1);
          popScore(s.x, s.y, 1, false);
          play("score");
        } else {
          setScore(state.score - 3);
          popScore(s.x, s.y, -3, true);
          play("hit");
          // Force sad/scared expression briefly
          setSprite("scared");
          shake(220);
        }
        continue;
      }

      // Off-screen bottom
      if (s.y > STAGE.clientHeight + 30) {
        s.alive = false;
        s.el.remove();
      }
    }
    // compact array
    for (let i = STARS.length - 1; i >= 0; i--) {
      if (!STARS[i].alive) STARS.splice(i, 1);
    }
  }

  // -------- main loop --------
  let lastT = performance.now();
  function tick(now) {
    const dt = Math.min(0.05, (now - lastT) / 1000);
    lastT = now;

    // input → velocity
    let ax = 0;
    if (KEYS.has("ArrowLeft")  || KEYS.has("a") || KEYS.has("A")) ax -= 1;
    if (KEYS.has("ArrowRight") || KEYS.has("d") || KEYS.has("D")) ax += 1;
    state.vx = ax * SPEED;
    if (ax !== 0) state.facing = ax;

    // jump
    if ((KEYS.has(" ") || KEYS.has("Space")) && state.onGround) {
      state.vy = JUMP_V;
      state.onGround = false;
      play("jump");
    }

    // physics
    state.vy -= GRAVITY * dt;
    state.y  += state.vy * dt;
    const wasInAir = !state.onGround;
    if (state.y <= 0) {
      if (wasInAir) {
        CHAR.classList.remove("landed");
        void CHAR.offsetWidth;
        CHAR.classList.add("landed");
        spawnDust(true);
        play("land");
        shake(180);
      }
      state.y = 0;
      state.vy = 0;
      state.onGround = true;
    }

    state.x += state.vx * dt;

    // Sprite choice by state — user-selected expression wins when idle;
    // movement/jump uses action poses so the character feels alive.
    if (!state.onGround) {
      setSprite(state.vy > 0 ? JUMP_SPRITE : FALL_SPRITE);
      if (STATUS.state) STATUS.state.textContent = state.vy > 0 ? "跳" : "落";
    } else if (Math.abs(state.vx) > 1) {
      state.walkTimer += dt;
      if (state.walkTimer > 0.11) {
        state.walkTimer = 0;
        state.walkFrame = (state.walkFrame + 1) % WALK_SPRITES.length;
      }
      setSprite(WALK_SPRITES[state.walkFrame]);
      if (STATUS.state) STATUS.state.textContent = "走";
      // Continuous running dust trail
      state.runDustTimer += dt;
      if (state.runDustTimer > 0.18) {
        state.runDustTimer = 0;
        spawnDust(false);
      }
    } else {
      if (state.currentExpression !== IDLE_SPRITE) {
        setSprite(state.currentExpression);
      }
      if (STATUS.state) STATUS.state.textContent = "停";
    }

    applyTransform();
    stepStars(dt);

    // Star spawning — ramps up as score climbs
    state.starSpawnTimer += dt;
    state.starSpawnInterval = Math.max(0.45, 1.4 - state.score * 0.02);
    if (state.starSpawnTimer >= state.starSpawnInterval) {
      state.starSpawnTimer = 0;
      spawnStar();
    }

    requestAnimationFrame(tick);
  }

  // -------- apply transform --------
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
    if (STATUS.pos) STATUS.pos.textContent = `${Math.round(state.x)}, ${Math.round(state.y)}`;
  }

  // -------- input listeners --------
  window.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    KEYS.add(e.key);
    if (["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"," "].includes(e.key)) e.preventDefault();
  });
  window.addEventListener("keyup",   (e) => KEYS.delete(e.key));
  window.addEventListener("blur",    () => KEYS.clear());

  STAGE.addEventListener("click", (e) => {
    if (e.target.closest("button")) return;
    cycleExpression();
  });

  // touch
  let touchStartX = null;
  STAGE.addEventListener("touchstart", (e) => {
    if (e.touches.length === 1) touchStartX = e.touches[0].clientX;
  }, { passive: true });
  STAGE.addEventListener("touchend", (e) => {
    if (touchStartX === null) return;
    const dx = e.changedTouches[0].clientX - touchStartX;
    touchStartX = null;
    if (Math.abs(dx) < 12) { cycleExpression(); }
    else {
      state.facing = dx > 0 ? 1 : -1;
      state.vx = state.facing * SPEED;
      setTimeout(() => { state.vx = 0; }, 220);
    }
  }, { passive: true });

  window.addEventListener("resize", () => {
    const minX = CHAR_W / 2;
    const maxX = STAGE.clientWidth - CHAR_W / 2;
    if (state.x < minX) state.x = minX;
    if (state.x > maxX) state.x = maxX;
  });

  requestAnimationFrame((t) => { lastT = t; tick(t); });
})();
