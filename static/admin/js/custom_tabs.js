// static/admin/js/custom_tabs.js

document.addEventListener('DOMContentLoaded', function() {
    // Create tab navigation
    const fieldsets = document.querySelectorAll('fieldset');
    const tabNav = document.createElement('div');
    tabNav.className = 'tab-navigation';
    const tabList = document.createElement('ul');
    
    // Add tabs for each fieldset
    fieldsets.forEach((fieldset, index) => {
        const legend = fieldset.querySelector('h2').textContent;
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = '#';
        a.textContent = legend;
        a.dataset.tab = `tab-${index}`;
        
        if (index === 0) {
            a.className = 'active';
            fieldset.className = 'tab-content active';
        } else {
            fieldset.className = 'tab-content';
        }
        
        a.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab-navigation a').forEach(tab => {
                tab.className = '';
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.className = 'tab-content';
            });
            
            // Add active class to clicked tab and corresponding content
            this.className = 'active';
            fieldset.className = 'tab-content active';
        });
        
        li.appendChild(a);
        tabList.appendChild(li);
    });
    
    tabNav.appendChild(tabList);
    
    // Insert tab navigation before the first fieldset
    if (fieldsets.length > 0) {
        fieldsets[0].parentNode.insertBefore(tabNav, fieldsets[0]);
    }
});