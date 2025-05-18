// calendar.js - Handles calendar functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the calendar if element exists
    const calendarEl = document.getElementById('familyCalendar');
    if (!calendarEl) return;
    
    // Get current filter values
    const childFilter = document.getElementById('childFilter');
    let selectedChildId = childFilter ? childFilter.value : 'all';
    
    // Initialize FullCalendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },
        height: 'auto',
        events: function(info, successCallback, failureCallback) {
            // Fetch events from the server
            fetch(`/api/calendar-events?start=${info.startStr}&end=${info.endStr}`)
                .then(response => response.json())
                .then(data => {
                    // Filter events by selected child if necessary
                    if (selectedChildId !== 'all') {
                        data = data.filter(event => 
                            event.extendedProps && event.extendedProps.user_id === selectedChildId
                        );
                    }
                    successCallback(data);
                })
                .catch(error => {
                    console.error('Error fetching calendar events:', error);
                    failureCallback(error);
                });
        },
        eventClick: function(info) {
            // Handle event clicks based on event type
            const eventType = info.event.extendedProps.type;
            
            if (eventType === 'completion') {
                showCompletionDetails(info.event);
            } else if (eventType === 'behavior') {
                showBehaviorDetails(info.event);
            }
        }
    });
    
    // Render the calendar
    calendar.render();
    
    // Handle filter changes
    if (childFilter) {
        childFilter.addEventListener('change', function() {
            selectedChildId = this.value;
            calendar.refetchEvents();
        });
    }
    
    // Function to show completion details
    function showCompletionDetails(event) {
        const modal = document.getElementById('eventDetailsModal');
        if (!modal) return;
        
        const modalTitle = modal.querySelector('.modal-title');
        const modalBody = modal.querySelector('.modal-body');
        
        // Extract data from the event
        const title = event.title;
        const date = new Date(event.start).toLocaleDateString();
        const timeSpent = event.extendedProps.time_spent;
        const earned = event.extendedProps.amount_earned.toFixed(2);
        
        // Update modal content
        modalTitle.textContent = 'Chore Completion';
        modalBody.innerHTML = `
            <p><strong>Task:</strong> ${title}</p>
            <p><strong>Date:</strong> ${date}</p>
            <p><strong>Time Spent:</strong> ${timeSpent} minutes</p>
            <p><strong>Earned:</strong> $${earned}</p>
        `;
        
        // Show the modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    // Function to show behavior details
    function showBehaviorDetails(event) {
        const modal = document.getElementById('eventDetailsModal');
        if (!modal) return;
        
        const modalTitle = modal.querySelector('.modal-title');
        const modalBody = modal.querySelector('.modal-body');
        
        // Extract data from the event
        const title = event.title;
        const date = new Date(event.start).toLocaleDateString();
        const description = event.extendedProps.description;
        const amount = event.extendedProps.amount.toFixed(2);
        const isPositive = event.extendedProps.is_positive;
        const type = isPositive ? 'Award' : 'Deduction';
        
        // Update modal content
        modalTitle.textContent = `Behavior ${type}`;
        modalBody.innerHTML = `
            <p><strong>For:</strong> ${title.split(':')[0]}</p>
            <p><strong>Date:</strong> ${date}</p>
            <p><strong>Description:</strong> ${description}</p>
            <p><strong>Amount:</strong> $${amount}</p>
            <p><strong>Type:</strong> <span class="${isPositive ? 'text-success' : 'text-danger'}">${type}</span></p>
        `;
        
        // Show the modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    // Add functionality for adding events from calendar
    const addEventButtons = document.querySelectorAll('.calendar-add-event');
    addEventButtons.forEach(button => {
        button.addEventListener('click', function() {
            const eventType = this.dataset.eventType;
            const modal = document.getElementById(
                eventType === 'chore' ? 'addChoreCompletionModal' : 'addBehaviorModal'
            );
            
            if (modal) {
                // Set the current date as default
                const dateInput = modal.querySelector('input[type="date"]');
                if (dateInput) {
                    const today = new Date().toISOString().split('T')[0];
                    dateInput.value = today;
                }
                
                // Show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
});
