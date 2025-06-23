// goals.js - Handles goals functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize goal progress charts
    const goalCharts = document.querySelectorAll('.goal-progress-chart');
    goalCharts.forEach(chartElement => {
        const goalId = chartElement.dataset.goalId;
        const goalName = chartElement.dataset.goalName;
        const currentAmount = parseFloat(chartElement.dataset.currentAmount);
        const goalAmount = parseFloat(chartElement.dataset.goalAmount);
        const progress = (currentAmount / goalAmount) * 100;
        
        const ctx = chartElement.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Saved', 'Remaining'],
                datasets: [{
                    data: [currentAmount, Math.max(goalAmount - currentAmount, 0)],
                    backgroundColor: [
                        progress >= 100 ? '#28a745' : '#17a2b8', // Green if complete, blue if in progress
                        '#e9ecef' // Light gray for remaining
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: $${value.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
        
        // Add center text with current/total
        const centerText = document.createElement('div');
        centerText.className = 'goal-chart-label';
        centerText.innerHTML = `$${currentAmount.toFixed(2)}<br><small>of $${goalAmount.toFixed(2)}</small>`;
        
        const parent = chartElement.parentNode;
        parent.style.position = 'relative';
        parent.appendChild(centerText);
    });
    
    // Handle edit goal modal population
    const editGoalButtons = document.querySelectorAll('.btn-edit-goal');
    editGoalButtons.forEach(button => {
        button.addEventListener('click', function() {
            const goalId = this.dataset.goalId;
            const goalName = this.dataset.goalName;
            const goalDescription = this.dataset.goalDescription;
            const goalAmount = this.dataset.goalAmount;
            const goalCurrentAmount = this.dataset.goalCurrentAmount;
            
            // Update the modal
            const modal = document.getElementById('editGoalModal');
            if (modal) {
                const form = modal.querySelector('#editGoalForm');
                if (form) {
                    // Update form action with the actual goal ID
                    const baseUrl = form.action.split('/goals/')[0];
                    form.action = `${baseUrl}/goals/${goalId}/edit`;
                }
                
                const nameInput = modal.querySelector('#editGoalName');
                const descriptionInput = modal.querySelector('#editGoalDescription');
                const amountInput = modal.querySelector('#editGoalAmount');
                const currentAmountInput = modal.querySelector('#editGoalCurrentAmount');
                
                if (nameInput) nameInput.value = goalName;
                if (descriptionInput) descriptionInput.value = goalDescription;
                if (amountInput) amountInput.value = goalAmount;
                if (currentAmountInput) currentAmountInput.value = goalCurrentAmount;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Handle delete goal confirmation
    const deleteGoalButtons = document.querySelectorAll('.btn-delete-goal');
    deleteGoalButtons.forEach(button => {
        button.addEventListener('click', function() {
            const goalId = this.dataset.goalId;
            const goalName = this.dataset.goalName;
            
            // Update the modal
            const modal = document.getElementById('deleteGoalModal');
            if (modal) {
                const goalNameElement = modal.querySelector('#deleteGoalNamePlaceholder');
                const form = modal.querySelector('#deleteGoalForm');
                
                if (goalNameElement) goalNameElement.textContent = goalName;
                if (form) {
                    // Update form action with the actual goal ID
                    const baseUrl = form.action.split('/goals/')[0];
                    form.action = `${baseUrl}/goals/${goalId}/delete`;
                }
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Handle Apply Reward buttons
    const applyRewardButtons = document.querySelectorAll('.btn-apply-reward');
    applyRewardButtons.forEach(button => {
        button.addEventListener('click', function() {
            const goalId = this.dataset.goalId;
            const goalName = this.dataset.goalName;
            const goalAmount = this.dataset.goalAmount;
            
            // Update the modal
            const modal = document.getElementById('applyRewardModal');
            if (modal) {
                const goalNameElement = modal.querySelector('#applyRewardGoalNamePlaceholder');
                const amountElement = modal.querySelector('#applyRewardAmountPlaceholder');
                const form = modal.querySelector('#applyRewardForm');
                
                if (goalNameElement) goalNameElement.textContent = goalName;
                if (amountElement) amountElement.textContent = `$${parseFloat(goalAmount).toFixed(2)}`;
                if (form) {
                    // Update form action with the actual goal ID
                    const baseUrl = form.action.split('/goals/')[0];
                    form.action = `${baseUrl}/goals/${goalId}/apply-reward`;
                }
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Handle contribute to goal
    const contributeButtons = document.querySelectorAll('.btn-contribute');
    contributeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const goalId = this.dataset.goalId;
            const goalName = this.dataset.goalName;
            const remainingAmount = parseFloat(this.dataset.remainingAmount);
            
            // Update the modal
            const modal = document.getElementById('contributeGoalModal');
            if (modal) {
                const goalNameElement = modal.querySelector('#contributeGoalNamePlaceholder');
                const form = modal.querySelector('#contributeGoalForm');
                const amountInput = modal.querySelector('#contributeAmount');
                
                if (goalNameElement) goalNameElement.textContent = goalName;
                if (form) {
                    // Update form action with the actual goal ID
                    const baseUrl = form.action.split('/goals/')[0];
                    form.action = `${baseUrl}/goals/${goalId}/contribute`;
                }
                if (amountInput) {
                    amountInput.setAttribute('max', remainingAmount);
                    amountInput.value = Math.min(5, remainingAmount).toFixed(2);
                }
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Handle reset goal buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-reset-goal')) {
            const button = e.target.closest('.btn-reset-goal');
            const goalId = button.dataset.goalId;
            const goalName = button.dataset.goalName;
            
            console.log('Reset button clicked for goal:', goalId, goalName);
            
            // Wait for DOM to be ready, then find modal
            setTimeout(() => {
                const modal = document.getElementById('resetGoalModal');
                console.log('Looking for modal:', modal);
                
                if (modal) {
                    const goalNameElement = modal.querySelector('#resetGoalNamePlaceholder');
                    const form = modal.querySelector('#resetGoalForm');
                    
                    if (goalNameElement) goalNameElement.textContent = goalName;
                    if (form) {
                        // Set the correct action URL
                        form.action = `/goals/${goalId}/reset`;
                        // Ensure the form has the required method
                        form.method = 'POST';
                        console.log('Form action set to:', form.action);
                    }
                    
                    // Show the modal
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                } else {
                    console.error('Reset modal not found in DOM');
                    console.log('Available modals:', document.querySelectorAll('.modal'));
                    
                    // Fallback: direct confirmation
                    if (confirm(`Are you sure you want to reset the funds for "${goalName}"? This will set the current amount back to $0.00.`)) {
                        // Create a temporary form and submit it
                        const tempForm = document.createElement('form');
                        tempForm.method = 'POST';
                        tempForm.action = `/goals/${goalId}/reset`;
                        document.body.appendChild(tempForm);
                        tempForm.submit();
                    }
                }
            }, 100);
        }
    });
    
    // Toggle between individual and family goals in add goal modal
    const goalTypeRadios = document.querySelectorAll('input[name="goal_type"]');
    goalTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const userIdField = document.getElementById('goalUserIdField');
            if (userIdField) {
                if (this.value === 'individual') {
                    userIdField.classList.remove('d-none');
                } else {
                    userIdField.classList.add('d-none');
                }
            }
        });
    });
});
