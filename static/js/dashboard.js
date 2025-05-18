// dashboard.js - Handles dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize earnings charts for children if present
    const childChartElements = document.querySelectorAll('.child-earnings-chart');
    if (childChartElements.length > 0) {
        childChartElements.forEach(element => {
            const childId = element.dataset.childId;
            const ctx = element.getContext('2d');
            
            // Get earnings data for this child (would come from AJAX in a full app)
            // For now, we'll use the data embedded in the page
            const earningsElement = document.querySelector(`.child-earnings[data-child-id="${childId}"]`);
            const earnedAmount = parseFloat(earningsElement.dataset.earned || 0);
            
            // Create chart
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Earned', 'Potential'],
                    datasets: [{
                        data: [earnedAmount, Math.max(100 - earnedAmount, 0)],
                        backgroundColor: [
                            '#28a745', // Green for earned
                            '#e9ecef'  // Light gray for potential
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `$${context.raw.toFixed(2)}`;
                                }
                            }
                        }
                    }
                }
            });
        });
    }
    
    // Initialize goal progress bars
    const goalProgressBars = document.querySelectorAll('.goal-progress-bar');
    goalProgressBars.forEach(bar => {
        const progress = parseFloat(bar.dataset.progress || 0);
        bar.style.width = `${Math.min(progress, 100)}%`;
        
        // Color coding based on progress
        if (progress >= 75) {
            bar.classList.add('bg-success'); // Green for 75%+
        } else if (progress >= 50) {
            bar.classList.add('bg-info');    // Blue for 50-74%
        } else if (progress >= 25) {
            bar.classList.add('bg-warning'); // Yellow for 25-49%
        } else {
            bar.classList.add('bg-danger');  // Red for <25%
        }
    });
    
    // Quick action buttons for parents
    const completeChoreButtons = document.querySelectorAll('.btn-complete-chore');
    completeChoreButtons.forEach(button => {
        button.addEventListener('click', function() {
            const choreId = this.dataset.choreId;
            const choreName = this.dataset.choreName;
            const choreTime = this.dataset.choreTime;
            const childId = this.dataset.childId;
            const childName = this.dataset.childName;
            
            // Update the modal
            const modal = document.getElementById('completeChoreModal');
            if (modal) {
                const choreNameElement = modal.querySelector('#choreNamePlaceholder');
                const childNameElement = modal.querySelector('#childNamePlaceholder');
                const timeSpentInput = modal.querySelector('#timeSpent');
                const choreIdInput = modal.querySelector('#choreId');
                const childIdInput = modal.querySelector('#childId');
                
                if (choreNameElement) choreNameElement.textContent = choreName;
                if (childNameElement) childNameElement.textContent = childName;
                if (timeSpentInput) timeSpentInput.value = choreTime;
                if (choreIdInput) choreIdInput.value = choreId;
                if (childIdInput) childIdInput.value = childId;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
    
    // Behavior award/deduction buttons
    const behaviorButtons = document.querySelectorAll('.btn-behavior');
    behaviorButtons.forEach(button => {
        button.addEventListener('click', function() {
            const behaviorType = this.dataset.behaviorType;
            const childId = this.dataset.childId;
            const childName = this.dataset.childName;
            
            // Update the modal
            const modal = document.getElementById('behaviorModal');
            if (modal) {
                const behaviorTitleElement = modal.querySelector('#behaviorTypeTitle');
                const childNameElement = modal.querySelector('#behaviorChildName');
                const behaviorTypeInput = modal.querySelector('#behaviorType');
                const childIdInput = modal.querySelector('#behaviorChildId');
                
                if (behaviorTitleElement) {
                    behaviorTitleElement.textContent = behaviorType === 'positive' ? 'Award' : 'Deduction';
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
    
    // Quick complete buttons for children
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
                
                if (choreNameElement) choreNameElement.textContent = choreName;
                if (timeSpentInput) timeSpentInput.value = choreTime;
                if (choreIdInput) choreIdInput.value = choreId;
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
});
