---
title: "角色 Playground"
date: 2026-06-25
draft: false
description: "把書裡的角色拿來玩 — 2D 街機風格小互動"
---

## 試試看

點角色換表情、方向鍵或 WASD 移動、空白鍵跳。試試看哪個表情最像你今天讀書的狀態。

<link rel="stylesheet" href="/css/character.css">

<div class="character-playground">
  <div class="stage">
    <div class="hills" aria-hidden="true">
      <div class="hill hill-1"></div>
      <div class="hill hill-2"></div>
      <div class="hill hill-3"></div>
      <div class="hill hill-4"></div>
    </div>
    <div class="ground" aria-hidden="true"></div>
    <div class="character idle" id="char">
      <img class="sprite" src="/img/character/expr_neutral.png" alt="character" draggable="false">
      <div class="shadow" aria-hidden="true"></div>
    </div>
    <div class="hud" aria-hidden="true">
      <div><span class="kbd">←</span> <span class="kbd">→</span> / <span class="kbd">A</span> <span class="kbd">D</span> 移動</div>
      <div><span class="kbd">Space</span> 跳躍</div>
      <div>點角色 = 換下一個表情</div>
    </div>
  </div>

  <div class="picker" aria-label="表情選擇"></div>

  <div class="status" aria-live="polite">
    <span>表情：<strong data-status="expr">平靜</strong></span>
    <span>動作：<strong data-status="state">停</strong></span>
    <span>位置：<strong data-status="pos">—</strong></span>
  </div>
</div>

<script src="/js/character.js" defer></script>

## 為什麼做這個

讀書讀到腦袋打結時，總需要一個小出口。這隻綠色毛怪本來只是書裡的插圖，把它從靜態 PNG 變成可以在螢幕上跑、跳、換表情的角色，是個好玩的小 side project。

也是「讓學過的東西換個形式活過來」的練習 — 把單純的素材做成可以互動的東西，比純讀一次印象深刻。
