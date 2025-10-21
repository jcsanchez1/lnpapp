/**
 * ====================================
 * LNV FRAMEWORK - CAROUSEL
 * Sistema de carrusel/slider con soporte táctil
 * ====================================
 */

const LNVCarousel = (function() {
  'use strict';

  /**
   * Clase Carousel
   */
  class Carousel {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('Carousel: Elemento no encontrado');
        return;
      }

      // Configuración por defecto
      this.config = {
        autoplay: false,
        interval: 5000,
        loop: true,
        speed: 300,
        slidesPerView: 1,
        spaceBetween: 0,
        navigation: true,
        pagination: true,
        keyboard: true,
        touch: true,
        pauseOnHover: true,
        effect: 'slide', // 'slide' o 'fade'
        breakpoints: {},
        onSlideChange: null,
        onInit: null,
        ...options
      };

      this.currentIndex = 0;
      this.slides = [];
      this.isAnimating = false;
      this.autoplayTimer = null;
      this.touchStartX = 0;
      this.touchEndX = 0;

      this.init();
    }

    init() {
      // Obtener slides
      this.track = this.container.querySelector('.lnv-carousel-track');
      this.slides = Array.from(this.container.querySelectorAll('.lnv-carousel-slide'));

      if (this.slides.length === 0) {
        console.warn('Carousel: No se encontraron slides');
        return;
      }

      // Aplicar configuración responsive
      this.applyBreakpoint();

      // Crear controles
      if (this.config.navigation) {
        this.createNavigation();
      }

      if (this.config.pagination) {
        this.createPagination();
      }

      // Setup
      this.setupSlides();
      this.updateSlide(0, false);

      // Event listeners
      this.attachEvents();

      // Autoplay
      if (this.config.autoplay) {
        this.startAutoplay();
      }

      // Callback
      if (this.config.onInit) {
        this.config.onInit(this);
      }

      console.log('✅ Carousel inicializado');
    }

    setupSlides() {
      // Aplicar estilos al track
      this.track.style.display = 'flex';
      this.track.style.transition = `transform ${this.config.speed}ms ease-in-out`;

      // Aplicar estilos a cada slide
      this.slides.forEach(slide => {
        const slideWidth = `calc((100% - ${this.config.spaceBetween * (this.config.slidesPerView - 1)}px) / ${this.config.slidesPerView})`;
        slide.style.minWidth = slideWidth;
        slide.style.marginRight = `${this.config.spaceBetween}px`;
      });

      // Último slide sin margen
      if (this.slides.length > 0) {
        this.slides[this.slides.length - 1].style.marginRight = '0';
      }
    }

    createNavigation() {
      // Botón anterior
      const prevBtn = document.createElement('button');
      prevBtn.className = 'lnv-carousel-prev';
      prevBtn.innerHTML = '‹';
      prevBtn.setAttribute('aria-label', 'Anterior');

      // Botón siguiente
      const nextBtn = document.createElement('button');
      nextBtn.className = 'lnv-carousel-next';
      nextBtn.innerHTML = '›';
      nextBtn.setAttribute('aria-label', 'Siguiente');

      this.container.appendChild(prevBtn);
      this.container.appendChild(nextBtn);

      this.prevBtn = prevBtn;
      this.nextBtn = nextBtn;

      // Events
      prevBtn.addEventListener('click', () => this.prev());
      nextBtn.addEventListener('click', () => this.next());
    }

    createPagination() {
      const pagination = document.createElement('div');
      pagination.className = 'lnv-carousel-pagination';

      const totalPages = Math.ceil(this.slides.length / this.config.slidesPerView);

      for (let i = 0; i < totalPages; i++) {
        const dot = document.createElement('button');
        dot.className = 'lnv-carousel-dot';
        dot.setAttribute('aria-label', `Ir a slide ${i + 1}`);
        dot.addEventListener('click', () => this.goTo(i * this.config.slidesPerView));
        pagination.appendChild(dot);
      }

      this.container.appendChild(pagination);
      this.pagination = pagination;
      this.dots = Array.from(pagination.querySelectorAll('.lnv-carousel-dot'));
    }

    attachEvents() {
      // Keyboard
      if (this.config.keyboard) {
        document.addEventListener('keydown', (e) => {
          if (e.key === 'ArrowLeft') this.prev();
          if (e.key === 'ArrowRight') this.next();
        });
      }

      // Touch
      if (this.config.touch) {
        this.track.addEventListener('touchstart', (e) => {
          this.touchStartX = e.touches[0].clientX;
        }, { passive: true });

        this.track.addEventListener('touchmove', (e) => {
          this.touchEndX = e.touches[0].clientX;
        }, { passive: true });

        this.track.addEventListener('touchend', () => {
          this.handleSwipe();
        });
      }

      // Pause on hover
      if (this.config.pauseOnHover && this.config.autoplay) {
        this.container.addEventListener('mouseenter', () => this.stopAutoplay());
        this.container.addEventListener('mouseleave', () => this.startAutoplay());
      }

      // Responsive
      window.addEventListener('resize', () => {
        this.applyBreakpoint();
        this.updateSlide(this.currentIndex, false);
      });
    }

    handleSwipe() {
      const swipeThreshold = 50;
      const diff = this.touchStartX - this.touchEndX;

      if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
          this.next();
        } else {
          this.prev();
        }
      }

      this.touchStartX = 0;
      this.touchEndX = 0;
    }

    applyBreakpoint() {
      const width = window.innerWidth;
      const breakpoints = Object.keys(this.config.breakpoints)
        .map(Number)
        .sort((a, b) => b - a);

      for (const bp of breakpoints) {
        if (width >= bp) {
          Object.assign(this.config, this.config.breakpoints[bp]);
          this.setupSlides();
          break;
        }
      }
    }

    updateSlide(index, animate = true) {
      if (this.isAnimating) return;

      // Validar index
      const maxIndex = this.slides.length - this.config.slidesPerView;
      
      if (!this.config.loop) {
        index = Math.max(0, Math.min(index, maxIndex));
      } else {
        if (index < 0) {
          index = maxIndex;
        } else if (index > maxIndex) {
          index = 0;
        }
      }

      this.currentIndex = index;

      // Calcular desplazamiento
      const slideWidth = this.slides[0].offsetWidth;
      const offset = -(index * (slideWidth + this.config.spaceBetween));

      // Aplicar transformación
      if (!animate) {
        this.track.style.transition = 'none';
      }

      if (this.config.effect === 'fade') {
        this.applyFadeEffect(index);
      } else {
        this.track.style.transform = `translateX(${offset}px)`;
      }

      if (!animate) {
        // Forzar reflow
        this.track.offsetHeight;
        this.track.style.transition = `transform ${this.config.speed}ms ease-in-out`;
      }

      // Actualizar estado
      this.updateControls();
      this.updatePagination();

      // Animation flag
      this.isAnimating = true;
      setTimeout(() => {
        this.isAnimating = false;
      }, this.config.speed);

      // Callback
      if (this.config.onSlideChange) {
        this.config.onSlideChange(this.currentIndex, this);
      }
    }

    applyFadeEffect(index) {
      this.slides.forEach((slide, i) => {
        slide.style.opacity = i === index ? '1' : '0';
        slide.style.transition = `opacity ${this.config.speed}ms`;
      });
    }

    updateControls() {
      if (!this.config.navigation) return;

      const maxIndex = this.slides.length - this.config.slidesPerView;

      if (!this.config.loop) {
        this.prevBtn.disabled = this.currentIndex === 0;
        this.nextBtn.disabled = this.currentIndex >= maxIndex;
      }
    }

    updatePagination() {
      if (!this.config.pagination || !this.dots) return;

      const activeIndex = Math.floor(this.currentIndex / this.config.slidesPerView);

      this.dots.forEach((dot, i) => {
        if (i === activeIndex) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });
    }

    next() {
      this.updateSlide(this.currentIndex + this.config.slidesPerView);
      this.resetAutoplay();
    }

    prev() {
      this.updateSlide(this.currentIndex - this.config.slidesPerView);
      this.resetAutoplay();
    }

    goTo(index) {
      this.updateSlide(index);
      this.resetAutoplay();
    }

    startAutoplay() {
      if (!this.config.autoplay) return;

      this.stopAutoplay();
      this.autoplayTimer = setInterval(() => {
        this.next();
      }, this.config.interval);
    }

    stopAutoplay() {
      if (this.autoplayTimer) {
        clearInterval(this.autoplayTimer);
        this.autoplayTimer = null;
      }
    }

    resetAutoplay() {
      if (this.config.autoplay) {
        this.stopAutoplay();
        this.startAutoplay();
      }
    }

    destroy() {
      this.stopAutoplay();
      // Remover event listeners y elementos creados
      if (this.prevBtn) this.prevBtn.remove();
      if (this.nextBtn) this.nextBtn.remove();
      if (this.pagination) this.pagination.remove();
    }
  }


  // ===========================
  // AUTO-INICIALIZACIÓN
  // ===========================
  
  function init() {
    const carousels = document.querySelectorAll('[data-carousel]');
    
    carousels.forEach(carousel => {
      const options = carousel.getAttribute('data-carousel-options');
      const config = options ? JSON.parse(options) : {};
      
      new Carousel(carousel, config);
    });

    console.log(`✅ LNV Carousel: ${carousels.length} carrusel(es) inicializado(s)`);
  }

  // Auto-inicializar
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }


  // ===========================
  // API PÚBLICA
  // ===========================
  
  return {
    Carousel,
    init
  };
})();

// Exportar globalmente
window.LNVCarousel = LNVCarousel;