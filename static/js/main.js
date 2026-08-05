// ─────────────────────────────────────────────────────
    // 1. NAVBAR — effet glass + lien actif au scroll
    // ─────────────────────────────────────────────────────
const navbar = document.getElementById('navbar');

if (navbar) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }, { passive: true });
}

    // Marquer le lien actif selon l'URL courante
    document.querySelectorAll('.nav-link').forEach(link => {
      if (link.href === window.location.href) {
        link.classList.add('active');
      }
    });

    // ─────────────────────────────────────────────────────
    // 2. MENU MOBILE — toggle
    // ─────────────────────────────────────────────────────
const menuToggle  = document.getElementById('menu-toggle');
const mobileMenu  = document.getElementById('mobile-menu');
const iconOpen    = document.getElementById('icon-open');
const iconClose   = document.getElementById('icon-close');

if (menuToggle && mobileMenu) {
  menuToggle.addEventListener('click', () => {
    const isOpen = mobileMenu.style.maxHeight && mobileMenu.style.maxHeight !== '0px';

    if (isOpen) {
      mobileMenu.style.maxHeight = '0px';
      if (iconOpen) iconOpen.classList.remove('hidden');
      if (iconClose) iconClose.classList.add('hidden');
      menuToggle.setAttribute('aria-expanded', 'false');
    } else {
      mobileMenu.style.maxHeight = mobileMenu.scrollHeight + 'px';
      if (iconOpen) iconOpen.classList.add('hidden');
      if (iconClose) iconClose.classList.remove('hidden');
      menuToggle.setAttribute('aria-expanded', 'true');
    }
  });
}

    // ─────────────────────────────────────────────────────
    // 3. SCROLL ANIMATIONS — IntersectionObserver
    //    Usage dans les templates enfants :
    //    <div data-animate="fade-up">     ← monte depuis le bas
    //    <div data-animate="fade-left">   ← vient de la gauche
    //    <div data-animate="fade-right">  ← vient de la droite
    //    <div data-animate="zoom">        ← zoom entrant
    //    <div data-animate="tilt">        ← rotation + montée
    //    Optionnel : data-delay="200"     ← délai en ms (100 à 600)
    // ─────────────────────────────────────────────────────
    const animatedEls = document.querySelectorAll('[data-animate]');

    if (animatedEls.length > 0) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('is-visible');
              // On arrête d'observer une fois l'animation déclenchée
              observer.unobserve(entry.target);
            }
          });
        },
        {
          threshold: 0.12,      // déclenche quand 12% de l'élément est visible
          rootMargin: '0px 0px -40px 0px',  // légèrement avant le bord bas
        }
      );

      animatedEls.forEach(el => observer.observe(el));
    }

    // ─────────────────────────────────────────────────────
    // 4. UTILITAIRE — exposer des helpers globaux
    //    Les pages enfants peuvent les utiliser
    // ─────────────────────────────────────────────────────
    window.HB = {
      /**
       * Animer un élément manuellement (sans scroll)
       * Ex: HB.animate(document.querySelector('.hero-title'))
       */
      animate(el) {
        if (el) el.classList.add('is-visible');
      },

      /**
       * Réinitialiser une animation (la rejouer)
       */
      reset(el) {
        if (el) el.classList.remove('is-visible');
      },
    };

// javascript pour la gestion du services des pages 

    document.addEventListener('DOMContentLoaded', function () {
  const services = [
    { title: 'Stratégie & Branding', text: 'Positionnement, identité visuelle et storytelling pour marques créatives.' },
    { title: 'Design Produit', text: 'UI/UX, prototypes et interfaces accessibles et esthétiques.' },
    { title: 'Développement', text: 'Sites, intégrations et expériences performantes sur le web.' }
  ];

  const btn = document.getElementById('welcome-learn-btn');
  const serviceArea = document.getElementById('welcome-service');
  const dots = Array.from(document.querySelectorAll('[data-service-index]'));

  if (!btn || !serviceArea || dots.length === 0) return;

  // compteur stocké en session (reset à fermeture onglet) ; change à localStorage si tu veux persister
  let count = Number(sessionStorage.getItem('welcome_click_count') || 0);

  function showService(idx) {
    const s = services[idx];
    serviceArea.innerHTML = `<strong class="block text-sm text-[#7d3b47]">${s.title}</strong><span class="block mt-1">${s.text}</span>`;
    serviceArea.classList.remove('opacity-0'); serviceArea.classList.add('opacity-100');
    // highlight dots: clear then add active to idx
    dots.forEach(d => d.classList.remove('service-dot-active'));
    const target = dots.find(d => Number(d.dataset.serviceIndex) === idx);
    if (target) target.classList.add('service-dot-active');
  }

  btn.addEventListener('click', function (e) {
    e.preventDefault();
    count += 1;
    sessionStorage.setItem('welcome_click_count', String(count));

    // if 4th click => redirect to services page
    if (count % 4 === 0) {
      // optional: small UX delay for last pulse
      window.location.href = '/services/'; // adapte l'URL si besoin
      return;
    }

    // otherwise show one of the 3 services (cycle 0..2)
    const idx = ( (count - 1) % 3 );
    showService(idx);
  });
});



//  pour gerer la presentation des blogs sur la page du home.html 


