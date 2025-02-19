document.addEventListener('DOMContentLoaded', () => {
    const childrenList = document.getElementById('children-list');
    const openChoresList = document.getElementById('open-chores-list');

    // Sample data
    const children = [
        { name: 'Alice', chores: [{ id: 1, text: 'Clean room', completed: false }] },
        { name: 'Bob', chores: [{ id: 2, text: 'Take out trash', completed: false }] }
    ];

    const openChores = [
        { id: 3, text: 'Wash dishes', completed: false },
        { id: 4, text: 'Vacuum living room', completed: false }
    ];

    // Render children's chores
    children.forEach(child => {
        const childDiv = document.createElement('div');
        const childName = document.createElement('h3');
        childName.innerText = child.name;
        childDiv.appendChild(childName);

        child.chores.forEach(chore => {
            const choreDiv = document.createElement('div');
            choreDiv.className = 'chore';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = chore.completed;
            const label = document.createElement('label');
            label.innerText = chore.text;
            const submitButton = document.createElement('button');
            submitButton.innerText = 'Submit';
            if (chore.completed) {
                checkbox.disabled = true;
                submitButton.style.display = 'none';
                label.innerHTML += ' <span class="green-check">&#10003;</span>';
            }
            submitButton.addEventListener('click', () => {
                chore.completed = true;
                checkbox.disabled = true;
                submitButton.style.display = 'none';
                label.innerHTML += ' <span class="green-check">&#10003;</span>';
                // Send to database
                sendChoreCompletion(child.name, chore.id);
            });
            choreDiv.appendChild(checkbox);
            choreDiv.appendChild(label);
            choreDiv.appendChild(submitButton);
            childDiv.appendChild(choreDiv);
        });

        childrenList.appendChild(childDiv);
    });

    // Render open chores
    openChores.forEach(chore => {
        const choreDiv = document.createElement('div');
        choreDiv.className = 'chore';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = chore.completed;
        const label = document.createElement('label');
        label.innerText = chore.text;
        const select = document.createElement('select');
        children.forEach(child => {
            const option = document.createElement('option');
            option.value = child.name;
            option.innerText = child.name;
            select.appendChild(option);
        });
        const submitButton = document.createElement('button');
        submitButton.innerText = 'Submit';
        if (chore.completed) {
            checkbox.disabled = true;
            select.disabled = true;
            submitButton.style.display = 'none';
            label.innerHTML += ' <span class="green-check">&#10003;</span>';
        }
        submitButton.addEventListener('click', () => {
            const selectedChild = select.value;
            chore.completed = true;
            checkbox.disabled = true;
            select.disabled = true;
            submitButton.style.display = 'none';
            label.innerHTML += ` <span class="green-check">&#10003;</span> (${selectedChild})`;
            // Send to database
            sendChoreCompletion(selectedChild, chore.id);
        });
        choreDiv.appendChild(checkbox);
        choreDiv.appendChild(label);
        choreDiv.appendChild(select);
        choreDiv.appendChild(submitButton);
        openChoresList.appendChild(choreDiv);
    });

    function sendChoreCompletion(childName, choreId) {
        fetch('/complete_chore', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                child_id: childName,
                chore_id: choreId
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
});