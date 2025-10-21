/**
 * ====================================
 * LNV FRAMEWORK - CORE JAVASCRIPT
 * Laboratorio Nacional de Vigilancia
 * Funciones principales del framework
 * ====================================
 */

const LNV = (function() {
  'use strict';

  // ===========================
  // UTILIDADES GENERALES
  // ===========================
  
  const Utils = {
    // Selector de elementos
    $(selector) {
      return document.querySelector(selector);
    },
    
    $$(selector) {
      return document.querySelectorAll(selector);
    },
    
    // Agregar clase
    addClass(el, className) {
      if (el) el.classList.add(className);
    },
    
    // Remover clase
    removeClass(el, className) {
      if (el) el.classList.remove(className);
    },
    
    // Toggle clase
    toggleClass(el, className) {
      if (el) el.classList.toggle(className);
    },
    
    // Verificar si tiene clase
    hasClass(el, className) {
      return el ? el.classList.contains(className) : false;
    },
    
    // Agregar evento
    on(el, event, handler) {
      if (el) el.addEventListener(event, handler);
    },
    
    // Crear elemento
    create(tag, attrs = {}) {
      const el = document.createElement(tag);
      Object.keys(attrs).forEach(key => {
        if (key === 'class') {
          el.className = attrs[key];
        } else if (key === 'html') {
          el.innerHTML = attrs[key];
        } else {
          el.setAttribute(key, attrs[key]);
        }
      });
      return el;
    },
    
    // Generar ID único
    generateId() {
      return 'lnv-' + Math.random().toString(36).substr(2, 9);
    }
  };

  
  // ===========================
  // MODALES
  // ===========================
  
  const Modal = {
    // Abrir modal
    open(modalId) {
      const modal = Utils.$(`#${modalId}`);
      if (modal) {
        Utils.addClass(modal, 'active');
        document.body.style.overflow = 'hidden';
        
        // Cerrar con ESC
        const handleEsc = (e) => {
          if (e.key === 'Escape') {
            this.close(modalId);
            document.removeEventListener('keydown', handleEsc);
          }
        };
        document.addEventListener('keydown', handleEsc);
      }
    },
    
    // Cerrar modal
    close(modalId) {
      const modal = Utils.$(`#${modalId}`);
      if (modal) {
        Utils.removeClass(modal, 'active');
        document.body.style.overflow = '';
      }
    },
    
    // Inicializar todos los modales
    init() {
      // Cerrar al hacer click en backdrop
      Utils.$$('.lnv-modal-backdrop').forEach(backdrop => {
        Utils.on(backdrop, 'click', function() {
          const modal = this.closest('.lnv-modal');
          if (modal) Modal.close(modal.id);
        });
      });
      
      // Cerrar con botón X
      Utils.$$('.lnv-modal-close').forEach(btn => {
        Utils.on(btn, 'click', function() {
          const modal = this.closest('.lnv-modal');
          if (modal) Modal.close(modal.id);
        });
      });
    }
  };

  
  // ===========================
  // DROPDOWNS
  // ===========================
  
  const Dropdown = {
    openDropdown: null,
    
    // Toggle dropdown
    toggle(dropdownEl) {
      // Cerrar otros dropdowns
      if (this.openDropdown && this.openDropdown !== dropdownEl) {
        Utils.removeClass(this.openDropdown, 'active');
      }
      
      Utils.toggleClass(dropdownEl, 'active');
      this.openDropdown = Utils.hasClass(dropdownEl, 'active') ? dropdownEl : null;
    },
    
    // Cerrar dropdown
    close(dropdownEl) {
      Utils.removeClass(dropdownEl, 'active');
      if (this.openDropdown === dropdownEl) {
        this.openDropdown = null;
      }
    },
    
    // Inicializar dropdowns
    init() {
      // Toggle con el botón
      Utils.$$('.lnv-dropdown-toggle').forEach(toggle => {
        Utils.on(toggle, 'click', (e) => {
          e.stopPropagation();
          const dropdown = toggle.closest('.lnv-dropdown');
          if (dropdown) this.toggle(dropdown);
        });
      });
      
      // Cerrar al hacer click fuera
      Utils.on(document, 'click', () => {
        if (this.openDropdown) {
          this.close(this.openDropdown);
        }
      });
      
      // Evitar cerrar al hacer click dentro del menu
      Utils.$$('.lnv-dropdown-menu').forEach(menu => {
        Utils.on(menu, 'click', (e) => {
          e.stopPropagation();
        });
      });
    }
  };

  
  // ===========================
  // TABS
  // ===========================
  
  const Tabs = {
    // Cambiar de tab
    switchTab(tabElement) {
      const tabsContainer = tabElement.closest('.lnv-tabs');
      if (!tabsContainer) return;
      
      const targetId = tabElement.getAttribute('data-tab');
      if (!targetId) return;
      
      // Remover active de todos los tabs
      Utils.$$('.lnv-tab', tabsContainer).forEach(tab => {
        Utils.removeClass(tab, 'active');
      });
      
      // Agregar active al tab clickeado
      Utils.addClass(tabElement, 'active');
      
      // Ocultar todos los contenidos
      Utils.$$('.lnv-tab-content').forEach(content => {
        Utils.removeClass(content, 'active');
      });
      
      // Mostrar el contenido correspondiente
      const targetContent = Utils.$(`#${targetId}`);
      if (targetContent) {
        Utils.addClass(targetContent, 'active');
      }
    },
    
    // Inicializar tabs
    init() {
      Utils.$$('.lnv-tab').forEach(tab => {
        Utils.on(tab, 'click', () => {
          this.switchTab(tab);
        });
      });
    }
  };

  
  // ===========================
  // ACCORDION
  // ===========================
  
  const Accordion = {
    // Toggle item
    toggle(item) {
      const isActive = Utils.hasClass(item, 'active');
      
      // Cerrar otros items del mismo accordion (opcional)
      const accordion = item.closest('.lnv-accordion');
      if (accordion) {
        Utils.$$('.lnv-accordion-item', accordion).forEach(otherItem => {
          if (otherItem !== item) {
            Utils.removeClass(otherItem, 'active');
          }
        });
      }
      
      // Toggle el item actual
      Utils.toggleClass(item, 'active');
    },
    
    // Inicializar accordion
    init() {
      Utils.$$('.lnv-accordion-header').forEach(header => {
        Utils.on(header, 'click', function() {
          const item = this.closest('.lnv-accordion-item');
          if (item) Accordion.toggle(item);
        });
      });
    }
  };

  
  // ===========================
  // SIDEBAR
  // ===========================
  
  const Sidebar = {
    // Toggle sidebar (para móvil)
    toggle() {
      const sidebar = Utils.$('.lnv-sidebar');
      const overlay = Utils.$('.lnv-sidebar-overlay');
      
      if (sidebar) {
        Utils.toggleClass(sidebar, 'active');
      }
      
      if (overlay) {
        Utils.toggleClass(overlay, 'active');
      }
    },
    
    // Colapsar sidebar (para desktop)
    collapse() {
      const sidebar = Utils.$('.lnv-sidebar');
      if (sidebar) {
        Utils.toggleClass(sidebar, 'collapsed');
      }
    },
    
    // Inicializar sidebar
    init() {
      // Toggle para móvil
      Utils.$$('[data-toggle="sidebar"]').forEach(btn => {
        Utils.on(btn, 'click', () => {
          this.toggle();
        });
      });
      
      // Cerrar con overlay
      const overlay = Utils.$('.lnv-sidebar-overlay');
      if (overlay) {
        Utils.on(overlay, 'click', () => {
          this.toggle();
        });
      }
      
      // Toggle collapse para desktop
      Utils.$$('[data-toggle="sidebar-collapse"]').forEach(btn => {
        Utils.on(btn, 'click', () => {
          this.collapse();
        });
      });
    }
  };

  
  // ===========================
  // ALERTS (Dismissible)
  // ===========================
  
  const Alert = {
    // Cerrar alert
    close(alertEl) {
      Utils.addClass(alertEl, 'lnv-fade-out');
      setTimeout(() => {
        if (alertEl.parentNode) {
          alertEl.parentNode.removeChild(alertEl);
        }
      }, 250);
    },
    
    // Inicializar alerts
    init() {
      Utils.$$('.lnv-alert-close').forEach(closeBtn => {
        Utils.on(closeBtn, 'click', function() {
          const alert = this.closest('.lnv-alert');
          if (alert) Alert.close(alert);
        });
      });
    }
  };

  
  // ===========================
  // TOAST NOTIFICATIONS
  // ===========================
  
  const Toast = {
    container: null,
    
    // Crear contenedor si no existe
    ensureContainer(position = 'top-right') {
      if (!this.container) {
        this.container = Utils.create('div', {
          class: `lnv-toast-container ${position}`
        });
        document.body.appendChild(this.container);
      }
      return this.container;
    },
    
    // Mostrar toast
    show(options = {}) {
      const defaults = {
        title: '',
        message: '',
        type: 'info', // info, success, danger, warning
        duration: 3000,
        position: 'top-right'
      };
      
      const config = { ...defaults, ...options };
      const container = this.ensureContainer(config.position);
      
      // Crear toast
      const toast = Utils.create('div', {
        class: `lnv-toast lnv-toast-${config.type}`
      });
      
      let html = '';
      if (config.title) {
        html += `
          <div class="lnv-toast-header">
            <strong class="lnv-toast-title">${config.title}</strong>
            <span class="lnv-toast-close">×</span>
          </div>
        `;
      }
      
      html += `
        <div class="lnv-toast-body">
          ${config.message}
        </div>
      `;
      
      toast.innerHTML = html;
      container.appendChild(toast);
      
      // Cerrar con botón X
      const closeBtn = toast.querySelector('.lnv-toast-close');
      if (closeBtn) {
        Utils.on(closeBtn, 'click', () => {
          this.close(toast);
        });
      }
      
      // Auto cerrar
      if (config.duration > 0) {
        setTimeout(() => {
          this.close(toast);
        }, config.duration);
      }
      
      return toast;
    },
    
    // Cerrar toast
    close(toastEl) {
      Utils.addClass(toastEl, 'lnv-fade-out');
      setTimeout(() => {
        if (toastEl.parentNode) {
          toastEl.parentNode.removeChild(toastEl);
        }
      }, 250);
    },
    
    // Shortcuts
    success(message, title = 'Éxito') {
      return this.show({ type: 'success', title, message });
    },
    
    error(message, title = 'Error') {
      return this.show({ type: 'danger', title, message });
    },
    
    warning(message, title = 'Advertencia') {
      return this.show({ type: 'warning', title, message });
    },
    
    info(message, title = 'Información') {
      return this.show({ type: 'info', title, message });
    }
  };

  
  // ===========================
  // THEME SWITCHER (Modo Oscuro)
  // ===========================
  
  const Theme = {
    // Cambiar tema
    toggle() {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('lnv-theme', newTheme);
      
      return newTheme;
    },
    
    // Establecer tema
    set(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('lnv-theme', theme);
    },
    
    // Obtener tema actual
    get() {
      return document.documentElement.getAttribute('data-theme') || 'light';
    },
    
    // Inicializar tema
    init() {
      // Cargar tema guardado
      const savedTheme = localStorage.getItem('lnv-theme') || 'light';
      this.set(savedTheme);
      
      // Toggle con botones
      Utils.$$('[data-toggle="theme"]').forEach(btn => {
        Utils.on(btn, 'click', () => {
          this.toggle();
        });
      });
    }
  };

  
  // ===========================
  // LOADING OVERLAY
  // ===========================
  
  const Loading = {
    overlay: null,
    
    // Mostrar loading
    show(message = 'Cargando...') {
      if (this.overlay) return;
      
      this.overlay = Utils.create('div', {
        class: 'lnv-loading-overlay',
        html: `
          <div>
            <div class="lnv-spinner lnv-spinner-lg"></div>
            <p style="margin-top: 1rem; color: var(--lnv-dark);">${message}</p>
          </div>
        `
      });
      
      document.body.appendChild(this.overlay);
    },
    
    // Ocultar loading
    hide() {
      if (this.overlay && this.overlay.parentNode) {
        this.overlay.parentNode.removeChild(this.overlay);
        this.overlay = null;
      }
    }
  };

  
  // ===========================
  // CONFIRMACIÓN
  // ===========================
  
  const Confirm = {
    // Mostrar confirmación
    show(options = {}) {
      const defaults = {
        title: '¿Estás seguro?',
        message: '',
        confirmText: 'Confirmar',
        cancelText: 'Cancelar',
        onConfirm: () => {},
        onCancel: () => {}
      };
      
      const config = { ...defaults, ...options };
      const modalId = Utils.generateId();
      
      const modal = Utils.create('div', {
        id: modalId,
        class: 'lnv-modal active',
        html: `
          <div class="lnv-modal-backdrop"></div>
          <div class="lnv-modal-content lnv-modal-sm">
            <div class="lnv-modal-header">
              <h3 class="lnv-modal-title">${config.title}</h3>
            </div>
            <div class="lnv-modal-body">
              ${config.message}
            </div>
            <div class="lnv-modal-footer">
              <button class="lnv-btn lnv-btn-light" data-action="cancel">
                ${config.cancelText}
              </button>
              <button class="lnv-btn lnv-btn-primary" data-action="confirm">
                ${config.confirmText}
              </button>
            </div>
          </div>
        `
      });
      
      document.body.appendChild(modal);
      document.body.style.overflow = 'hidden';
      
      // Manejar botones
      const confirmBtn = modal.querySelector('[data-action="confirm"]');
      const cancelBtn = modal.querySelector('[data-action="cancel"]');
      const backdrop = modal.querySelector('.lnv-modal-backdrop');
      
      const cleanup = () => {
        document.body.removeChild(modal);
        document.body.style.overflow = '';
      };
      
      Utils.on(confirmBtn, 'click', () => {
        config.onConfirm();
        cleanup();
      });
      
      Utils.on(cancelBtn, 'click', () => {
        config.onCancel();
        cleanup();
      });
      
      Utils.on(backdrop, 'click', () => {
        config.onCancel();
        cleanup();
      });
    }
  };

  
  // ===========================
  // INICIALIZACIÓN
  // ===========================
  
  function init() {
    // Inicializar todos los componentes cuando el DOM esté listo
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initComponents);
    } else {
      initComponents();
    }
  }
  
  function initComponents() {
    Modal.init();
    Dropdown.init();
    Tabs.init();
    Accordion.init();
    Sidebar.init();
    Alert.init();
    Theme.init();
    
    console.log('✅ LNV Framework inicializado correctamente');
  }
  
  // Auto-inicializar
  init();
  
  // API Pública
  return {
    Utils,
    Modal,
    Dropdown,
    Tabs,
    Accordion,
    Sidebar,
    Alert,
    Toast,
    Theme,
    Loading,
    Confirm,
    init: initComponents
  };
})();

// Hacer disponible globalmente
window.LNV = LNV;