/**
 * ====================================
 * LNV FRAMEWORK - FORMS
 * Validación y manejo de formularios
 * ====================================
 */

const LNVForms = (function() {
  'use strict';

  // ===========================
  // MÁSCARAS DE INPUT
  // ===========================
  
  const Masks = {
    /**
     * Máscara para DNI Honduras (0000-0000-00000)
     * @param {HTMLInputElement} input
     */
    dni(input) {
      input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 13) value = value.slice(0, 13);
        
        let formatted = '';
        if (value.length > 0) {
          formatted = value.substring(0, 4);
          if (value.length > 4) {
            formatted += '-' + value.substring(4, 8);
          }
          if (value.length > 8) {
            formatted += '-' + value.substring(8, 13);
          }
        }
        
        e.target.value = formatted;
      });
    },

    /**
     * Máscara para teléfono Honduras (0000-0000)
     * @param {HTMLInputElement} input
     */
    phone(input) {
      input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 8) value = value.slice(0, 8);
        
        let formatted = '';
        if (value.length > 0) {
          formatted = value.substring(0, 4);
          if (value.length > 4) {
            formatted += '-' + value.substring(4, 8);
          }
        }
        
        e.target.value = formatted;
      });
    },

    /**
     * Máscara para moneda (L 0,000.00)
     * @param {HTMLInputElement} input
     */
    currency(input) {
      input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/[^\d.]/g, '');
        
        // Permitir solo un punto decimal
        const parts = value.split('.');
        if (parts.length > 2) {
          value = parts[0] + '.' + parts.slice(1).join('');
        }
        
        // Formatear con comas
        if (value) {
          const [integer, decimal] = value.split('.');
          const formattedInteger = integer.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
          value = decimal !== undefined ? `${formattedInteger}.${decimal}` : formattedInteger;
        }
        
        e.target.value = value ? 'L ' + value : '';
      });
    },

    /**
     * Máscara para fecha (DD/MM/YYYY)
     * @param {HTMLInputElement} input
     */
    date(input) {
      input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 8) value = value.slice(0, 8);
        
        let formatted = '';
        if (value.length > 0) {
          formatted = value.substring(0, 2);
          if (value.length > 2) {
            formatted += '/' + value.substring(2, 4);
          }
          if (value.length > 4) {
            formatted += '/' + value.substring(4, 8);
          }
        }
        
        e.target.value = formatted;
      });
    },

    /**
     * Aplicar máscara automáticamente según atributo data-mask
     */
    init() {
      document.querySelectorAll('[data-mask]').forEach(input => {
        const maskType = input.getAttribute('data-mask');
        if (this[maskType]) {
          this[maskType](input);
        }
      });
    }
  };


  // ===========================
  // REGLAS DE VALIDACIÓN
  // ===========================
  
  const Rules = {
    required(value) {
      if (value === null || value === undefined) return false;
      if (typeof value === 'string') return value.trim().length > 0;
      if (Array.isArray(value)) return value.length > 0;
      return true;
    },

    email(value) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(value);
    },

    minLength(value, length) {
      return value.length >= length;
    },

    maxLength(value, length) {
      return value.length <= length;
    },

    min(value, min) {
      return parseFloat(value) >= min;
    },

    max(value, max) {
      return parseFloat(value) <= max;
    },

    pattern(value, pattern) {
      const regex = new RegExp(pattern);
      return regex.test(value);
    },

    dni(value) {
      const cleaned = value.replace(/\D/g, '');
      return cleaned.length === 13;
    },

    phone(value) {
      const cleaned = value.replace(/\D/g, '');
      return cleaned.length === 8;
    },

    url(value) {
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    },

    numeric(value) {
      return !isNaN(parseFloat(value)) && isFinite(value);
    },

    alpha(value) {
      return /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value);
    },

    alphanumeric(value) {
      return /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$/.test(value);
    },

    match(value, targetValue) {
      return value === targetValue;
    }
  };


  // ===========================
  // MENSAJES DE ERROR
  // ===========================
  
  const Messages = {
    required: 'Este campo es obligatorio',
    email: 'Ingrese un correo electrónico válido',
    minLength: 'Debe tener al menos {length} caracteres',
    maxLength: 'No debe exceder {length} caracteres',
    min: 'El valor mínimo es {min}',
    max: 'El valor máximo es {max}',
    pattern: 'El formato no es válido',
    dni: 'Ingrese un DNI válido (13 dígitos)',
    phone: 'Ingrese un teléfono válido (8 dígitos)',
    url: 'Ingrese una URL válida',
    numeric: 'Solo se permiten números',
    alpha: 'Solo se permiten letras',
    alphanumeric: 'Solo se permiten letras y números',
    match: 'Los campos no coinciden'
  };


  // ===========================
  // VALIDADOR DE FORMULARIOS
  // ===========================
  
  class FormValidator {
    constructor(formId, options = {}) {
      this.form = document.getElementById(formId);
      if (!this.form) {
        console.error(`Formulario con ID "${formId}" no encontrado`);
        return;
      }

      this.options = {
        validateOnInput: true,
        validateOnBlur: true,
        scrollToError: true,
        customMessages: {},
        onSubmit: null,
        onError: null,
        ...options
      };

      this.errors = {};
      this.fields = {};
      
      this.init();
    }

    init() {
      // Prevenir submit por defecto
      this.form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleSubmit();
      });

      // Recolectar campos con validación
      this.form.querySelectorAll('[data-validate]').forEach(field => {
        this.registerField(field);
      });

      // Agregar listeners
      if (this.options.validateOnInput) {
        this.addInputListeners();
      }

      if (this.options.validateOnBlur) {
        this.addBlurListeners();
      }
    }

    registerField(field) {
      const name = field.name || field.id;
      if (!name) return;

      const rules = field.getAttribute('data-validate').split('|');
      const customMessage = field.getAttribute('data-message');

      this.fields[name] = {
        element: field,
        rules: this.parseRules(rules),
        customMessage: customMessage
      };
    }

    parseRules(rules) {
      const parsed = [];
      
      rules.forEach(rule => {
        const [name, ...params] = rule.split(':');
        parsed.push({
          name: name.trim(),
          params: params.length > 0 ? params[0].split(',') : []
        });
      });

      return parsed;
    }

    validateField(fieldName) {
      const field = this.fields[fieldName];
      if (!field) return true;

      const value = field.element.value;
      const errors = [];

      field.rules.forEach(rule => {
        const validator = Rules[rule.name];
        if (!validator) {
          console.warn(`Regla de validación "${rule.name}" no existe`);
          return;
        }

        let isValid;
        if (rule.params.length > 0) {
          // Reglas con parámetros
          if (rule.name === 'match') {
            const targetField = this.form.querySelector(`[name="${rule.params[0]}"]`);
            isValid = validator(value, targetField ? targetField.value : '');
          } else {
            isValid = validator(value, ...rule.params);
          }
        } else {
          isValid = validator(value);
        }

        if (!isValid) {
          let message = field.customMessage || Messages[rule.name] || 'Campo inválido';
          
          // Reemplazar placeholders en el mensaje
          rule.params.forEach((param, index) => {
            message = message.replace(`{${rule.name === 'minLength' || rule.name === 'maxLength' ? 'length' : rule.name}}`, param);
          });

          errors.push(message);
        }
      });

      if (errors.length > 0) {
        this.errors[fieldName] = errors[0]; // Mostrar solo el primer error
        this.showError(field.element, errors[0]);
        return false;
      } else {
        delete this.errors[fieldName];
        this.clearError(field.element);
        return true;
      }
    }

    validateAll() {
      let isValid = true;
      Object.keys(this.fields).forEach(fieldName => {
        if (!this.validateField(fieldName)) {
          isValid = false;
        }
      });
      return isValid;
    }

    showError(element, message) {
      // Agregar clase de error al input
      element.classList.add('is-invalid');
      element.classList.remove('is-valid');

      // Buscar o crear elemento de mensaje
      let errorElement = element.parentElement.querySelector('.lnv-form-error');
      
      if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'lnv-form-error';
        element.parentElement.appendChild(errorElement);
      }

      errorElement.textContent = message;
      errorElement.style.display = 'block';
    }

    clearError(element) {
      element.classList.remove('is-invalid');
      element.classList.add('is-valid');

      const errorElement = element.parentElement.querySelector('.lnv-form-error');
      if (errorElement) {
        errorElement.style.display = 'none';
      }
    }

    clearAllErrors() {
      Object.keys(this.fields).forEach(fieldName => {
        const field = this.fields[fieldName];
        this.clearError(field.element);
      });
      this.errors = {};
    }

    addInputListeners() {
      Object.keys(this.fields).forEach(fieldName => {
        const field = this.fields[fieldName];
        field.element.addEventListener('input', () => {
          if (this.errors[fieldName]) {
            this.validateField(fieldName);
          }
        });
      });
    }

    addBlurListeners() {
      Object.keys(this.fields).forEach(fieldName => {
        const field = this.fields[fieldName];
        field.element.addEventListener('blur', () => {
          this.validateField(fieldName);
        });
      });
    }

    handleSubmit() {
      this.clearAllErrors();

      if (this.validateAll()) {
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData);

        if (this.options.onSubmit) {
          this.options.onSubmit(data, this.form);
        } else {
          console.log('Formulario válido:', data);
        }
      } else {
        // Scroll al primer error
        if (this.options.scrollToError) {
          const firstErrorField = Object.keys(this.errors)[0];
          if (firstErrorField) {
            const element = this.fields[firstErrorField].element;
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            element.focus();
          }
        }

        if (this.options.onError) {
          this.options.onError(this.errors);
        }
      }
    }

    getValues() {
      const formData = new FormData(this.form);
      return Object.fromEntries(formData);
    }

    reset() {
      this.form.reset();
      this.clearAllErrors();
    }

    setValues(data) {
      Object.keys(data).forEach(key => {
        const field = this.form.querySelector(`[name="${key}"]`);
        if (field) {
          field.value = data[key];
        }
      });
    }
  }


  // ===========================
  // VALIDACIÓN EN TIEMPO REAL
  // ===========================
  
  /**
   * Agregar validación en tiempo real a un campo individual
   * @param {String} fieldId - ID del campo
   * @param {Array} rules - Array de reglas ['required', 'email', etc]
   * @param {Object} options - Opciones adicionales
   */
  function validateField(fieldId, rules, options = {}) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    const config = {
      message: '',
      onValid: null,
      onInvalid: null,
      ...options
    };

    const parsedRules = rules.map(rule => {
      if (typeof rule === 'string') {
        const [name, ...params] = rule.split(':');
        return { name, params: params.length > 0 ? params[0].split(',') : [] };
      }
      return rule;
    });

    const validate = () => {
      const value = field.value;
      let isValid = true;
      let errorMessage = '';

      for (const rule of parsedRules) {
        const validator = Rules[rule.name];
        if (!validator) continue;

        const valid = rule.params.length > 0 
          ? validator(value, ...rule.params)
          : validator(value);

        if (!valid) {
          isValid = false;
          errorMessage = config.message || Messages[rule.name] || 'Campo inválido';
          break;
        }
      }

      if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (config.onValid) config.onValid(field);
      } else {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        // Mostrar mensaje de error
        let errorEl = field.parentElement.querySelector('.lnv-form-error');
        if (!errorEl) {
          errorEl = document.createElement('div');
          errorEl.className = 'lnv-form-error';
          field.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = errorMessage;
        errorEl.style.display = 'block';

        if (config.onInvalid) config.onInvalid(field, errorMessage);
      }

      return isValid;
    };

    field.addEventListener('blur', validate);
    field.addEventListener('input', () => {
      if (field.classList.contains('is-invalid')) {
        validate();
      }
    });
  }


  // ===========================
  // COMPARAR CONTRASEÑAS
  // ===========================
  
  /**
   * Validar que dos campos de contraseña coincidan
   * @param {String} passwordId - ID del campo de contraseña
   * @param {String} confirmId - ID del campo de confirmación
   */
  function matchPasswords(passwordId, confirmId) {
    const password = document.getElementById(passwordId);
    const confirm = document.getElementById(confirmId);

    if (!password || !confirm) return;

    const validate = () => {
      if (confirm.value === '') return;

      if (password.value === confirm.value) {
        confirm.classList.remove('is-invalid');
        confirm.classList.add('is-valid');
        
        const errorEl = confirm.parentElement.querySelector('.lnv-form-error');
        if (errorEl) errorEl.style.display = 'none';
      } else {
        confirm.classList.add('is-invalid');
        confirm.classList.remove('is-valid');
        
        let errorEl = confirm.parentElement.querySelector('.lnv-form-error');
        if (!errorEl) {
          errorEl = document.createElement('div');
          errorEl.className = 'lnv-form-error';
          confirm.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = 'Las contraseñas no coinciden';
        errorEl.style.display = 'block';
      }
    };

    password.addEventListener('input', validate);
    confirm.addEventListener('input', validate);
  }


  // ===========================
  // MOSTRAR/OCULTAR CONTRASEÑA
  // ===========================
  
  /**
   * Toggle para mostrar/ocultar contraseña
   * @param {String} inputId - ID del input de contraseña
   * @param {String} toggleId - ID del botón toggle
   */
  function togglePassword(inputId, toggleId) {
    const input = document.getElementById(inputId);
    const toggle = document.getElementById(toggleId);

    if (!input || !toggle) return;

    toggle.addEventListener('click', () => {
      const type = input.type === 'password' ? 'text' : 'password';
      input.type = type;
      
      // Cambiar icono si existe
      const icon = toggle.querySelector('i, .lnv-icon');
      if (icon) {
        icon.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
      }
    });
  }


  // ===========================
  // CONTADOR DE CARACTERES
  // ===========================
  
  /**
   * Agregar contador de caracteres a un campo
   * @param {String} fieldId - ID del campo
   * @param {Number} maxLength - Longitud máxima
   */
  function characterCounter(fieldId, maxLength) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Crear elemento contador
    const counter = document.createElement('div');
    counter.className = 'lnv-form-help';
    counter.style.textAlign = 'right';
    counter.style.fontSize = '0.875rem';
    counter.style.marginTop = '0.25rem';
    
    field.parentElement.appendChild(counter);

    const updateCounter = () => {
      const length = field.value.length;
      counter.textContent = `${length} / ${maxLength}`;
      
      if (length > maxLength) {
        counter.style.color = 'var(--lnv-danger)';
      } else if (length > maxLength * 0.9) {
        counter.style.color = 'var(--lnv-warning)';
      } else {
        counter.style.color = 'var(--lnv-gray)';
      }
    };

    field.addEventListener('input', updateCounter);
    updateCounter();
  }


  // ===========================
  // VALIDADOR DE FUERZA DE CONTRASEÑA
  // ===========================
  
  /**
   * Validar fuerza de contraseña
   * @param {String} passwordId - ID del campo de contraseña
   * @param {Object} options - Opciones de validación
   */
  function passwordStrength(passwordId, options = {}) {
    const field = document.getElementById(passwordId);
    if (!field) return;

    const config = {
      showIndicator: true,
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecial: true,
      ...options
    };

    // Crear indicador visual
    let indicator;
    if (config.showIndicator) {
      indicator = document.createElement('div');
      indicator.className = 'lnv-password-strength';
      indicator.innerHTML = `
        <div class="lnv-password-strength-bar">
          <div class="lnv-password-strength-fill"></div>
        </div>
        <div class="lnv-password-strength-text"></div>
      `;
      field.parentElement.appendChild(indicator);

      // Estilos inline para el indicador
      const style = document.createElement('style');
      style.textContent = `
        .lnv-password-strength { margin-top: 0.5rem; }
        .lnv-password-strength-bar {
          height: 4px;
          background-color: var(--lnv-gray-light);
          border-radius: 2px;
          overflow: hidden;
        }
        .lnv-password-strength-fill {
          height: 100%;
          transition: width 0.3s, background-color 0.3s;
          width: 0;
        }
        .lnv-password-strength-text {
          font-size: 0.75rem;
          margin-top: 0.25rem;
        }
      `;
      document.head.appendChild(style);
    }

    const checkStrength = () => {
      const value = field.value;
      let strength = 0;
      const checks = [];

      // Longitud
      if (value.length >= config.minLength) {
        strength += 20;
        checks.push('Longitud suficiente');
      }

      // Mayúsculas
      if (config.requireUppercase && /[A-Z]/.test(value)) {
        strength += 20;
        checks.push('Mayúsculas');
      }

      // Minúsculas
      if (config.requireLowercase && /[a-z]/.test(value)) {
        strength += 20;
        checks.push('Minúsculas');
      }

      // Números
      if (config.requireNumbers && /\d/.test(value)) {
        strength += 20;
        checks.push('Números');
      }

      // Caracteres especiales
      if (config.requireSpecial && /[!@#$%^&*(),.?":{}|<>]/.test(value)) {
        strength += 20;
        checks.push('Caracteres especiales');
      }

      // Actualizar indicador visual
      if (indicator) {
        const fill = indicator.querySelector('.lnv-password-strength-fill');
        const text = indicator.querySelector('.lnv-password-strength-text');

        fill.style.width = `${strength}%`;

        if (strength === 0) {
          fill.style.backgroundColor = 'transparent';
          text.textContent = '';
        } else if (strength < 40) {
          fill.style.backgroundColor = 'var(--lnv-danger)';
          text.textContent = 'Débil';
          text.style.color = 'var(--lnv-danger)';
        } else if (strength < 60) {
          fill.style.backgroundColor = 'var(--lnv-warning)';
          text.textContent = 'Media';
          text.style.color = 'var(--lnv-warning)';
        } else if (strength < 80) {
          fill.style.backgroundColor = 'var(--lnv-info)';
          text.textContent = 'Buena';
          text.style.color = 'var(--lnv-info)';
        } else {
          fill.style.backgroundColor = 'var(--lnv-success)';
          text.textContent = 'Fuerte';
          text.style.color = 'var(--lnv-success)';
        }
      }

      return { strength, checks };
    };

    field.addEventListener('input', checkStrength);
  }


  // ===========================
  // AUTO-INICIALIZACIÓN
  // ===========================
  
  function init() {
    // Inicializar máscaras
    Masks.init();

    // Auto-inicializar validadores con atributo data-validator
    document.querySelectorAll('[data-validator]').forEach(form => {
      const formId = form.id;
      if (formId) {
        new FormValidator(formId);
      }
    });

    // Auto-inicializar comparación de contraseñas
    document.querySelectorAll('[data-match]').forEach(field => {
      const targetId = field.getAttribute('data-match');
      matchPasswords(targetId, field.id);
    });

    // Auto-inicializar toggle de contraseñas
    document.querySelectorAll('[data-toggle-password]').forEach(toggle => {
      const targetId = toggle.getAttribute('data-toggle-password');
      togglePassword(targetId, toggle.id);
    });

    // Auto-inicializar contadores de caracteres
    document.querySelectorAll('[data-maxlength]').forEach(field => {
      const maxLength = parseInt(field.getAttribute('data-maxlength'));
      if (maxLength) {
        characterCounter(field.id, maxLength);
      }
    });

    // Auto-inicializar indicadores de fuerza de contraseña
    document.querySelectorAll('[data-password-strength]').forEach(field => {
      passwordStrength(field.id);
    });

    console.log('✅ LNV Forms inicializado correctamente');
  }

  // Auto-inicializar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }


  // ===========================
  // API PÚBLICA
  // ===========================
  
  return {
    Masks,
    Rules,
    Messages,
    FormValidator,
    validateField,
    matchPasswords,
    togglePassword,
    characterCounter,
    passwordStrength,
    init
  };
})();

// Exportar globalmente
window.LNVForms = LNVForms;