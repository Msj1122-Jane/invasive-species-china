import re

filepath = r'C:\Users\lenovo\WorkBuddy\2026-07-20-00-14-33\index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_css = """/* ============================================
   CHAPTER 0: 序章 . 封面 + 叙事引言
   ============================================ */
#chapter-intro {
  height: auto;
  min-height: 100vh;
  color: var(--b-text);
  position: relative;
  background:
    radial-gradient(ellipse 80% 60% at 50% 35%, rgba(245,158,11,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 30% 70%, rgba(34,197,94,0.04) 0%, transparent 60%),
    var(--b-bg);
  padding: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

#chapter-intro::before {
  content: '';
  position: absolute;
  top: 18%;
  left: 50%;
  transform: translateX(-50%);
  width: 1px;
  height: 70px;
  background: linear-gradient(180deg, rgba(245,158,11,0.3), transparent);
  pointer-events: none;
  z-index: 0;
}
#chapter-intro::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 160px;
  background: linear-gradient(180deg, transparent 0%, rgba(11,20,16,0.7) 60%, var(--b-bg) 100%);
  pointer-events: none;
  z-index: 9;
}

.page-flip-wrapper {
  position: sticky;
  top: 0;
  height: 100vh;
  width: 100%;
  z-index: 10;
  perspective: 1800px;
  perspective-origin: 50% 50%;
  overflow: hidden;
}
.page-flip-inner {
  width: 100%;
  height: 100%;
  transform-origin: 50% 100%;
  backface-visibility: hidden;
  position: relative;
}
.page-flip-inner::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to top, rgba(11,20,16,0.5) 0%, transparent 45%);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease;
  z-index: 5;
}
.page-flip-inner.flipping::after { opacity: 1; }

#chapter-intro { position: relative; z-index: 10; }
#chapter-map { position: relative; z-index: 5; }

.intro-content {
  position: relative;
  z-index: 3;
  max-width: 680px;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.intro-big-number {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  color: var(--b-gold);
  border: 1px solid rgba(245,158,11,0.25);
  border-radius: 4px;
  padding: 5px 16px;
  margin-bottom: 3.5vh;
  opacity: 0;
  animation: introFadeSlide 1s 0.15s ease forwards;
}

.intro-main-title {
  font-family: var(--font-serif);
  font-size: clamp(3.2rem, 8vw, 5.6rem);
  font-weight: 700;
  line-height: 1.1;
  margin: 0 0 2.5vh 0;
  letter-spacing: 0.08em;
  color: var(--b-text);
  opacity: 0;
  animation: introFadeSlide 1.1s 0.35s ease forwards;
}

.intro-eng-title {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--b-text-dim);
  font-weight: 300;
  margin: 0 0 2vh 0;
  opacity: 0;
  animation: introFadeSlide 1.1s 0.5s ease forwards;
}

.intro-tagline {
  font-family: var(--font-sans);
  font-size: 0.9rem;
  color: var(--b-text-dim);
  max-width: 420px;
  line-height: 1.7;
  margin: 0;
  opacity: 0;
  animation: introFadeSlide 1.2s 0.65s ease forwards;
}

@keyframes introFadeSlide {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.intro-scroll-hint {
  position: absolute;
  bottom: 36px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  z-index: 10;
  opacity: 0;
  animation: introFadeSlide 1.2s 0.9s ease forwards;
}
.scroll-arrow-anim {
  width: 26px;
  height: 42px;
  border: 1.5px solid rgba(255,255,255,0.2);
  border-radius: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.scroll-arrow-anim svg {
  width: 13px;
  height: 20px;
  animation: scrollArrowDown 1.5s ease-in-out infinite;
}
@keyframes scrollArrowDown {
  0%, 100% { transform: translateY(-3px); opacity: 0.4; }
  50% { transform: translateY(3px); opacity: 1; }
}
.scroll-hint-text {
  font-size: 0.65rem;
  color: rgba(255,255,255,0.25);
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.intro-narrative {
  width: 100%;
  max-width: 680px;
  margin: 0 auto;
  padding: 110px 24px 100px;
  position: relative;
  z-index: 11;
  background: var(--b-bg);
}
.intro-narrative::before {
  content: '';
  position: absolute;
  top: -60px;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(180deg, rgba(11,20,16,0) 0%, var(--b-bg) 100%);
  pointer-events: none;
}
.narrative-text {
  font-family: var(--font-serif);
  font-size: clamp(1rem, 1.8vw, 1.15rem);
  line-height: 2.1;
  color: var(--b-text-dim);
  padding: 0;
  text-align: center;
  max-width: 640px;
  margin: 0 auto;
}
.narrative-text p {
  font-size: inherit;
  line-height: inherit;
  color: inherit;
  margin: 0 0 28px;
}
.narrative-em {
  color: var(--b-gold);
  font-weight: 600;
  font-family: var(--font-mono);
}
.narrative-big {
  font-family: var(--font-mono);
  font-size: 1.3em;
  color: var(--b-gold);
  font-weight: 700;
}
.narrative-divider {
  border: none;
  border-top: 1px solid rgba(255,255,255,0.1);
  width: 48px;
  margin: 36px auto;
}
.narrative-data {
  font-size: 1em !important;
}
.narrative-closing {
  color: var(--b-text-dim) !important;
  font-style: italic;
  margin-top: 12px !important;
}
"""

# Replace lines 282-518 (0-indexed: 282-517)
with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines[:282] + [new_css + '\n'] + lines[518:])

print('Done! Lines 283-518 replaced.')
