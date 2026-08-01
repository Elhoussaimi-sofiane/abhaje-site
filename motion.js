(function () {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGsap = typeof window.gsap !== 'undefined';
  const hasScrollTrigger = typeof window.ScrollTrigger !== 'undefined';

  if (reduceMotion || !hasGsap || !hasScrollTrigger) return;

  const { gsap, ScrollTrigger } = window;
  gsap.registerPlugin(ScrollTrigger);
  document.documentElement.classList.add('motion-ready');

  if (typeof window.Lenis !== 'undefined') {
    const lenis = new window.Lenis({
      duration: 1.05,
      smoothWheel: true,
      anchors: { offset: -84 }
    });

    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
    window.abhajeLenis = lenis;
  }

  const revealSelectors = [
    '[data-reveal]',
    '.intro-grid > *',
    '.section-heading > *',
    '.service-card',
    '.solution-grid article',
    '.project-card',
    '.knowhow-copy',
    '.knowhow-panel',
    '.partners-row > *',
    '.group-card',
    '.location-copy',
    '.location-map',
    '.contact-grid > *',
    '.footer-grid > *'
  ];

  const revealTargets = [...new Set(
    revealSelectors.flatMap((selector) => [...document.querySelectorAll(selector)])
  )];

  const entrance = (element, fromAbove) => {
    const horizontal = element.classList.contains('reveal-left')
      ? -44
      : element.classList.contains('reveal-right')
        ? 44
        : 0;

    gsap.killTweensOf(element);
    gsap.fromTo(element, {
      autoAlpha: 0.12,
      x: horizontal,
      y: fromAbove ? -38 : 38,
      scale: 0.985,
      filter: 'blur(5px)'
    }, {
      autoAlpha: 1,
      x: 0,
      y: 0,
      scale: 1,
      filter: 'blur(0px)',
      duration: 0.85,
      ease: 'power3.out',
      overwrite: true
    });
  };

  revealTargets.forEach((element, index) => {
    element.classList.add('gsap-reveal');
    gsap.set(element, {
      autoAlpha: 0.12,
      y: 38,
      scale: 0.985,
      filter: 'blur(5px)'
    });

    ScrollTrigger.create({
      trigger: element,
      start: 'top 91%',
      end: 'bottom 9%',
      onEnter: () => gsap.delayedCall(Math.min(index % 4, 3) * 0.055, () => entrance(element, false)),
      onEnterBack: () => entrance(element, true),
      onLeave: () => gsap.to(element, {
        autoAlpha: 0.16,
        y: -28,
        scale: 0.99,
        filter: 'blur(3px)',
        duration: 0.45,
        ease: 'power2.in',
        overwrite: true
      }),
      onLeaveBack: () => gsap.to(element, {
        autoAlpha: 0.16,
        y: 28,
        scale: 0.99,
        filter: 'blur(3px)',
        duration: 0.45,
        ease: 'power2.in',
        overwrite: true
      })
    });
  });

  document.querySelectorAll(
    '.project-card img, .group-media img, .progress-card img, .content-feature img, .location-visual img'
  ).forEach((image) => {
    const trigger = image.closest('article, .content-feature, .location-visual') || image;
    gsap.fromTo(image, {
      '--motion-scale': 0.96,
      '--motion-y': '-2%'
    }, {
      '--motion-scale': 1.035,
      '--motion-y': '3%',
      ease: 'none',
      scrollTrigger: {
        trigger,
        start: 'top bottom',
        end: 'bottom top',
        scrub: 0.65
      }
    });
  });

  document.querySelectorAll(
    '.section-title, .content-heading h2, .realisations-heading h2, .page-hero h1'
  ).forEach((title) => {
    gsap.fromTo(title, {
      opacity: 0.38,
      y: 18
    }, {
      opacity: 1,
      y: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: title,
        start: 'top 92%',
        end: 'top 48%',
        scrub: 0.45
      }
    });
  });

  window.addEventListener('load', () => ScrollTrigger.refresh(), { once: true });
})();
