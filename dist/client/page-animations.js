const pageReduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const pageRevealTargets = [...document.querySelectorAll('[data-reveal]')];

if (!pageReduceMotion && pageRevealTargets.length && 'IntersectionObserver' in window) {
  document.documentElement.classList.add('reveal-ready', 'scrolling-down');
  let pagePreviousScrollY = window.scrollY;
  let pageScrollFrame = false;

  window.addEventListener('scroll', () => {
    if (pageScrollFrame) return;
    pageScrollFrame = true;
    requestAnimationFrame(() => {
      const scrollingUp = window.scrollY < pagePreviousScrollY;
      document.documentElement.classList.toggle('scrolling-up', scrollingUp);
      document.documentElement.classList.toggle('scrolling-down', !scrollingUp);
      pagePreviousScrollY = window.scrollY;
      pageScrollFrame = false;
    });
  }, { passive: true });

  pageRevealTargets.forEach((target, index) => {
    target.classList.add('scroll-reveal');
    target.style.setProperty('--reveal-delay', `${Math.min((index % 3) * 90, 180)}ms`);
  });

  const pageRevealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.target.classList.toggle('is-visible', entry.isIntersecting));
  }, { threshold: .12, rootMargin: '0px 0px -5% 0px' });

  pageRevealTargets.forEach(target => pageRevealObserver.observe(target));
}
