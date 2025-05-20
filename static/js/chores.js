// chores.js - Handles chores functionality

document.addEventListener('DOMContentLoaded', function() {
    // Handle edit chore modal population
    const editChoreButtons = document.querySelectorAll('.btn-edit-chore');
    editChoreButtons.forEach(button => {
        button.addEventListener('click', function() {
            const choreId = this.dataset.choreId;
            const choreName = this.dataset.choreName;
            const choreDescription = this.dataset.choreDescription;
            const choreTime = this.dataset.choreTime;
            const choreAssignedTo = this.dataset.choreAssignedTo;
            const choreFrequency = this.dataset.choreFrequency;
            const choreStatus = this.dataset.choreStatus;
            
            // Update the modal
            const modal = document.getElementById('editChoreModal');
            if (modal) {
                const form = modal.querySelector('form');
                form.action = `/chores/${choreId}/edit`;
                form.id = 'editChoreForm';
                
                const nameInput = modal.querySelector('#editChoreName');
                const descriptionInput = modal.querySelector('#editChoreDescription');
                const timeInput = modal.querySelector('#editChoreTime');
                const assignedToSelect = modal.querySelector('#editChoreAssignedTo');
                const frequencySelect = modal.querySelector('#editChoreFrequency');
                const statusSelect = modal.querySelector('#editChoreStatus');
                
                if (nameInput) nameInput.value = choreName;
                if (descriptionInput) descriptionInput.value = choreDescription;
                if (timeInput) timeInput.value = choreTime;
                if (assignedToSelect) assignedToSelect.value = choreAssignedTo;
                if (frequencySelect) frequencySelect.value = choreFrequency;
                if (statusSelect) statusSelect.value = choreStatus;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Handle delete chore confirmation
    const deleteChoreButtons = document.querySelectorAll('.btn-delete-chore');
    deleteChoreButtons.forEach(button => {
        button.addEventListener('click', function() {
            const choreId = this.dataset.choreId;
            const choreName = this.dataset.choreName;
            
            // Update the modal
            const modal = document.getElementById('deleteChoreModal');
            if (modal) {
                const choreNameElement = modal.querySelector('#deleteChoreNamePlaceholder');
                const form = modal.querySelector('form');
                
                if (choreNameElement) choreNameElement.textContent = choreName;
                if (form) form.action = `/chores/${choreId}/delete`;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Filter chores by status
    const choreStatusFilter = document.getElementById('choreStatusFilter');
    if (choreStatusFilter) {
        choreStatusFilter.addEventListener('change', function() {
            const selectedStatus = this.value;
            const choreRows = document.querySelectorAll('.chore-row');
            
            choreRows.forEach(row => {
                const rowStatus = row.dataset.status;
                if (selectedStatus === 'all' || rowStatus === selectedStatus) {
                    row.classList.remove('d-none');
                } else {
                    row.classList.add('d-none');
                }
            });
        });
    }
    
    // Filter chores by assigned child
    const choreChildFilter = document.getElementById('choreChildFilter');
    if (choreChildFilter) {
        choreChildFilter.addEventListener('change', function() {
            const selectedChild = this.value;
            const choreRows = document.querySelectorAll('.chore-row');
            
            choreRows.forEach(row => {
                const assignedTo = row.dataset.assignedTo;
                if (selectedChild === 'all' || assignedTo === selectedChild) {
                    row.classList.remove('d-none');
                } else {
                    row.classList.add('d-none');
                }
            });
        });
    }
    
    // Quick complete buttons
    const quickCompleteButtons = document.querySelectorAll('.btn-quick-complete');
    quickCompleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const choreId = this.dataset.choreId;
            const choreName = this.dataset.choreName;
            const choreTime = this.dataset.choreTime;
            const childId = this.dataset.childId;
            const childName = this.dataset.childName;
            
            // Update the modal
            const modal = document.getElementById('completeChoreModal');
            if (modal) {
                const choreNameElement = modal.querySelector('#completeChoreNamePlaceholder');
                const childNameElement = modal.querySelector('#completeChildNamePlaceholder');
                const timeSpentInput = modal.querySelector('#completeChoreTime');
                const form = modal.querySelector('form');
                const choreIdInput = form.querySelector('input[name="chore_id"]');
                const childIdInput = form.querySelector('input[name="child_id"]');
                
                if (choreNameElement) choreNameElement.textContent = choreName;
                if (childNameElement) childNameElement.textContent = childName;
                if (timeSpentInput) timeSpentInput.value = choreTime;
                if (choreIdInput) choreIdInput.value = choreId;
                if (childIdInput) childIdInput.value = childId;
                if (form) form.action = `/chores/${choreId}/complete`;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
});
