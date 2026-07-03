<template>
  <div class="skeleton-wrap">
    <div class="skeleton-header">
      <div class="skeleton-line" style="width: 40%;"></div>
    </div>
    <div class="skeleton-grid">
      <div class="skeleton-card">
        <div class="skeleton-line" style="width: 70%;"></div>
        <div class="skeleton-line" style="width: 50%;"></div>
        <div class="skeleton-line" style="width: 90%;"></div>
      </div>
      <div class="skeleton-card">
        <div class="skeleton-line" style="width: 60%;"></div>
        <div class="skeleton-line" style="width: 80%;"></div>
        <div class="skeleton-line" style="width: 45%;"></div>
      </div>
    </div>
    <div class="skeleton-block">
      <div class="skeleton-line" style="width: 30%;"></div>
      <div class="skeleton-line" style="width: 100%;"></div>
      <div class="skeleton-line" style="width: 85%;"></div>
      <div class="skeleton-line" style="width: 60%;"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-wrap {
  display: flex; flex-direction: column; gap: 14px;
  padding: 16px 4px;
  animation: fadeIn .25s ease;
}
@keyframes fadeIn {
  from { opacity: 0; } to { opacity: 1; }
}
.skeleton-header {
  padding: 10px 0 6px;
}
.skeleton-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 14px;
}
.skeleton-card, .skeleton-block {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  display: flex; flex-direction: column; gap: 10px;
}
.skeleton-block { grid-column: 1 / -1; }
.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, var(--panel-2) 25%, var(--panel-3) 50%, var(--panel-2) 75%);
  background-size: 200% 100%;
  border-radius: 6px;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
