const slides = [...document.querySelectorAll('.hero-slide')];
const dots = [...document.querySelectorAll('.hero-dot')];
let activeSlide = 0;
let carouselTimer;

function showSlide(index) {
  activeSlide = (index + slides.length) % slides.length;
  slides.forEach((slide, position) => slide.classList.toggle('is-active', position === activeSlide));
  dots.forEach((dot, position) => {
    dot.classList.toggle('is-active', position === activeSlide);
    dot.setAttribute('aria-current', position === activeSlide ? 'true' : 'false');
  });
}

function startCarousel() {
  window.clearInterval(carouselTimer);
  carouselTimer = window.setInterval(() => showSlide(activeSlide + 1), 6500);
}

dots.forEach((dot, index) => dot.addEventListener('click', () => {
  showSlide(index);
  startCarousel();
}));

document.getElementById('year').textContent = new Date().getFullYear();
showSlide(0);
startCarousel();

// Refined section and card reveals while scrolling.
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!reduceMotion && 'IntersectionObserver' in window) {
  document.documentElement.classList.add('reveal-ready', 'scrolling-down');
  let previousScrollY = window.scrollY;
  let scrollFrameRequested = false;

  window.addEventListener('scroll', () => {
    if (scrollFrameRequested) return;
    scrollFrameRequested = true;
    window.requestAnimationFrame(() => {
      const scrollingUp = window.scrollY < previousScrollY;
      document.documentElement.classList.toggle('scrolling-up', scrollingUp);
      document.documentElement.classList.toggle('scrolling-down', !scrollingUp);
      previousScrollY = window.scrollY;
      scrollFrameRequested = false;
    });
  }, { passive: true });

  const revealGroups = [
    ['.intro-grid > *', ''],
    ['.section-heading > *', ''],
    ['.service-card', ''],
    ['.solution-grid article', ''],
    ['.project-card', ''],
    ['.knowhow-copy', 'reveal-left'],
    ['.knowhow-panel', 'reveal-right'],
    ['.partners-row > *', ''],
    ['.group-card', ''],
    ['.location-copy', 'reveal-left'],
    ['.location-map', 'reveal-right'],
    ['.contact-grid > *', ''],
    ['.footer-grid > *', '']
  ];

  revealGroups.forEach(([selector, direction]) => {
    document.querySelectorAll(selector).forEach((element, index) => {
      element.classList.add('scroll-reveal');
      if (direction) element.classList.add(direction);
      element.style.setProperty('--reveal-delay', `${Math.min(index * 90, 360)}ms`);
    });
  });

  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      entry.target.classList.toggle('is-visible', entry.isIntersecting);
    });
  }, { threshold: 0.14, rootMargin: '0px 0px -7% 0px' });

  document.querySelectorAll('.scroll-reveal').forEach(element => revealObserver.observe(element));

  const sectionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      entry.target.classList.toggle('section-entered', entry.isIntersecting);
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.section, .contact-cta').forEach(section => sectionObserver.observe(section));
}
