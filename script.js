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
