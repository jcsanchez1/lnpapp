/**
 * ====================================
 * LNV FRAMEWORK - ADVANCED COMPONENTS 2
 * DataTable, Transfer List, Tree View, Image Gallery
 * ====================================
 */

const LNVAdvancedComponents = (function() {
  'use strict';

  // ===========================
  // DATA TABLE
  // ===========================
  
  class DataTable {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('DataTable: Elemento no encontrado');
        return;
      }

      this.config = {
        data: [],
        columns: [],
        sortable: true,
        searchable: true,
        pagination: true,
        pageSize: 10,
        selectable: false,
        actions: null,
        onSort: null,
        onSearch: null,
        onSelect: null,
        ...options
      };

      this.data = [...this.config.data];
      this.filteredData = [...this.data];
      this.currentPage = 1;
      this.sortColumn = null;
      this.sortDirection = 'asc';
      this.selectedRows = new Set();

      this.init();
    }

    init() {
      this.render();
      console.log('✅ DataTable inicializado');
    }

    render() {
      const wrapper = document.createElement('div');
      wrapper.className = 'lnv-datatable-wrapper';

      // Header
      if (this.config.searchable) {
        wrapper.appendChild(this.renderHeader());
      }

      // Table
      wrapper.appendChild(this.renderTable());

      // Footer
      if (this.config.pagination) {
        wrapper.appendChild(this.renderFooter());
      }

      this.container.innerHTML = '';
      this.container.appendChild(wrapper);
    }

    renderHeader() {
      const header = document.createElement('div');
      header.className = 'lnv-datatable-header';

      const searchWrapper = document.createElement('div');
      searchWrapper.className = 'lnv-datatable-search';
      
      const searchInput = document.createElement('input');
      searchInput.type = 'text';
      searchInput.className = 'lnv-form-control';
      searchInput.placeholder = 'Buscar...';
      searchInput.addEventListener('input', (e) => this.search(e.target.value));
      
      searchWrapper.appendChild(searchInput);
      header.appendChild(searchWrapper);

      return header;
    }

    renderTable() {
      const table = document.createElement('table');
      table.className = 'lnv-datatable';

      // Thead
      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');

      // Checkbox column
      if (this.config.selectable) {
        const th = document.createElement('th');
        th.className = 'lnv-datatable-checkbox';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.addEventListener('change', (e) => this.selectAll(e.target.checked));
        th.appendChild(checkbox);
        headerRow.appendChild(th);
      }

      // Data columns
      this.config.columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col.label;
        
        if (this.config.sortable && col.sortable !== false) {
          th.classList.add('sortable');
          th.addEventListener('click', () => this.sort(col.key));
          
          if (this.sortColumn === col.key) {
            th.classList.add(`sorted-${this.sortDirection}`);
          }
        }

        headerRow.appendChild(th);
      });

      // Actions column
      if (this.config.actions) {
        const th = document.createElement('th');
        th.textContent = 'Acciones';
        th.className = 'lnv-datatable-actions-cell';
        headerRow.appendChild(th);
      }

      thead.appendChild(headerRow);
      table.appendChild(thead);

      // Tbody
      const tbody = document.createElement('tbody');
      const startIndex = (this.currentPage - 1) * this.config.pageSize;
      const endIndex = startIndex + this.config.pageSize;
      const pageData = this.filteredData.slice(startIndex, endIndex);

      if (pageData.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = this.config.columns.length + (this.config.selectable ? 1 : 0) + (this.config.actions ? 1 : 0);
        td.className = 'lnv-datatable-empty';
        td.textContent = 'No hay datos disponibles';
        tr.appendChild(td);
        tbody.appendChild(tr);
      } else {
        pageData.forEach((row, index) => {
          const tr = document.createElement('tr');
          const rowIndex = startIndex + index;

          // Checkbox
          if (this.config.selectable) {
            const td = document.createElement('td');
            td.className = 'lnv-datatable-checkbox';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = this.selectedRows.has(rowIndex);
            checkbox.addEventListener('change', (e) => this.selectRow(rowIndex, e.target.checked));
            td.appendChild(checkbox);
            tr.appendChild(td);
          }

          // Data cells
          this.config.columns.forEach(col => {
            const td = document.createElement('td');
            
            if (col.render) {
              const rendered = col.render(row[col.key], row);
              if (typeof rendered === 'string') {
                td.innerHTML = rendered;
              } else {
                td.appendChild(rendered);
              }
            } else {
              td.textContent = row[col.key] || '';
            }

            tr.appendChild(td);
          });

          // Actions
          if (this.config.actions) {
            const td = document.createElement('td');
            td.className = 'lnv-datatable-actions-cell';
            td.appendChild(this.config.actions(row, rowIndex));
            tr.appendChild(td);
          }

          tbody.appendChild(tr);
        });
      }

      table.appendChild(tbody);
      return table;
    }

    renderFooter() {
      const footer = document.createElement('div');
      footer.className = 'lnv-datatable-footer';

      // Info
      const info = document.createElement('div');
      info.className = 'lnv-datatable-info';
      const start = (this.currentPage - 1) * this.config.pageSize + 1;
      const end = Math.min(this.currentPage * this.config.pageSize, this.filteredData.length);
      info.textContent = `Mostrando ${start}-${end} de ${this.filteredData.length} registros`;
      footer.appendChild(info);

      // Pagination
      const pagination = document.createElement('div');
      pagination.className = 'lnv-datatable-pagination';

      const totalPages = Math.ceil(this.filteredData.length / this.config.pageSize);

      // Previous
      const prevBtn = document.createElement('button');
      prevBtn.className = 'lnv-btn lnv-btn-sm lnv-btn-light';
      prevBtn.textContent = '‹';
      prevBtn.disabled = this.currentPage === 1;
      prevBtn.addEventListener('click', () => this.goToPage(this.currentPage - 1));
      pagination.appendChild(prevBtn);

      // Pages
      for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= this.currentPage - 1 && i <= this.currentPage + 1)) {
          const pageBtn = document.createElement('button');
          pageBtn.className = `lnv-btn lnv-btn-sm ${i === this.currentPage ? 'lnv-btn-primary' : 'lnv-btn-light'}`;
          pageBtn.textContent = i;
          pageBtn.addEventListener('click', () => this.goToPage(i));
          pagination.appendChild(pageBtn);
        } else if (i === this.currentPage - 2 || i === this.currentPage + 2) {
          const dots = document.createElement('span');
          dots.textContent = '...';
          dots.style.padding = '0 0.5rem';
          pagination.appendChild(dots);
        }
      }

      // Next
      const nextBtn = document.createElement('button');
      nextBtn.className = 'lnv-btn lnv-btn-sm lnv-btn-light';
      nextBtn.textContent = '›';
      nextBtn.disabled = this.currentPage === totalPages;
      nextBtn.addEventListener('click', () => this.goToPage(this.currentPage + 1));
      pagination.appendChild(nextBtn);

      footer.appendChild(pagination);
      return footer;
    }

  sort(column) {
      if (this.sortColumn === column) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortColumn = column;
        this.sortDirection = 'asc';
      }

      this.filteredData.sort((a, b) => {
        const aVal = a[column];
        const bVal = b[column];

        if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
        return 0;
      });

      this.render();

      if (this.config.onSort) {
        this.config.onSort(column, this.sortDirection);
      }
    }

    search(query) {
      if (!query) {
        this.filteredData = [...this.data];
      } else {
        const lowerQuery = query.toLowerCase();
        this.filteredData = this.data.filter(row => {
          return this.config.columns.some(col => {
            const value = row[col.key];
            return value && value.toString().toLowerCase().includes(lowerQuery);
          });
        });
      }

      this.currentPage = 1;
      this.render();

      if (this.config.onSearch) {
        this.config.onSearch(query, this.filteredData);
      }
    }

    goToPage(page) {
      this.currentPage = page;
      this.render();
    }

    selectRow(index, selected) {
      if (selected) {
        this.selectedRows.add(index);
      } else {
        this.selectedRows.delete(index);
      }

      if (this.config.onSelect) {
        this.config.onSelect(Array.from(this.selectedRows));
      }
    }

    selectAll(selected) {
      if (selected) {
        this.filteredData.forEach((_, index) => this.selectedRows.add(index));
      } else {
        this.selectedRows.clear();
      }
      this.render();
    }

    getData() {
      return this.filteredData;
    }

    getSelectedRows() {
      return Array.from(this.selectedRows).map(index => this.filteredData[index]);
    }
  }


  // ===========================
  // TRANSFER LIST
  // ===========================
  
  class TransferList {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('TransferList: Elemento no encontrado');
        return;
      }

      this.config = {
        data: [],
        leftTitle: 'Disponible',
        rightTitle: 'Seleccionado',
        searchable: true,
        onChange: null,
        ...options
      };

      this.leftItems = [...this.config.data];
      this.rightItems = [];
      this.leftSelected = new Set();
      this.rightSelected = new Set();

      this.init();
    }

    init() {
      this.render();
      console.log('✅ TransferList inicializado');
    }

    render() {
      const wrapper = document.createElement('div');
      wrapper.className = 'lnv-transfer';

      // Left list
      wrapper.appendChild(this.renderList('left', this.leftItems, this.leftSelected));

      // Controls
      wrapper.appendChild(this.renderControls());

      // Right list
      wrapper.appendChild(this.renderList('right', this.rightItems, this.rightSelected));

      this.container.innerHTML = '';
      this.container.appendChild(wrapper);
    }

    renderList(side, items, selected) {
      const list = document.createElement('div');
      list.className = 'lnv-transfer-list';

      // Header
      const header = document.createElement('div');
      header.className = 'lnv-transfer-header';
      
      const title = document.createElement('div');
      title.className = 'lnv-transfer-title';
      title.textContent = side === 'left' ? this.config.leftTitle : this.config.rightTitle;
      
      const count = document.createElement('span');
      count.className = 'lnv-transfer-count';
      count.textContent = `(${items.length})`;
      
      header.appendChild(title);
      header.appendChild(count);
      list.appendChild(header);

      // Search
      if (this.config.searchable) {
        const search = document.createElement('div');
        search.className = 'lnv-transfer-search';
        
        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Buscar...';
        input.addEventListener('input', (e) => this.filterList(side, e.target.value));
        
        search.appendChild(input);
        list.appendChild(search);
      }

      // Items
      const itemsContainer = document.createElement('div');
      itemsContainer.className = 'lnv-transfer-items';
      itemsContainer.dataset.side = side;

      items.forEach((item, index) => {
        const itemEl = document.createElement('div');
        itemEl.className = 'lnv-transfer-item';
        if (selected.has(index)) itemEl.classList.add('selected');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = selected.has(index);
        checkbox.addEventListener('change', (e) => {
          if (e.target.checked) {
            selected.add(index);
          } else {
            selected.delete(index);
          }
          this.render();
        });

        const label = document.createElement('span');
        label.textContent = typeof item === 'string' ? item : item.label || item.name;

        itemEl.appendChild(checkbox);
        itemEl.appendChild(label);
        itemsContainer.appendChild(itemEl);
      });

      list.appendChild(itemsContainer);
      return list;
    }

    renderControls() {
      const controls = document.createElement('div');
      controls.className = 'lnv-transfer-controls';

      // Move right
      const rightBtn = document.createElement('button');
      rightBtn.className = 'lnv-btn lnv-btn-primary';
      rightBtn.innerHTML = '→';
      rightBtn.addEventListener('click', () => this.moveRight());
      controls.appendChild(rightBtn);

      // Move left
      const leftBtn = document.createElement('button');
      leftBtn.className = 'lnv-btn lnv-btn-light';
      leftBtn.innerHTML = '←';
      leftBtn.addEventListener('click', () => this.moveLeft());
      controls.appendChild(leftBtn);

      return controls;
    }

    moveRight() {
      const selected = Array.from(this.leftSelected).sort((a, b) => b - a);
      selected.forEach(index => {
        this.rightItems.push(this.leftItems[index]);
        this.leftItems.splice(index, 1);
      });

      this.leftSelected.clear();
      this.render();

      if (this.config.onChange) {
        this.config.onChange(this.leftItems, this.rightItems);
      }
    }

    moveLeft() {
      const selected = Array.from(this.rightSelected).sort((a, b) => b - a);
      selected.forEach(index => {
        this.leftItems.push(this.rightItems[index]);
        this.rightItems.splice(index, 1);
      });

      this.rightSelected.clear();
      this.render();

      if (this.config.onChange) {
        this.config.onChange(this.leftItems, this.rightItems);
      }
    }

    filterList(side, query) {
      // Implementación simple - re-render con filtro
      this.render();
    }

    getSelected() {
      return this.rightItems;
    }
  }


  // ===========================
  // TREE VIEW
  // ===========================
  
  class TreeView {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('TreeView: Elemento no encontrado');
        return;
      }

      this.config = {
        data: [],
        onSelect: null,
        onToggle: null,
        ...options
      };

      this.selectedNode = null;

      this.init();
    }

    init() {
      this.render();
      console.log('✅ TreeView inicializado');
    }

    render() {
      const tree = document.createElement('ul');
      tree.className = 'lnv-tree';

      this.config.data.forEach(node => {
        tree.appendChild(this.renderNode(node));
      });

      this.container.innerHTML = '';
      this.container.appendChild(tree);
    }

    renderNode(node) {
      const li = document.createElement('li');
      li.className = 'lnv-tree-item';
      
      if (!node.children || node.children.length === 0) {
        li.classList.add('no-children');
      }

      // Content
      const content = document.createElement('div');
      content.className = 'lnv-tree-content';

      // Toggle
      const toggle = document.createElement('button');
      toggle.className = 'lnv-tree-toggle';
      toggle.textContent = '▶';
      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleNode(li);
      });

      // Icon
      const icon = document.createElement('span');
      icon.className = 'lnv-tree-icon';
      icon.textContent = node.icon || '📄';

      // Label
      const label = document.createElement('span');
      label.className = 'lnv-tree-label';
      label.textContent = node.label || node.name;

      content.appendChild(toggle);
      content.appendChild(icon);
      content.appendChild(label);

      // Badge
      if (node.badge) {
        const badge = document.createElement('span');
        badge.className = 'lnv-tree-badge';
        badge.textContent = node.badge;
        content.appendChild(badge);
      }

      content.addEventListener('click', () => this.selectNode(content, node));

      li.appendChild(content);

      // Children
      if (node.children && node.children.length > 0) {
        const children = document.createElement('ul');
        children.className = 'lnv-tree-children';

        node.children.forEach(child => {
          children.appendChild(this.renderNode(child));
        });

        li.appendChild(children);
      }

      return li;
    }

    toggleNode(nodeEl) {
      nodeEl.classList.toggle('expanded');

      if (this.config.onToggle) {
        this.config.onToggle(nodeEl.classList.contains('expanded'));
      }
    }

    selectNode(contentEl, node) {
      // Remove previous selection
      if (this.selectedNode) {
        this.selectedNode.classList.remove('selected');
      }

      // Add new selection
      contentEl.classList.add('selected');
      this.selectedNode = contentEl;

      if (this.config.onSelect) {
        this.config.onSelect(node);
      }
    }

    expandAll() {
      this.container.querySelectorAll('.lnv-tree-item').forEach(item => {
        item.classList.add('expanded');
      });
    }

    collapseAll() {
      this.container.querySelectorAll('.lnv-tree-item').forEach(item => {
        item.classList.remove('expanded');
      });
    }
  }


  // ===========================
  // IMAGE GALLERY
  // ===========================
  
  class ImageGallery {
    constructor(element, options = {}) {
      this.container = typeof element === 'string' 
        ? document.querySelector(element)
        : element;

      if (!this.container) {
        console.error('ImageGallery: Elemento no encontrado');
        return;
      }

      this.config = {
        images: [],
        columns: 4,
        lightbox: true,
        ...options
      };

      this.currentIndex = 0;
      this.lightbox = null;

      this.init();
    }

    init() {
      this.render();
      
      if (this.config.lightbox) {
        this.createLightbox();
      }

      console.log('✅ ImageGallery inicializado');
    }

    render() {
      const gallery = document.createElement('div');
      gallery.className = 'lnv-gallery';
      gallery.style.gridTemplateColumns = `repeat(${this.config.columns}, 1fr)`;

      this.config.images.forEach((image, index) => {
        const item = document.createElement('div');
        item.className = 'lnv-gallery-item';

        const img = document.createElement('img');
        img.src = image.thumb || image.src;
        img.alt = image.alt || image.title || '';
        img.loading = 'lazy';

        item.appendChild(img);

        // Overlay
        if (image.title) {
          const overlay = document.createElement('div');
          overlay.className = 'lnv-gallery-overlay';
          
          const title = document.createElement('h4');
          title.className = 'lnv-gallery-title';
          title.textContent = image.title;
          
          overlay.appendChild(title);
          item.appendChild(overlay);
        }

        // Click handler
        item.addEventListener('click', () => {
          if (this.config.lightbox) {
            this.openLightbox(index);
          }
        });

        gallery.appendChild(item);
      });

      this.container.innerHTML = '';
      this.container.appendChild(gallery);
    }

    createLightbox() {
      this.lightbox = document.createElement('div');
      this.lightbox.className = 'lnv-lightbox';

      this.lightbox.innerHTML = `
        <button class="lnv-lightbox-close">×</button>
        <button class="lnv-lightbox-prev">‹</button>
        <button class="lnv-lightbox-next">›</button>
        <div class="lnv-lightbox-content">
          <img class="lnv-lightbox-image" src="" alt="">
        </div>
        <div class="lnv-lightbox-caption"></div>
      `;

      document.body.appendChild(this.lightbox);

      // Events
      this.lightbox.querySelector('.lnv-lightbox-close').addEventListener('click', () => this.closeLightbox());
      this.lightbox.querySelector('.lnv-lightbox-prev').addEventListener('click', () => this.prevImage());
      this.lightbox.querySelector('.lnv-lightbox-next').addEventListener('click', () => this.nextImage());

      // Keyboard
      document.addEventListener('keydown', (e) => {
        if (!this.lightbox.classList.contains('active')) return;

        if (e.key === 'Escape') this.closeLightbox();
        if (e.key === 'ArrowLeft') this.prevImage();
        if (e.key === 'ArrowRight') this.nextImage();
      });

      // Click outside
      this.lightbox.addEventListener('click', (e) => {
        if (e.target === this.lightbox) {
          this.closeLightbox();
        }
      });
    }

    openLightbox(index) {
      this.currentIndex = index;
      this.updateLightbox();
      this.lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    }

    closeLightbox() {
      this.lightbox.classList.remove('active');
      document.body.style.overflow = '';
    }

    updateLightbox() {
      const image = this.config.images[this.currentIndex];
      const img = this.lightbox.querySelector('.lnv-lightbox-image');
      const caption = this.lightbox.querySelector('.lnv-lightbox-caption');

      img.src = image.src;
      img.alt = image.alt || image.title || '';

      if (image.title) {
        caption.textContent = image.title;
        caption.style.display = 'block';
      } else {
        caption.style.display = 'none';
      }

      // Update buttons
      const prevBtn = this.lightbox.querySelector('.lnv-lightbox-prev');
      const nextBtn = this.lightbox.querySelector('.lnv-lightbox-next');

      prevBtn.disabled = this.currentIndex === 0;
      nextBtn.disabled = this.currentIndex === this.config.images.length - 1;
    }

    prevImage() {
      if (this.currentIndex > 0) {
        this.currentIndex--;
        this.updateLightbox();
      }
    }

    nextImage() {
      if (this.currentIndex < this.config.images.length - 1) {
        this.currentIndex++;
        this.updateLightbox();
      }
    }
  }


  // ===========================
  // AUTO-INICIALIZACIÓN
  // ===========================
  
  function init() {
    console.log('✅ LNV Advanced Components 2 listos para usar');
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
    DataTable,
    TransferList,
    TreeView,
    ImageGallery,
    init
  };
})();

// Exportar globalmente
window.LNVAdvancedComponents = LNVAdvancedComponents;