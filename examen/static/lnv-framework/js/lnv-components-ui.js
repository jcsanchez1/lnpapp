/**
 * ====================================
 * LNV FRAMEWORK - UI COMPONENTS
 * Drawer, Range Slider, Date Picker, File Upload
 * ====================================
 */

const LNVUIComponents = (function() {
  'use strict';

  // ===========================
  // DRAWER / OFFCANVAS
  // ===========================
  
  class Drawer {
    constructor(element, options = {}) {
      this.drawer = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.drawer) {
        console.error('Drawer: Elemento no encontrado');
        return;
      }

      this.config = {
        position: 'left', // 'left', 'right', 'top', 'bottom'
        backdrop: true,
        keyboard: true,
        onOpen: null,
        onClose: null,
        ...options
      };

      this.isOpen = false;
      this.overlay = null;

      this.init();
    }

    init() {
      // Aplicar posición
      this.drawer.classList.add(`lnv-drawer-${this.config.position}`);

      // Crear overlay si es necesario
      if (this.config.backdrop) {
        this.createOverlay();
      }

      // Buscar botón de cierre
      const closeBtn = this.drawer.querySelector('.lnv-drawer-close');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => this.close());
      }

      // Keyboard
      if (this.config.keyboard) {
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && this.isOpen) {
            this.close();
          }
        });
      }

      console.log('✅ Drawer inicializado');
    }

    createOverlay() {
      this.overlay = document.createElement('div');
      this.overlay.className = 'lnv-drawer-overlay';
      this.overlay.addEventListener('click', () => this.close());
      document.body.appendChild(this.overlay);
    }

    open() {
      this.drawer.classList.add('active');
      if (this.overlay) {
        this.overlay.classList.add('active');
      }
      document.body.style.overflow = 'hidden';
      this.isOpen = true;

      if (this.config.onOpen) {
        this.config.onOpen(this);
      }
    }

    close() {
      this.drawer.classList.remove('active');
      if (this.overlay) {
        this.overlay.classList.remove('active');
      }
      document.body.style.overflow = '';
      this.isOpen = false;

      if (this.config.onClose) {
        this.config.onClose(this);
      }
    }

    toggle() {
      if (this.isOpen) {
        this.close();
      } else {
        this.open();
      }
    }

    destroy() {
      if (this.overlay && this.overlay.parentNode) {
        this.overlay.parentNode.removeChild(this.overlay);
      }
    }
  }


  // ===========================
  // RANGE SLIDER
  // ===========================
  
  class RangeSlider {
    constructor(element, options = {}) {
      this.input = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.input) {
        console.error('RangeSlider: Elemento no encontrado');
        return;
      }

      this.config = {
        min: parseFloat(this.input.min) || 0,
        max: parseFloat(this.input.max) || 100,
        step: parseFloat(this.input.step) || 1,
        value: parseFloat(this.input.value) || 0,
        showValue: true,
        showTooltip: false,
        showLabels: false,
        prefix: '',
        suffix: '',
        onChange: null,
        ...options
      };

      this.value = this.config.value;

      this.init();
    }

    init() {
      // Crear wrapper si no existe
      if (!this.input.parentElement.classList.contains('lnv-range-wrapper')) {
        const wrapper = document.createElement('div');
        wrapper.className = 'lnv-range-wrapper';
        this.input.parentNode.insertBefore(wrapper, this.input);
        wrapper.appendChild(this.input);
      }

      this.wrapper = this.input.parentElement;
      this.input.classList.add('lnv-range');

      // Crear track progress
      this.createTrack();

      // Mostrar valor si es necesario
      if (this.config.showValue) {
        this.createValueDisplay();
      }

      // Mostrar tooltip si es necesario
      if (this.config.showTooltip) {
        this.createTooltip();
      }

      // Mostrar labels si es necesario
      if (this.config.showLabels) {
        this.createLabels();
      }

      // Establecer valores
      this.input.min = this.config.min;
      this.input.max = this.config.max;
      this.input.step = this.config.step;
      this.input.value = this.config.value;

      // Events
      this.input.addEventListener('input', () => {
        this.value = parseFloat(this.input.value);
        this.update();

        if (this.config.onChange) {
          this.config.onChange(this.value, this);
        }
      });

      this.update();
      console.log('✅ RangeSlider inicializado');
    }

    createTrack() {
      this.track = document.createElement('div');
      this.track.className = 'lnv-range-track';
      this.wrapper.appendChild(this.track);
    }

    createValueDisplay() {
      this.valueDisplay = document.createElement('div');
      this.valueDisplay.className = 'lnv-range-value';
      this.wrapper.appendChild(this.valueDisplay);
    }

    createTooltip() {
      this.tooltip = document.createElement('div');
      this.tooltip.className = 'lnv-range-tooltip';
      this.wrapper.appendChild(this.tooltip);
    }

    createLabels() {
      const labels = document.createElement('div');
      labels.className = 'lnv-range-labels';
      labels.innerHTML = `
        <span>${this.config.prefix}${this.config.min}${this.config.suffix}</span>
        <span>${this.config.prefix}${this.config.max}${this.config.suffix}</span>
      `;
      this.wrapper.appendChild(labels);
    }

    update() {
      const percent = ((this.value - this.config.min) / (this.config.max - this.config.min)) * 100;
      
      // Actualizar track
      if (this.track) {
        this.track.style.width = `${percent}%`;
      }

      // Actualizar valor
      const displayValue = `${this.config.prefix}${this.value}${this.config.suffix}`;
      
      if (this.valueDisplay) {
        this.valueDisplay.textContent = displayValue;
      }

      if (this.tooltip) {
        this.tooltip.textContent = displayValue;
        this.tooltip.style.left = `${percent}%`;
      }
    }

    setValue(value) {
      this.value = value;
      this.input.value = value;
      this.update();
    }

    getValue() {
      return this.value;
    }
  }


  // ===========================
  // DATE PICKER
  // ===========================
  
  class DatePicker {
    constructor(element, options = {}) {
      this.input = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.input) {
        console.error('DatePicker: Elemento no encontrado');
        return;
      }

      this.config = {
        format: 'dd/mm/yyyy',
        minDate: null,
        maxDate: null,
        startDate: new Date(),
        onChange: null,
        onSelect: null,
        ...options
      };

      this.selectedDate = null;
      this.currentMonth = this.config.startDate.getMonth();
      this.currentYear = this.config.startDate.getFullYear();
      this.calendar = null;

      this.init();
    }

    init() {
      // Crear wrapper
      const wrapper = document.createElement('div');
      wrapper.className = 'lnv-datepicker';
      this.input.parentNode.insertBefore(wrapper, this.input);
      wrapper.appendChild(this.input);

      this.wrapper = wrapper;
      this.input.classList.add('lnv-datepicker-input');
      this.input.readOnly = true;

      // Agregar icono
      const icon = document.createElement('span');
      icon.className = 'lnv-datepicker-icon';
      icon.innerHTML = '📅';
      wrapper.appendChild(icon);

      // Crear calendario
      this.createCalendar();
    // Events
      this.input.addEventListener('click', () => this.toggle());
      icon.addEventListener('click', () => this.toggle());

      document.addEventListener('click', (e) => {
        if (!wrapper.contains(e.target) && this.calendar.classList.contains('active')) {
          this.close();
        }
      });

      console.log('✅ DatePicker inicializado');
    }

    createCalendar() {
      this.calendar = document.createElement('div');
      this.calendar.className = 'lnv-datepicker-calendar';
      this.wrapper.appendChild(this.calendar);
      this.renderCalendar();
    }

    renderCalendar() {
      const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
      
      const weekdays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

      // Header
      const header = `
        <div class="lnv-datepicker-header">
          <button type="button" data-action="prev-month">‹</button>
          <div class="lnv-datepicker-month-year">
            ${monthNames[this.currentMonth]} ${this.currentYear}
          </div>
          <button type="button" data-action="next-month">›</button>
        </div>
      `;

      // Weekdays
      const weekdaysHtml = `
        <div class="lnv-datepicker-weekdays">
          ${weekdays.map(day => `<div class="lnv-datepicker-weekday">${day}</div>`).join('')}
        </div>
      `;

      // Days
      const daysHtml = this.renderDays();

      this.calendar.innerHTML = header + weekdaysHtml + daysHtml;

      // Attach events
      this.calendar.querySelector('[data-action="prev-month"]').addEventListener('click', () => {
        this.currentMonth--;
        if (this.currentMonth < 0) {
          this.currentMonth = 11;
          this.currentYear--;
        }
        this.renderCalendar();
      });

      this.calendar.querySelector('[data-action="next-month"]').addEventListener('click', () => {
        this.currentMonth++;
        if (this.currentMonth > 11) {
          this.currentMonth = 0;
          this.currentYear++;
        }
        this.renderCalendar();
      });

      // Day click events
      this.calendar.querySelectorAll('.lnv-datepicker-day').forEach(day => {
        day.addEventListener('click', () => {
          const date = day.dataset.date;
          if (date) {
            this.selectDate(new Date(date));
          }
        });
      });
    }

    renderDays() {
      const firstDay = new Date(this.currentYear, this.currentMonth, 1);
      const lastDay = new Date(this.currentYear, this.currentMonth + 1, 0);
      const prevLastDay = new Date(this.currentYear, this.currentMonth, 0);
      
      const firstDayIndex = firstDay.getDay();
      const lastDayDate = lastDay.getDate();
      const prevLastDayDate = prevLastDay.getDate();

      let days = '<div class="lnv-datepicker-days">';

      // Previous month days
      for (let i = firstDayIndex; i > 0; i--) {
        const date = new Date(this.currentYear, this.currentMonth - 1, prevLastDayDate - i + 1);
        days += `<button type="button" class="lnv-datepicker-day other-month" data-date="${date.toISOString()}">${prevLastDayDate - i + 1}</button>`;
      }

      // Current month days
      for (let i = 1; i <= lastDayDate; i++) {
        const date = new Date(this.currentYear, this.currentMonth, i);
        const isToday = this.isToday(date);
        const isSelected = this.selectedDate && this.isSameDay(date, this.selectedDate);
        
        let classes = 'lnv-datepicker-day';
        if (isToday) classes += ' today';
        if (isSelected) classes += ' selected';

        days += `<button type="button" class="${classes}" data-date="${date.toISOString()}">${i}</button>`;
      }

      days += '</div>';
      return days;
    }

    isToday(date) {
      const today = new Date();
      return this.isSameDay(date, today);
    }

    isSameDay(date1, date2) {
      return date1.getDate() === date2.getDate() &&
             date1.getMonth() === date2.getMonth() &&
             date1.getFullYear() === date2.getFullYear();
    }

    selectDate(date) {
      this.selectedDate = date;
      this.input.value = this.formatDate(date);
      this.renderCalendar();
      this.close();

      if (this.config.onSelect) {
        this.config.onSelect(date, this);
      }
    }

    formatDate(date) {
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();

      return this.config.format
        .replace('dd', day)
        .replace('mm', month)
        .replace('yyyy', year);
    }

    toggle() {
      if (this.calendar.classList.contains('active')) {
        this.close();
      } else {
        this.open();
      }
    }

    open() {
      this.calendar.classList.add('active');
    }

    close() {
      this.calendar.classList.remove('active');
    }

    getValue() {
      return this.selectedDate;
    }

    setValue(date) {
      this.selectDate(new Date(date));
    }
  }


  // ===========================
  // FILE UPLOAD (DRAG & DROP)
  // ===========================
  
  class FileUpload {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('FileUpload: Elemento no encontrado');
        return;
      }

      this.config = {
        multiple: true,
        accept: '*',
        maxSize: 10 * 1024 * 1024, // 10MB
        maxFiles: 10,
        showPreview: true,
        autoUpload: false,
        uploadUrl: null,
        onSelect: null,
        onUpload: null,
        onError: null,
        onProgress: null,
        ...options
      };

      this.files = [];
      this.input = null;

      this.init();
    }

    init() {
      this.container.classList.add('lnv-file-upload');

      // Crear estructura HTML
      this.container.innerHTML = `
        <input type="file" ${this.config.multiple ? 'multiple' : ''} accept="${this.config.accept}">
        <div class="lnv-file-upload-icon">📁</div>
        <div class="lnv-file-upload-text">Arrastra archivos aquí</div>
        <div class="lnv-file-upload-hint">o haz clic para seleccionar</div>
      `;

      this.input = this.container.querySelector('input[type="file"]');

      // Crear lista de archivos
      if (this.config.showPreview) {
        this.fileList = document.createElement('div');
        this.fileList.className = 'lnv-file-list';
        this.container.parentNode.insertBefore(this.fileList, this.container.nextSibling);
      }

      // Events
      this.attachEvents();

      console.log('✅ FileUpload inicializado');
    }

    attachEvents() {
      // Input change
      this.input.addEventListener('change', (e) => {
        this.handleFiles(e.target.files);
      });

      // Drag & Drop
      this.container.addEventListener('dragover', (e) => {
        e.preventDefault();
        this.container.classList.add('dragging');
      });

      this.container.addEventListener('dragleave', () => {
        this.container.classList.remove('dragging');
      });

      this.container.addEventListener('drop', (e) => {
        e.preventDefault();
        this.container.classList.remove('dragging');
        this.handleFiles(e.dataTransfer.files);
      });
    }

    handleFiles(fileList) {
      const filesArray = Array.from(fileList);

      // Validar cantidad
      if (this.files.length + filesArray.length > this.config.maxFiles) {
        if (this.config.onError) {
          this.config.onError(`Máximo ${this.config.maxFiles} archivos permitidos`);
        }
        return;
      }

      // Validar tamaño
      const invalidFiles = filesArray.filter(file => file.size > this.config.maxSize);
      if (invalidFiles.length > 0) {
        if (this.config.onError) {
          this.config.onError('Algunos archivos exceden el tamaño máximo permitido');
        }
        return;
      }

      // Agregar archivos
      filesArray.forEach(file => {
        this.addFile(file);
      });

      // Callback
      if (this.config.onSelect) {
        this.config.onSelect(this.files, this);
      }

      // Auto upload
      if (this.config.autoUpload && this.config.uploadUrl) {
        this.uploadAll();
      }
    }

    addFile(file) {
      const fileData = {
        file: file,
        id: Date.now() + Math.random(),
        name: file.name,
        size: this.formatFileSize(file.size),
        progress: 0,
        uploaded: false
      };

      this.files.push(fileData);

      if (this.config.showPreview) {
        this.renderFileItem(fileData);
      }
    }

    renderFileItem(fileData) {
      const fileItem = document.createElement('div');
      fileItem.className = 'lnv-file-item';
      fileItem.dataset.id = fileData.id;

      const icon = this.getFileIcon(fileData.file);

      fileItem.innerHTML = `
        <div class="lnv-file-icon">${icon}</div>
        <div class="lnv-file-info">
          <div class="lnv-file-name">${fileData.name}</div>
          <div class="lnv-file-size">${fileData.size}</div>
          ${this.config.uploadUrl ? '<div class="lnv-file-progress"><div class="lnv-file-progress-bar"><div class="lnv-file-progress-fill" style="width: 0%"></div></div></div>' : ''}
        </div>
        <button type="button" class="lnv-file-remove">×</button>
      `;

      // Remove button
      fileItem.querySelector('.lnv-file-remove').addEventListener('click', () => {
        this.removeFile(fileData.id);
      });

      this.fileList.appendChild(fileItem);
    }

    removeFile(id) {
      this.files = this.files.filter(f => f.id !== id);
      
      const fileItem = this.fileList.querySelector(`[data-id="${id}"]`);
      if (fileItem) {
        fileItem.style.animation = 'lnv-fade-out 0.3s';
        setTimeout(() => fileItem.remove(), 300);
      }
    }

    getFileIcon(file) {
      const type = file.type;
      
      if (type.startsWith('image/')) return '🖼️';
      if (type.startsWith('video/')) return '🎬';
      if (type.startsWith('audio/')) return '🎵';
      if (type.includes('pdf')) return '📄';
      if (type.includes('word') || type.includes('document')) return '📝';
      if (type.includes('excel') || type.includes('sheet')) return '📊';
      if (type.includes('zip') || type.includes('rar')) return '🗜️';
      
      return '📎';
    }

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    uploadAll() {
      this.files.forEach(fileData => {
        if (!fileData.uploaded) {
          this.uploadFile(fileData);
        }
      });
    }

    uploadFile(fileData) {
      if (!this.config.uploadUrl) return;

      const formData = new FormData();
      formData.append('file', fileData.file);

      const xhr = new XMLHttpRequest();

      // Progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percent = (e.loaded / e.total) * 100;
          fileData.progress = percent;
          this.updateProgress(fileData.id, percent);

          if (this.config.onProgress) {
            this.config.onProgress(percent, fileData, this);
          }
        }
      });

      // Complete
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          fileData.uploaded = true;
          this.updateProgress(fileData.id, 100);

          if (this.config.onUpload) {
            this.config.onUpload(xhr.response, fileData, this);
          }
        } else {
          if (this.config.onError) {
            this.config.onError(`Error al subir ${fileData.name}`, fileData);
          }
        }
      });

      // Error
      xhr.addEventListener('error', () => {
        if (this.config.onError) {
          this.config.onError(`Error al subir ${fileData.name}`, fileData);
        }
      });

      xhr.open('POST', this.config.uploadUrl);
      xhr.send(formData);
    }

    updateProgress(id, percent) {
      const fileItem = this.fileList.querySelector(`[data-id="${id}"]`);
      if (fileItem) {
        const progressFill = fileItem.querySelector('.lnv-file-progress-fill');
        if (progressFill) {
          progressFill.style.width = `${percent}%`;
        }
      }
    }

    getFiles() {
      return this.files;
    }

    clear() {
      this.files = [];
      if (this.fileList) {
        this.fileList.innerHTML = '';
      }
      this.input.value = '';
    }
  }


  // ===========================
  // AUTO-INICIALIZACIÓN
  // ===========================
  
  function init() {
    // Inicializar Drawers
    document.querySelectorAll('[data-drawer]').forEach(element => {
      const options = element.getAttribute('data-drawer-options');
      const config = options ? JSON.parse(options) : {};
      new Drawer(element, config);
    });

    // Inicializar Range Sliders
    document.querySelectorAll('[data-range]').forEach(element => {
      const options = element.getAttribute('data-range-options');
      const config = options ? JSON.parse(options) : {};
      new RangeSlider(element, config);
    });

    // Inicializar Date Pickers
    document.querySelectorAll('[data-datepicker]').forEach(element => {
      const options = element.getAttribute('data-datepicker-options');
      const config = options ? JSON.parse(options) : {};
      new DatePicker(element, config);
    });

    // Inicializar File Uploads
    document.querySelectorAll('[data-file-upload]').forEach(element => {
      const options = element.getAttribute('data-upload-options');
      const config = options ? JSON.parse(options) : {};
      new FileUpload(element, config);
    });

    console.log('✅ LNV UI Components inicializados');
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
    Drawer,
    RangeSlider,
    DatePicker,
    FileUpload,
    init
  };
})();

// Exportar globalmente
window.LNVUIComponents = LNVUIComponents;