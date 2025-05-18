// behavior.js - Handles behavior management functionality

document.addEventListener('DOMContentLoaded', function() {
    // Set color coding for behavior records
    const behaviorTypeIndicators = document.querySelectorAll('.behavior-type-indicator');
    behaviorTypeIndicators.forEach(indicator => {
        const isPositive = indicator.dataset.isPositive === 'true';
        indicator.classList.add(isPositive ? 'bg-success' : 'bg-danger');
        indicator.textContent = isPositive ? '+' : '-';
    });
    
    // Handle edit behavior modal population
    const editBehaviorButtons = document.querySelectorAll('.btn-edit-behavior');
    editBehaviorButtons.forEach(button => {
        button.addEventListener('click', function() {
            const recordId = this.dataset.recordId;
            const description = this.dataset.description;
            const amount = this.dataset.amount;
            const isPositive = this.dataset.isPositive === 'true';
            const date = this.dataset.date;
            
            // Update the modal
            const modal = document.getElementById('editBehaviorModal');
            if (modal) {
                const form = modal.querySelector('form');
                form.action = `/behavior/${recordId}/edit`;
                
                const descriptionInput = modal.querySelector('#editBehaviorDescription');
                const amountInput = modal.querySelector('#editBehaviorAmount');
                const dateInput = modal.querySelector('#editBehaviorDate');
                const positiveRadio = modal.querySelector('#editBehaviorPositive');
                const negativeRadio = modal.querySelector('#editBehaviorNegative');
                
                if (descriptionInput) descriptionInput.value = description;
                if (amountInput) amountInput.value = amount;
                if (dateInput) dateInput.value = date;
                if (positiveRadio && negativeRadio) {
                    positiveRadio.checked = isPositive;
                    negativeRadio.checked = !isPositive;
                }
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Handle delete behavior confirmation
    const deleteBehaviorButtons = document.querySelectorAll('.btn-delete-behavior');
    deleteBehaviorButtons.forEach(button => {
        button.addEventListener('click', function() {
            const recordId = this.dataset.recordId;
            const description = this.dataset.description;
            
            // Update the modal
            const modal = document.getElementById('deleteBehaviorModal');
            if (modal) {
                const descriptionElement = modal.querySelector('#deleteBehaviorDescriptionPlaceholder');
                const form = modal.querySelector('form');
                
                if (descriptionElement) descriptionElement.textContent = description;
                if (form) form.action = `/behavior/${recordId}/delete`;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Add quick award/deduction buttons
    const quickBehaviorButtons = document.querySelectorAll('.btn-quick-behavior');
    quickBehaviorButtons.forEach(button => {
        button.addEventListener('click', function() {
            const behaviorType = this.dataset.behaviorType;
            const childId = this.dataset.childId;
            const childName = this.dataset.childName;
            
            // Update the modal
            const modal = document.getElementById('quickBehaviorModal');
            if (modal) {
                const titleElement = modal.querySelector('#quickBehaviorTitle');
                const childNameElement = modal.querySelector('#quickBehaviorChildName');
                const behaviorTypeInput = modal.querySelector('#quickBehaviorType');
                const childIdInput = modal.querySelector('#quickBehaviorChildId');
                
                if (titleElement) {
                    titleElement.textContent = behaviorType === 'positive' ? 'Quick Award' : 'Quick Deduction';
                }
                
                if (childNameElement) childNameElement.textContent = childName;
                if (behaviorTypeInput) behaviorTypeInput.value = behaviorType;
                if (childIdInput) childIdInput.value = childId;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Filter behavior records
    const behaviorTypeFilter = document.getElementById('behaviorTypeFilter');
    const behaviorChildFilter = document.getElementById('behaviorChildFilter');
    
    function applyFilters() {
        const selectedType = behaviorTypeFilter ? behaviorTypeFilter.value : 'all';
        const selectedChild = behaviorChildFilter ? behaviorChildFilter.value : 'all';
        
        const behaviorRows = document.querySelectorAll('.behavior-row');
        
        behaviorRows.forEach(row => {
            const rowType = row.dataset.isPositive === 'true' ? 'positive' : 'negative';
            const rowChild = row.dataset.childId;
            
            const typeMatch = selectedType === 'all' || rowType === selectedType;
            const childMatch = selectedChild === 'all' || rowChild === selectedChild;
            
            if (typeMatch && childMatch) {
                row.classList.remove('d-none');
            } else {
                row.classList.add('d-none');
            }
        });
    }
    
    if (behaviorTypeFilter) {
        behaviorTypeFilter.addEventListener('change', applyFilters);
    }
    
    if (behaviorChildFilter) {
        behaviorChildFilter.addEventListener('change', applyFilters);
    }
    
    // Date range picker for behavior records if available
    const dateRangeStart = document.getElementById('behaviorDateStart');
    const dateRangeEnd = document.getElementById('behaviorDateEnd');
    
    if (dateRangeStart && dateRangeEnd) {
        // Set initial values
        const today = new Date();
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(today.getDate() - 30);
        
        dateRangeStart.value = thirtyDaysAgo.toISOString().split('T')[0];
        dateRangeEnd.value = today.toISOString().split('T')[0];
        
        // Add event listeners
        [dateRangeStart, dateRangeEnd].forEach(input => {
            input.addEventListener('change', function() {
                const startDate = new Date(dateRangeStart.value);
                const endDate = new Date(dateRangeEnd.value);
                
                const behaviorRows = document.querySelectorAll('.behavior-row');
                
                behaviorRows.forEach(row => {
                    const rowDate = new Date(row.dataset.date);
                    
                    if (rowDate >= startDate && rowDate <= endDate) {
                        // This still respects other filters
                        if (!row.classList.contains('d-none')) {
                            row.classList.remove('filter-date-hidden');
                        }
                    } else {
                        row.classList.add('filter-date-hidden');
                    }
                });
            });
        });
    }
});
