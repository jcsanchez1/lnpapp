/**
 * ====================================
 * LNV FRAMEWORK - ADVANCED COMPONENTS
 * Stepper, Rating, Chips/Tags
 * ====================================
 */

const LNVComponents = (function() {
  'use strict';

  // ===========================
  // STEPPER / WIZARD
  // ===========================
  
  class Stepper {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('Stepper: Elemento no encontrado');
        return;
      }

      this.config = {
        currentStep: 0,
        linear: true, // Requiere completar pasos anteriores
        onStepChange: null,
        onComplete: null,
        ...options
      };

      this.steps = Array.from(this.container.querySelectorAll('.lnv-stepper-item'));
      this.contents = Array.from(document.querySelectorAll('.lnv-stepper-content'));
      this.currentStep = this.config.currentStep;

      this.init();
    }

    init() {
      // Marcar pasos completados
      this.updateSteps();

      // Agregar click listeners a los círculos
      this.steps.forEach((step, index) => {
        const circle = step.querySelector('.lnv-stepper-circle');
        if (circle) {
          circle.addEventListener('click', () => {
            if (!this.config.linear || index <= this.currentStep + 1) {
              this.goTo(index);
            }
          });
        }
      });

      console.log('✅ Stepper inicializado');
    }

    updateSteps() {
      this.steps.forEach((step, index) => {
        step.classList.remove('active', 'completed');

        if (index < this.currentStep) {
          step.classList.add('completed');
        } else if (index === this.currentStep) {
          step.classList.add('active');
        }
      });

      // Actualizar contenido
      this.contents.forEach((content, index) => {
        content.classList.remove('active');
        if (index === this.currentStep) {
          content.classList.add('active');
        }
      });

      // Callback
      if (this.config.onStepChange) {
        this.config.onStepChange(this.currentStep, this);
      }
    }

    next() {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++;
        this.updateSteps();
      } else if (this.currentStep === this.steps.length - 1) {
        // Último paso completado
        if (this.config.onComplete) {
          this.config.onComplete(this);
        }
      }
    }

    prev() {
      if (this.currentStep > 0) {
        this.currentStep--;
        this.updateSteps();
      }
    }

    goTo(index) {
      if (index >= 0 && index < this.steps.length) {
        if (!this.config.linear || index <= this.currentStep + 1) {
          this.currentStep = index;
          this.updateSteps();
        }
      }
    }

    reset() {
      this.currentStep = 0;
      this.updateSteps();
    }

    complete() {
      this.steps.forEach(step => step.classList.add('completed'));
      if (this.config.onComplete) {
        this.config.onComplete(this);
      }
    }
  }


  // ===========================
  // RATING (ESTRELLAS)
  // ===========================
  
  class Rating {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('Rating: Elemento no encontrado');
        return;
      }

      this.config = {
        max: 5,
        value: 0,
        readonly: false,
        size: 'base', // 'sm', 'base', 'lg', 'xl'
        icon: '★',
        emptyIcon: '☆',
        onChange: null,
        ...options
      };

      this.value = this.config.value;
      this.hoveredValue = 0;

      this.init();
    }

    init() {
      this.container.classList.add('lnv-rating');
      
      if (this.config.size !== 'base') {
        this.container.classList.add(`lnv-rating-${this.config.size}`);
      }

      if (this.config.readonly) {
        this.container.classList.add('readonly');
      }

      // Crear estrellas
      this.createStars();

      // Update inicial
      this.updateStars();

      console.log('✅ Rating inicializado');
    }

    createStars() {
      this.container.innerHTML = '';
      this.stars = [];

      for (let i = 1; i <= this.config.max; i++) {
        const star = document.createElement('span');
        star.className = 'lnv-rating-star';
        star.textContent = this.config.emptyIcon;
        star.dataset.value = i;

        if (!this.config.readonly) {
          star.addEventListener('click', () => this.setValue(i));
          star.addEventListener('mouseenter', () => this.hover(i));
          star.addEventListener('mouseleave', () => this.hover(0));
        }

        this.container.appendChild(star);
        this.stars.push(star);
      }
    }

    updateStars() {
      const displayValue = this.hoveredValue || this.value;

      this.stars.forEach((star, index) => {
        const starValue = index + 1;
        
        if (starValue <= displayValue) {
          star.classList.add('filled');
          star.textContent = this.config.icon;
        } else {
          star.classList.remove('filled');
          star.textContent = this.config.emptyIcon;
        }

        if (this.hoveredValue && starValue <= this.hoveredValue) {
          star.classList.add('hover');
        } else {
          star.classList.remove('hover');
        }
      });
    }

    setValue(value) {
      if (this.config.readonly) return;

      this.value = value;
      this.updateStars();

      if (this.config.onChange) {
        this.config.onChange(this.value, this);
      }
    }

    hover(value) {
      if (this.config.readonly) return;

      this.hoveredValue = value;
      this.updateStars();
    }

    getValue() {
      return this.value;
    }

    reset() {
      this.value = 0;
      this.updateStars();
    }

    setReadonly(readonly) {
      this.config.readonly = readonly;
      
      if (readonly) {
        this.container.classList.add('readonly');
      } else {
        this.container.classList.remove('readonly');
      }
    }
  }


  // ===========================
  // CHIPS / TAGS
  // ===========================
  
  class ChipInput {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('ChipInput: Elemento no encontrado');
        return;
      }

      this.config = {
        placeholder: 'Agregar...',
        max: null,
        allowDuplicates: false,
        variant: 'default', // 'default', 'primary', 'success', etc.
        removable: true,
        onAdd: null,
        onRemove: null,
        onChange: null,
        ...options
      };

      this.chips = [];
      this.init();
    }

    init() {
      // Crear wrapper
      this.wrapper = document.createElement('div');
      this.wrapper.className = 'lnv-chip-input-wrapper';
      this.wrapper.style.cssText = `
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 0.75rem;
        border: 1px solid var(--lnv-gray-light);
        border-radius: var(--lnv-radius-md);
        min-height: 44px;
        cursor: text;
      `;

      // Crear input
      this.input = document.createElement('input');
      this.input.type = 'text';
      this.input.placeholder = this.config.placeholder;
      this.input.style.cssText = `
        border: none;
        outline: none;
        flex: 1;
        min-width: 120px;
        font-size: 0.875rem;
        background: transparent;
      `;

      this.wrapper.appendChild(this.input);
      this.container.appendChild(this.wrapper);

      // Eventos
      this.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && this.input.value.trim()) {
          e.preventDefault();
          this.add(this.input.value.trim());
          this.input.value = '';
        } else if (e.key === 'Backspace' && !this.input.value && this.chips.length > 0) {
          this.remove(this.chips.length - 1);
        }
      });

      this.wrapper.addEventListener('click', () => {
        this.input.focus();
      });

      console.log('✅ ChipInput inicializado');
    }

    add(value) {
      // Validaciones
      if (!value) return;

      if (this.config.max && this.chips.length >= this.config.max) {
        console.warn('ChipInput: Máximo de chips alcanzado');
        return;
      }

      if (!this.config.allowDuplicates && this.chips.includes(value)) {
        console.warn('ChipInput: Chip duplicado');
        return;
      }

      // Agregar chip
      this.chips.push(value);
      this.renderChip(value, this.chips.length - 1);

      // Callbacks
      if (this.config.onAdd) {
        this.config.onAdd(value, this);
      }

      if (this.config.onChange) {
        this.config.onChange(this.chips, this);
      }
    }

    renderChip(value, index) {
      const chip = document.createElement('div');
      chip.className = 'lnv-chip';
      
      if (this.config.variant !== 'default') {
        chip.classList.add(`lnv-chip-${this.config.variant}`);
      }

      chip.innerHTML = `
        <span>${value}</span>
        ${this.config.removable ? '<button class="lnv-chip-close">×</button>' : ''}
      `;

      if (this.config.removable) {
        const closeBtn = chip.querySelector('.lnv-chip-close');
        closeBtn.addEventListener('click', () => this.remove(index));
      }

      this.wrapper.insertBefore(chip, this.input);
    }

    remove(index) {
      if (index < 0 || index >= this.chips.length) return;

      const value = this.chips[index];
      this.chips.splice(index, 1);

      // Volver a renderizar todos los chips
      this.wrapper.querySelectorAll('.lnv-chip').forEach(chip => chip.remove());
      this.chips.forEach((chip, i) => this.renderChip(chip, i));

      // Callbacks
      if (this.config.onRemove) {
        this.config.onRemove(value, this);
      }

      if (this.config.onChange) {
        this.config.onChange(this.chips, this);
      }
    }

    getValues() {
      return [...this.chips];
    }

    setValues(values) {
      this.clear();
      values.forEach(value => this.add(value));
    }

    clear() {
      this.chips = [];
      this.wrapper.querySelectorAll('.lnv-chip').forEach(chip => chip.remove());

      if (this.config.onChange) {
        this.config.onChange(this.chips, this);
      }
    }
  }


  // ===========================
  // POPOVER
  // ===========================
  
  class Popover {
    constructor(trigger, options = {}) {
      this.trigger = typeof trigger === 'string' 
        ? document.querySelector(trigger)
        : trigger;

      if (!this.trigger) {
        console.error('Popover: Trigger no encontrado');
        return;
      }

      this.config = {
        title: '',
        content: '',
        placement: 'top', // 'top', 'bottom', 'left', 'right'
        trigger: 'click', // 'click', 'hover'
        html: false,
        offset: 10,
        ...options
      };

      this.popover = null;
      this.isOpen = false;

      this.init();
    }

    init() {
      // Crear popover
      this.createPopover();

      // Eventos
      if (this.config.trigger === 'click') {
        this.trigger.addEventListener('click', (e) => {
          e.stopPropagation();
          this.toggle();
        });

        document.addEventListener('click', (e) => {
          if (this.isOpen && !this.popover.contains(e.target)) {
            this.hide();
          }
        });
      } else if (this.config.trigger === 'hover') {
        this.trigger.addEventListener('mouseenter', () => this.show());
        this.trigger.addEventListener('mouseleave', () => this.hide());
      }

      console.log('✅ Popover inicializado');
    }

    createPopover() {
      this.popover = document.createElement('div');
      this.popover.className = `lnv-popover lnv-popover-${this.config.placement}`;

      let html = '';

      if (this.config.title) {
        html += `<div class="lnv-popover-header">${this.config.title}</div>`;
      }

      html += `<div class="lnv-popover-body">${this.config.content}</div>`;
      html += `<div class="lnv-popover-arrow"></div>`;

      this.popover.innerHTML = html;
      document.body.appendChild(this.popover);
    }

    position() {
      const triggerRect = this.trigger.getBoundingClientRect();
      const popoverRect = this.popover.getBoundingClientRect();

      let top, left;

      switch (this.config.placement) {
        case 'top':
          top = triggerRect.top - popoverRect.height - this.config.offset;
          left = triggerRect.left + (triggerRect.width / 2) - (popoverRect.width / 2);
          break;
        case 'bottom':
          top = triggerRect.bottom + this.config.offset;
          left = triggerRect.left + (triggerRect.width / 2) - (popoverRect.width / 2);
          break;
        case 'left':
          top = triggerRect.top + (triggerRect.height / 2) - (popoverRect.height / 2);
          left = triggerRect.left - popoverRect.width - this.config.offset;
          break;
        case 'right':
          top = triggerRect.top + (triggerRect.height / 2) - (popoverRect.height / 2);
          left = triggerRect.right + this.config.offset;
          break;
      }

      this.popover.style.top = `${top + window.scrollY}px`;
      this.popover.style.left = `${left + window.scrollX}px`;
    }

    show() {
      this.position();
      this.popover.classList.add('active');
      this.isOpen = true;
    }

    hide() {
      this.popover.classList.remove('active');
      this.isOpen = false;
    }

    toggle() {
      if (this.isOpen) {
        this.hide();
      } else {
        this.show();
      }
    }

    destroy() {
      if (this.popover && this.popover.parentNode) {
        this.popover.parentNode.removeChild(this.popover);
      }
    }
  }


  // ===========================
  // AUTO-INICIALIZACIÓN
  // ===========================
  
  function init() {
    // Inicializar steppers
    document.querySelectorAll('[data-stepper]').forEach(element => {
      new Stepper(element);
    });

    // Inicializar ratings
    document.querySelectorAll('[data-rating]').forEach(element => {
      const options = element.getAttribute('data-rating-options');
      const config = options ? JSON.parse(options) : {};
      new Rating(element, config);
    });

    // Inicializar chip inputs
    document.querySelectorAll('[data-chip-input]').forEach(element => {
      const options = element.getAttribute('data-chip-options');
      const config = options ? JSON.parse(options) : {};
      new ChipInput(element, config);
    });

    console.log('✅ LNV Advanced Components inicializados');
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
    Stepper,
    Rating,
    ChipInput,
    Popover,
    init
  };
})();

// Exportar globalmente
window.LNVComponents = LNVComponents;