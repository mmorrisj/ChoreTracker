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
            const childId = this.dataset.childId || '';
            const childName = this.dataset.childName || '';
            const isUnassigned = !childId || childId === '';

            // Update the modal
            const modal = document.getElementById('completeChoreModal');
            if (modal) {
                const choreNameElement = modal.querySelector('#completeChoreNamePlaceholder');
                const childNameElement = modal.querySelector('#completeChildNamePlaceholder');
                const childContainer = modal.querySelector('#completeForChild');
                const childSelectContainer = modal.querySelector('#completeChildSelectContainer');
                const timeSpentInput = modal.querySelector('#completeChoreTime');
                const dateInput = modal.querySelector('#completeChoreDate');
                const form = modal.querySelector('form');
                const choreIdInput = form.querySelector('input[name="chore_id"]');
                const childIdInput = document.getElementById('completeChildIdHidden');
                const childSelect = document.getElementById('completeChildSelect');

                if (choreNameElement) choreNameElement.textContent = choreName;

                // Handle assigned vs unassigned chores differently
                if (isUnassigned) {
                    // For unassigned chores, show the dropdown to select a child
                    if (childContainer) childContainer.style.display = 'none';
                    if (childSelectContainer) childSelectContainer.style.display = 'block';
                    if (childIdInput) childIdInput.value = '';

                    // Pre-select the first child in the dropdown
                    if (childSelect && childSelect.options.length > 0) {
                        childSelect.selectedIndex = 0;
                        // Update the hidden input when dropdown changes
                        childSelect.addEventListener('change', function() {
                            childIdInput.value = this.value;
                        });
                        // Set initial value
                        childIdInput.value = childSelect.value;
                    }
                } else {
                    // For assigned chores, show the child's name
                    if (childContainer) childContainer.style.display = 'inline';
                    if (childNameElement) childNameElement.textContent = childName;
                    if (childSelectContainer) childSelectContainer.style.display = 'none';
                    if (childIdInput) childIdInput.value = childId;
                }

                if (timeSpentInput) timeSpentInput.value = choreTime;
                if (choreIdInput) choreIdInput.value = choreId;

                // Ensure date is set to today
                if (dateInput) {
                    const today = new Date();
                    const year = today.getFullYear();
                    const month = String(today.getMonth() + 1).padStart(2, '0');
                    const day = String(today.getDate()).padStart(2, '0');
                    dateInput.value = `${year}-${month}-${day}`;
                }

                if (form) form.action = `/chores/${choreId}/complete`;

                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });

    // Child complete buttons (for children completing their own chores)
    const childCompleteButtons = document.querySelectorAll('.btn-child-complete');
    childCompleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const choreId = this.dataset.choreId;
            const choreName = this.dataset.choreName;
            const choreTime = this.dataset.choreTime;

            // Update the modal
            const modal = document.getElementById('childCompleteModal');
            if (modal) {
                const choreNameElement = modal.querySelector('#childChoreNamePlaceholder');
                const timeSpentInput = modal.querySelector('#childTimeSpent');
                const choreIdInput = modal.querySelector('#childChoreId');
                const form = modal.querySelector('#childCompleteForm');

                if (choreNameElement) choreNameElement.textContent = choreName;
                if (timeSpentInput) timeSpentInput.value = choreTime;
                if (choreIdInput) choreIdInput.value = choreId;

                // Update the form action URL
                if (form) {
                    const baseUrl = window.location.origin;
                    form.action = `${baseUrl}/chores/${choreId}/complete`;
                }

                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
});