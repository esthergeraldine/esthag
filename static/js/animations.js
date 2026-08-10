/**
 * =====================================================
 * ANIMATIONS.JS — Animations, scrolls & interactions
 * =====================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initDarkMode();
  initScrollReveal();
  initLegacyReveal(); // Pour .reveal class (ancien système)
  initParallax();
  initSmoothScroll();
  initAnimatedCounters();
  initHoverEffects();
  initNavbarScrollEffects();
});

/**
 * ─────────────────────────────────────────────────────
 * DARK MODE — Toggle avec persistence
 * ─────────────────────────────────────────────────────
 */
function initDarkMode() {
  const themeToggle = document.getElementById('theme-toggle');
  const sunIcon = document.getElementById('sun-icon');
  const moonIcon = document.getElementById('moon-icon');

  if (!themeToggle) return;

  function updateIcons(isDark) {
    if (sunIcon && moonIcon) {
      sunIcon.classList.toggle('hidden', !isDark);
      moonIcon.classList.toggle('hidden', isDark);
    }
  }

  // Sync icons on load
  const isDark = document.documentElement.classList.contains('dark');
  updateIcons(isDark);

  themeToggle.addEventListener('click', () => {
    const nowDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', nowDark ? 'dark' : 'light');
    updateIcons(nowDark);
  });
}

/**
 * ─────────────────────────────────────────────────────
 * 1. SCROLL REVEAL — IntersectionObserver
 *    Usage: <div data-reveal="fade-up" data-delay="200">
 * ─────────────────────────────────────────────────────
 */
function initScrollReveal() {
  const reveals = document.querySelectorAll('[data-reveal]');
  if (!reveals.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const delay = entry.target.dataset.delay || 0;
          setTimeout(() => {
            entry.target.classList.add('is-revealed');
          }, delay);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
  );

  reveals.forEach((el) => observer.observe(el));
}

/**
 * ─────────────────────────────────────────────────────
 * 1b. LEGACY REVEAL — Pour .reveal class (ancien système)
 *    Usage: <div class="reveal">
 * ─────────────────────────────────────────────────────
 */
function initLegacyReveal() {
  const reveals = document.querySelectorAll('.reveal');
  if (!reveals.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
  );

  reveals.forEach((el) => observer.observe(el));
}

/**
 * ─────────────────────────────────────────────────────
 * 2. PARALLAX — effet de profondeur au scroll
 *    Usage: <div data-parallax="0.5">
 * ─────────────────────────────────────────────────────
 */
function initParallax() {
  const parallaxEls = document.querySelectorAll('[data-parallax]');
  if (!parallaxEls.length) return;

  function updateParallax() {
    const scrollY = window.scrollY;
    parallaxEls.forEach((el) => {
      const speed = parseFloat(el.dataset.parallax) || 0.3;
      const rect = el.getBoundingClientRect();
      const inView = rect.top < window.innerHeight && rect.bottom > 0;
      if (inView) {
        const offset = (rect.top - window.innerHeight / 2) * speed;
        el.style.transform = `translateY(${offset}px)`;
      }
    });
  }

  window.addEventListener('scroll', updateParallax, { passive: true });
  updateParallax();
}

/**
 * ─────────────────────────────────────────────────────
 * 3. SMOOTH SCROLL — défilement fluide vers les ancres
 * ─────────────────────────────────────────────────────
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/**
 * ─────────────────────────────────────────────────────
 * 4. ANIMATED COUNTERS — compteurs animés au scroll
 *    Usage: <span data-counter="150" data-suffix="+">
 * ─────────────────────────────────────────────────────
 */
function initAnimatedCounters() {
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  counters.forEach((el) => observer.observe(el));
}

function animateCounter(el) {
  const target = parseInt(el.dataset.counter) || 0;
  const suffix = el.dataset.suffix || '';
  const duration = 1500;
  const start = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(eased * target);
    el.textContent = current + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

/**
 * ─────────────────────────────────────────────────────
 * 5. HOVER EFFECTS — effets au survol
 * ─────────────────────────────────────────────────────
 */
function initHoverEffects() {
  // Carte hover lift
  document.querySelectorAll('[data-hover="lift"]').forEach((card) => {
    card.addEventListener('mouseenter', () => {
      card.classList.add('is-lifted');
    });
    card.addEventListener('mouseleave', () => {
      card.classList.remove('is-lifted');
    });
  });

  // Bouton ripple effect
  document.querySelectorAll('[data-ripple]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const ripple = document.createElement('span');
      ripple.className = 'ripple-effect';
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });
}

/**
 * ─────────────────────────────────────────────────────
 * 6. NAVBAR SCROLL EFFECTS — changement d'état au scroll
 * ─────────────────────────────────────────────────────
 */
