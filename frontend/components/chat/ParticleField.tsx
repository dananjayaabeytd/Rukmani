"use client";

/**
 * The chat's animated background: soft purple particles drifting upwards,
 * a few twinkling gold "gift sparkles", faint lines between particles that
 * are close, and a gentle push away from the pointer.
 *
 * Kept light on purpose: one canvas, at most ~70 particles (fewer on
 * phones), paused while the tab is hidden, and a still picture for people
 * who ask their system for reduced motion.
 */

import { useEffect, useRef } from "react";

// Kapruka palette (globals.css) as RGB, for canvas colours with alpha.
const PURPLES = ["87, 59, 145", "64, 41, 112", "156, 144, 181"]; // brand-light, brand, brand-muted
const GOLDS = ["248, 218, 8", "255, 184, 0"]; // sun, gold

const LINK_DISTANCE = 120; // px: particles closer than this are joined by a line
const POINTER_RADIUS = 140; // px: how far the pointer pushes particles away

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  colour: string;
  gold: boolean;
  phase: number; // for twinkling
}

function makeParticle(width: number, height: number, anywhere: boolean): Particle {
  const gold = Math.random() < 0.15;
  return {
    x: Math.random() * width,
    // New particles rise in from just below the bottom edge.
    y: anywhere ? Math.random() * height : height + 10,
    vx: (Math.random() - 0.5) * 0.15,
    vy: -(0.08 + Math.random() * 0.22),
    radius: gold ? 1.2 + Math.random() * 1.6 : 1 + Math.random() * 2.2,
    colour: gold
      ? GOLDS[Math.floor(Math.random() * GOLDS.length)]
      : PURPLES[Math.floor(Math.random() * PURPLES.length)],
    gold,
    phase: Math.random() * Math.PI * 2,
  };
}

export function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (!canvas || !context) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const pointer = { x: -9999, y: -9999 };
    let particles: Particle[] = [];
    let width = 0;
    let height = 0;
    let frame = 0;

    function resize() {
      const rect = canvas!.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      width = rect.width;
      height = rect.height;
      canvas!.width = width * ratio;
      canvas!.height = height * ratio;
      context!.setTransform(ratio, 0, 0, ratio, 0, 0);
      // About one particle per 14,000 px², between 25 and 70.
      const count = Math.max(25, Math.min(70, Math.round((width * height) / 14000)));
      particles = Array.from({ length: count }, () => makeParticle(width, height, true));
    }

    function draw(time: number) {
      context!.clearRect(0, 0, width, height);

      // Lines between nearby particles (purple only, very faint).
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i];
        if (a.gold) continue;
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j];
          if (b.gold) continue;
          const distance = Math.hypot(a.x - b.x, a.y - b.y);
          if (distance < LINK_DISTANCE) {
            context!.strokeStyle = `rgba(87, 59, 145, ${0.12 * (1 - distance / LINK_DISTANCE)})`;
            context!.lineWidth = 1;
            context!.beginPath();
            context!.moveTo(a.x, a.y);
            context!.lineTo(b.x, b.y);
            context!.stroke();
          }
        }
      }

      for (const p of particles) {
        const twinkle = p.gold ? 0.55 + 0.45 * Math.sin(time / 600 + p.phase) : 1;
        const alpha = (p.gold ? 0.9 : 0.35) * twinkle;
        if (p.gold) {
          // A soft glow behind each sparkle.
          context!.fillStyle = `rgba(${p.colour}, ${0.18 * twinkle})`;
          context!.beginPath();
          context!.arc(p.x, p.y, p.radius * 3.5, 0, Math.PI * 2);
          context!.fill();
        }
        context!.fillStyle = `rgba(${p.colour}, ${alpha})`;
        context!.beginPath();
        context!.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        context!.fill();
      }
    }

    function step(time: number) {
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        // Gentle push away from the pointer.
        const dx = p.x - pointer.x;
        const dy = p.y - pointer.y;
        const distance = Math.hypot(dx, dy);
        if (distance < POINTER_RADIUS && distance > 0) {
          const force = (1 - distance / POINTER_RADIUS) * 0.6;
          p.x += (dx / distance) * force;
          p.y += (dy / distance) * force;
        }
        p.x += p.vx + Math.sin(time / 3000 + p.phase) * 0.05; // slight sway
        p.y += p.vy;
        // Past the top or the sides: start again from the bottom.
        if (p.y < -10 || p.x < -20 || p.x > width + 20) particles[i] = makeParticle(width, height, false);
      }
      draw(time);
      frame = requestAnimationFrame(step);
    }

    function onPointerMove(event: PointerEvent) {
      const rect = canvas!.getBoundingClientRect();
      pointer.x = event.clientX - rect.left;
      pointer.y = event.clientY - rect.top;
    }

    function onVisibility() {
      cancelAnimationFrame(frame);
      if (!document.hidden && !reducedMotion) frame = requestAnimationFrame(step);
    }

    resize();
    if (reducedMotion) {
      draw(0); // a still picture
    } else {
      frame = requestAnimationFrame(step);
    }

    const observer = new ResizeObserver(() => {
      resize();
      if (reducedMotion) draw(0);
    });
    observer.observe(canvas);
    window.addEventListener("pointermove", onPointerMove);
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener("pointermove", onPointerMove);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, []);

  return <canvas ref={canvasRef} aria-hidden className="pointer-events-none absolute inset-0 size-full" />;
}
