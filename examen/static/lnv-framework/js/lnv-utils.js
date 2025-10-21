/**
 * ====================================
 * LNV FRAMEWORK - UTILITIES
 * Utilidades y helpers JavaScript
 * ====================================
 */

const LNVUtils = (function() {
  'use strict';

  // ===========================
  // DEBOUNCE & THROTTLE
  // ===========================
  
  /**
   * Debounce - Ejecuta función después de que pasen X ms sin llamadas
   * @param {Function} func - Función a ejecutar
   * @param {Number} wait - Tiempo de espera en ms
   * @returns {Function}
   * @example
   * const debouncedSearch = LNVUtils.debounce(searchFunction, 300);
   */
  function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * Throttle - Ejecuta función máximo una vez cada X ms
   * @param {Function} func - Función a ejecutar
   * @param {Number} limit - Límite de tiempo en ms
   * @returns {Function}
   * @example
   * const throttledScroll = LNVUtils.throttle(onScroll, 100);
   */
  function throttle(func, limit = 300) {
    let inThrottle;
    return function executedFunction(...args) {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }


  // ===========================
  // LOCAL STORAGE HELPERS
  // ===========================
  
  const Storage = {
    /**
     * Guardar en localStorage con manejo de errores
     * @param {String} key - Llave del item
     * @param {*} value - Valor a guardar (se convierte a JSON)
     * @returns {Boolean} - true si se guardó correctamente
     */
    set(key, value) {
      try {
        const serialized = JSON.stringify(value);
        localStorage.setItem(key, serialized);
        return true;
      } catch (error) {
        console.error('Error guardando en localStorage:', error);
        return false;
      }
    },

    /**
     * Obtener de localStorage
     * @param {String} key - Llave del item
     * @param {*} defaultValue - Valor por defecto si no existe
     * @returns {*} - Valor parseado o defaultValue
     */
    get(key, defaultValue = null) {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch (error) {
        console.error('Error leyendo de localStorage:', error);
        return defaultValue;
      }
    },

    /**
     * Remover item de localStorage
     * @param {String} key - Llave del item
     */
    remove(key) {
      try {
        localStorage.removeItem(key);
        return true;
      } catch (error) {
        console.error('Error removiendo de localStorage:', error);
        return false;
      }
    },

    /**
     * Limpiar todo el localStorage
     */
    clear() {
      try {
        localStorage.clear();
        return true;
      } catch (error) {
        console.error('Error limpiando localStorage:', error);
        return false;
      }
    },

    /**
     * Verificar si una key existe
     * @param {String} key - Llave a verificar
     * @returns {Boolean}
     */
    has(key) {
      return localStorage.getItem(key) !== null;
    }
  };


  // ===========================
  // API FETCH WRAPPER
  // ===========================
  
  /**
   * Wrapper para fetch con configuración por defecto
   * @param {String} url - URL del endpoint
   * @param {Object} options - Opciones de fetch
   * @returns {Promise}
   * @example
   * LNVUtils.api('/api/users', { method: 'POST', body: data })
   */
  async function api(url, options = {}) {
    const defaults = {
      headers: {
        'Content-Type': 'application/json',
      }
    };

    const config = {
      ...defaults,
      ...options,
      headers: {
        ...defaults.headers,
        ...options.headers
      }
    };

    // Convertir body a JSON si es objeto
    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      
      // Verificar si la respuesta es JSON
      const contentType = response.headers.get('content-type');
      const isJson = contentType && contentType.includes('application/json');
      
      const data = isJson ? await response.json() : await response.text();

      if (!response.ok) {
        throw {
          status: response.status,
          statusText: response.statusText,
          data
        };
      }

      return data;
    } catch (error) {
      console.error('Error en API call:', error);
      throw error;
    }
  }


  // ===========================
  // DATE FORMATTING
  // ===========================
  
  const DateUtils = {
    /**
     * Formatear fecha a formato local
     * @param {Date|String} date - Fecha a formatear
     * @param {String} format - Formato: 'short', 'long', 'time', 'datetime'
     * @returns {String}
     */
    format(date, format = 'short') {
      const d = new Date(date);
      
      if (isNaN(d.getTime())) {
        return 'Fecha inválida';
      }

      const options = {
        short: { year: 'numeric', month: '2-digit', day: '2-digit' },
        long: { year: 'numeric', month: 'long', day: 'numeric' },
        time: { hour: '2-digit', minute: '2-digit' },
        datetime: { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }
      };

      return d.toLocaleDateString('es-HN', options[format] || options.short);
    },

    /**
     * Obtener fecha relativa (hace X días)
     * @param {Date|String} date - Fecha
     * @returns {String}
     */
    relative(date) {
      const d = new Date(date);
      const now = new Date();
      const diff = now - d;
      
      const seconds = Math.floor(diff / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      const months = Math.floor(days / 30);
      const years = Math.floor(days / 365);

      if (seconds < 60) return 'Hace un momento';
      if (minutes < 60) return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
      if (hours < 24) return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
      if (days < 30) return `Hace ${days} día${days > 1 ? 's' : ''}`;
      if (months < 12) return `Hace ${months} mes${months > 1 : 'es'}`;
      return `Hace ${years} año${years > 1 ? 's' : ''}`;
    },

    /**
     * Verificar si una fecha es hoy
     * @param {Date|String} date
     * @returns {Boolean}
     */
    isToday(date) {
      const d = new Date(date);
      const today = new Date();
      return d.getDate() === today.getDate() &&
             d.getMonth() === today.getMonth() &&
             d.getFullYear() === today.getFullYear();
    }
  };


  // ===========================
  // NUMBER FORMATTING
  // ===========================
  
  const NumberUtils = {
    /**
     * Formatear número a moneda (Lempiras)
     * @param {Number} number - Número a formatear
     * @param {String} currency - Código de moneda (default: HNL)
     * @returns {String}
     */
    currency(number, currency = 'HNL') {
      return new Intl.NumberFormat('es-HN', {
        style: 'currency',
        currency: currency
      }).format(number);
    },

    /**
     * Formatear número con separadores de miles
     * @param {Number} number - Número a formatear
     * @param {Number} decimals - Cantidad de decimales
     * @returns {String}
     */
    format(number, decimals = 0) {
      return new Intl.NumberFormat('es-HN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(number);
    },

    /**
     * Formatear número a porcentaje
     * @param {Number} number - Número (0-1 o 0-100)
     * @param {Number} decimals - Decimales a mostrar
     * @returns {String}
     */
    percentage(number, decimals = 0) {
      const value = number > 1 ? number / 100 : number;
      return new Intl.NumberFormat('es-HN', {
        style: 'percent',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(value);
    },

    /**
     * Abreviar números grandes (1000 -> 1K, 1000000 -> 1M)
     * @param {Number} number - Número a abreviar
     * @returns {String}
     */
    abbreviate(number) {
      if (number < 1000) return number.toString();
      if (number < 1000000) return (number / 1000).toFixed(1) + 'K';
      if (number < 1000000000) return (number / 1000000).toFixed(1) + 'M';
      return (number / 1000000000).toFixed(1) + 'B';
    }
  };


  // ===========================
  // COPY TO CLIPBOARD
  // ===========================
  
  /**
   * Copiar texto al portapapeles
   * @param {String} text - Texto a copiar
   * @returns {Promise<Boolean>}
   * @example
   * LNVUtils.copyToClipboard('Hola mundo').then(() => alert('Copiado!'));
   */
  async function copyToClipboard(text) {
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
        return true;
      } else {
        // Fallback para navegadores antiguos
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textarea);
        return success;
      }
    } catch (error) {
      console.error('Error copiando al portapapeles:', error);
      return false;
    }
  }


  // ===========================
  // QUERY STRING HELPERS
  // ===========================
  
  const QueryString = {
    /**
     * Parsear query string a objeto
     * @param {String} search - Query string (opcional, usa window.location.search)
     * @returns {Object}
     */
    parse(search = window.location.search) {
      const params = new URLSearchParams(search);
      const result = {};
      for (const [key, value] of params) {
        result[key] = value;
      }
      return result;
    },

    /**
     * Convertir objeto a query string
     * @param {Object} obj - Objeto con parámetros
     * @returns {String}
     */
    stringify(obj) {
      const params = new URLSearchParams();
      Object.keys(obj).forEach(key => {
        if (obj[key] !== null && obj[key] !== undefined) {
          params.append(key, obj[key]);
        }
      });
      return params.toString();
    },

    /**
     * Obtener un parámetro específico
     * @param {String} param - Nombre del parámetro
     * @returns {String|null}
     */
    get(param) {
      const params = new URLSearchParams(window.location.search);
      return params.get(param);
    },

    /**
     * Actualizar parámetros en la URL sin recargar
     * @param {Object} params - Parámetros a actualizar
     */
    update(params) {
      const current = this.parse();
      const updated = { ...current, ...params };
      const newQuery = this.stringify(updated);
      const newUrl = window.location.pathname + (newQuery ? '?' + newQuery : '');
      window.history.pushState({}, '', newUrl);
    }
  };


  // ===========================
  // COOKIE MANAGEMENT
  // ===========================
  
  const Cookie = {
    /**
     * Establecer cookie
     * @param {String} name - Nombre de la cookie
     * @param {String} value - Valor
     * @param {Number} days - Días hasta expiración
     */
    set(name, value, days = 7) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      const expires = "expires=" + date.toUTCString();
      document.cookie = `${name}=${value};${expires};path=/`;
    },

    /**
     * Obtener cookie
     * @param {String} name - Nombre de la cookie
     * @returns {String|null}
     */
    get(name) {
      const nameEQ = name + "=";
      const ca = document.cookie.split(';');
      for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
      }
      return null;
    },

    /**
     * Eliminar cookie
     * @param {String} name - Nombre de la cookie
     */
    remove(name) {
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
    },

    /**
     * Verificar si existe una cookie
     * @param {String} name - Nombre de la cookie
     * @returns {Boolean}
     */
    has(name) {
      return this.get(name) !== null;
    }
  };


  // ===========================
  // STRING UTILITIES
  // ===========================
  
  const StringUtils = {
    /**
     * Capitalizar primera letra
     * @param {String} str
     * @returns {String}
     */
    capitalize(str) {
      return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    },

    /**
     * Convertir a title case
     * @param {String} str
     * @returns {String}
     */
    titleCase(str) {
      return str.toLowerCase().split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
    },

    /**
     * Generar slug desde texto
     * @param {String} str
     * @returns {String}
     */
    slugify(str) {
      return str
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
    },

    /**
     * Truncar texto
     * @param {String} str - Texto a truncar
     * @param {Number} length - Longitud máxima
     * @param {String} suffix - Sufijo (default: '...')
     * @returns {String}
     */
    truncate(str, length = 50, suffix = '...') {
      if (str.length <= length) return str;
      return str.substring(0, length).trim() + suffix;
    },

    /**
     * Generar string aleatorio
     * @param {Number} length - Longitud del string
     * @returns {String}
     */
    random(length = 8) {
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      let result = '';
      for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return result;
    }
  };


  // ===========================
  // ARRAY UTILITIES
  // ===========================
  
  const ArrayUtils = {
    /**
     * Dividir array en chunks
     * @param {Array} array
     * @param {Number} size - Tamaño de cada chunk
     * @returns {Array}
     */
    chunk(array, size) {
      const chunks = [];
      for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
      }
      return chunks;
    },

    /**
     * Remover duplicados
     * @param {Array} array
     * @returns {Array}
     */
    unique(array) {
      return [...new Set(array)];
    },

    /**
     * Ordenar array de objetos por propiedad
     * @param {Array} array
     * @param {String} key - Propiedad a ordenar
     * @param {String} order - 'asc' o 'desc'
     * @returns {Array}
     */
    sortBy(array, key, order = 'asc') {
      return [...array].sort((a, b) => {
        const valueA = a[key];
        const valueB = b[key];
        
        if (valueA < valueB) return order === 'asc' ? -1 : 1;
        if (valueA > valueB) return order === 'asc' ? 1 : -1;
        return 0;
      });
    },

    /**
     * Agrupar array de objetos por propiedad
     * @param {Array} array
     * @param {String} key - Propiedad para agrupar
     * @returns {Object}
     */
    groupBy(array, key) {
      return array.reduce((result, item) => {
        const group = item[key];
        result[group] = result[group] || [];
        result[group].push(item);
        return result;
      }, {});
    }
  };


  // ===========================
  // VALIDATORS
  // ===========================
  
  const Validators = {
    /**
     * Validar email
     * @param {String} email
     * @returns {Boolean}
     */
    isEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    },

    /**
     * Validar DNI Honduras (13 dígitos)
     * @param {String} dni
     * @returns {Boolean}
     */
    isDNI(dni) {
      const cleaned = dni.replace(/\D/g, '');
      return cleaned.length === 13;
    },

    /**
     * Validar teléfono Honduras
     * @param {String} phone
     * @returns {Boolean}
     */
    isPhone(phone) {
      const cleaned = phone.replace(/\D/g, '');
      return cleaned.length === 8 || cleaned.length === 11;
    },

    /**
     * Validar URL
     * @param {String} url
     * @returns {Boolean}
     */
    isURL(url) {
      try {
        new URL(url);
        return true;
      } catch {
        return false;
      }
    },

    /**
     * Validar que no esté vacío
     * @param {*} value
     * @returns {Boolean}
     */
    isNotEmpty(value) {
      if (value === null || value === undefined) return false;
      if (typeof value === 'string') return value.trim().length > 0;
      if (Array.isArray(value)) return value.length > 0;
      return true;
    }
  };


  // ===========================
  // SCROLL UTILITIES
  // ===========================
  
  const Scroll = {
    /**
     * Scroll suave a elemento
     * @param {String|Element} target - Selector o elemento
     * @param {Number} offset - Offset desde el top
     */
    to(target, offset = 0) {
      const element = typeof target === 'string' ? 
        document.querySelector(target) : target;
      
      if (element) {
        const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    },

    /**
     * Scroll al top de la página
     */
    toTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    /**
     * Obtener posición del scroll
     * @returns {Object} { x, y }
     */
    getPosition() {
      return {
        x: window.pageXOffset,
        y: window.pageYOffset
      };
    },

    /**
     * Verificar si está en el viewport
     * @param {Element} element
     * @returns {Boolean}
     */
    isInViewport(element) {
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= window.innerHeight &&
        rect.right <= window.innerWidth
      );
    }
  };


  // ===========================
  // DEVICE DETECTION
  // ===========================
  
  const Device = {
    /**
     * Detectar si es móvil
     * @returns {Boolean}
     */
    isMobile() {
      return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },

    /**
     * Detectar si es tablet
     * @returns {Boolean}
     */
    isTablet() {
      return /iPad|Android/i.test(navigator.userAgent) && !this.isMobile();
    },

    /**
     * Detectar si es desktop
     * @returns {Boolean}
     */
    isDesktop() {
      return !this.isMobile() && !this.isTablet();
    },

    /**
     * Obtener tamaño de viewport
     * @returns {Object} { width, height }
     */
    getViewport() {
      return {
        width: window.innerWidth,
        height: window.innerHeight
      };
    }
  };


  // ===========================
  // GENERAR ID ÚNICO
  // ===========================
  
  /**
   * Generar ID único
   * @param {String} prefix - Prefijo opcional
   * @returns {String}
   */
  function generateId(prefix = 'lnv') {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }


  // ===========================
  // SLEEP/DELAY
  // ===========================
  
  /**
   * Pausar ejecución por X milisegundos
   * @param {Number} ms - Milisegundos
   * @returns {Promise}
   * @example
   * await LNVUtils.sleep(1000); // Espera 1 segundo
   */
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }


  // ===========================
  // API PÚBLICA
  // ===========================
  
  return {
    debounce,
    throttle,
    Storage,
    api,
    DateUtils,
    NumberUtils,
    copyToClipboard,
    QueryString,
    Cookie,
    StringUtils,
    ArrayUtils,
    Validators,
    Scroll,
    Device,
    generateId,
    sleep
  };
})();

// Exportar globalmente
window.LNVUtils = LNVUtils;