function initNavbarScrollEffects() {
  const navbar = document.querySelector('[data-navbar]');
  if (!navbar) return;

  let lastScroll = 0;

  window.addEventListener(
    'scroll',
    () => {
      const currentScroll = window.scrollY;

      // Add/remove scrolled class
      if (currentScroll > 50) {
        navbar.classList.add('navbar-scrolled');
      } else {
        navbar.classList.remove('navbar-scrolled');
      }

      // Hide/show navbar on scroll
      if (currentScroll > lastScroll && currentScroll > 200) {
        navbar.classList.add('navbar-hidden');
      } else {
        navbar.classList.remove('navbar-hidden');
      }

      lastScroll = currentScroll;
    },
    { passive: true }
  );
}

/**
 * ─────────────────────────────────────────────────────
 * 7. STAGGERED ANIMATION — apparition en cascade
 *    Usage: <div data-stagger-parent>
 *             <div data-stagger-child>
 * ─────────────────────────────────────────────────────
 */
document.querySelectorAll('[data-stagger-parent]').forEach((parent) => {
  const children = parent.querySelectorAll('[data-stagger-child]');
  const delay = parseInt(parent.dataset.staggerDelay) || 100;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          children.forEach((child, index) => {
            setTimeout(() => {
              child.classList.add('is-revealed');
            }, index * delay);
          });
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  observer.observe(parent);
});

/**
 * ─────────────────────────────────────────────────────
 * 8. SCROLL PROGRESS BAR — barre de progression
 *    Usage: <div id="scroll-progress">
 * ─────────────────────────────────────────────────────
 */
const scrollProgressBar = document.getElementById('scroll-progress');
if (scrollProgressBar) {
  window.addEventListener(
    'scroll',
    () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (scrollTop / docHeight) * 100;
      scrollProgressBar.style.width = progress + '%';
    },
    { passive: true }
  );
}

/**
 * ─────────────────────────────────────────────────────
 * 9. CURSOR TRAIL — effet de traînée au curseur
 *    Usage: <div id="cursor-trail">
 * ─────────────────────────────────────────────────────
 */
const cursorTrail = document.getElementById('cursor-trail');
if (cursorTrail) {
  let trailVisible = false;
  let isOnInteractive = false;

  document.addEventListener('mousemove', (e) => {
    // Hide on interactive elements
    const target = e.target;
    isOnInteractive = target.closest('button, a, input, textarea, select, [data-no-trail]');

    if (isOnInteractive) {
      cursorTrail.style.opacity = '0';
      return;
    }

    if (!trailVisible) {
      cursorTrail.style.opacity = '1';
      trailVisible = true;
    }
    cursorTrail.style.left = e.clientX + 'px';
    cursorTrail.style.top = e.clientY + 'px';
  });

  document.addEventListener('mouseleave', () => {
    cursorTrail.style.opacity = '0';
    trailVisible = false;
  });
}

/**
 * ─────────────────────────────────────────────────────
 * 10. TYPEWRITER EFFECT — effet de machine à écrire
 *    Usage: <span data-typewriter="Bonjour, je suis développeur">
 * ─────────────────────────────────────────────────────
 */
document.querySelectorAll('[data-typewriter]').forEach((el) => {
  const text = el.dataset.typewriter;
  const speed = parseInt(el.dataset.typeSpeed) || 80;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          typeWriter(el, text, speed);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  observer.observe(el);
});

function typeWriter(el, text, speed) {
  let i = 0;
  el.textContent = '';
  function type() {
    if (i < text.length) {
      el.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  type();
}

/**
 * ─────────────────────────────────────────────────────
 * 11. TILT EFFECT — effet 3D au survol
 *    Usage: <div data-tilt data-tilt-intensity="10">
 * ─────────────────────────────────────────────────────
 */
document.querySelectorAll('[data-tilt]').forEach((el) => {
  el.addEventListener('mousemove', (e) => {
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const intensity = parseFloat(el.dataset.tiltIntensity) || 10;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * intensity;
    const rotateY = ((centerX - x) / centerX) * intensity;

    el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  });

  el.addEventListener('mouseleave', () => {
    el.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
  });
});

/**
 * ─────────────────────────────────────────────────────
 * 12. LAZY LOAD IMAGES — chargement différé
 *    Usage: <img data-lazy="/path/to/image.jpg">
 * ─────────────────────────────────────────────────────
 */
document.querySelectorAll('[data-lazy]').forEach((img) => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          img.src = img.dataset.lazy;
          img.removeAttribute('data-lazy');
          observer.unobserve(img);
        }
      });
    },
    { rootMargin: '100px' }
  );

  observer.observe(img);
});
