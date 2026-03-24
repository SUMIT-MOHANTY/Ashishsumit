document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    initTodoApp();
});

function initTodoApp() {
    // Add event listener for form submission
    const todoForm = document.getElementById('todo-form');
    if (todoForm) {
        todoForm.addEventListener('submit', handleFormSubmit);
    }

    // Add event listeners for todo actions
    setupTodoActions();
}

async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Adding...';

    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error('Server error: ' + response.status);
        }

        // Assuming the server returns the new todo HTML or JSON
        const result = await response.json();

        // Add the new todo to the list without page reload
        addTodoToList(result.todo);

        // Clear the form
        form.reset();

        // Show success message
        showNotification('Todo added successfully!', 'success');
    } catch (error) {
        console.error('Error adding todo:', error);
        showNotification('Failed to add todo. Please try again.', 'error');
    } finally {
        // Restore button state
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
}

function setupTodoActions() {
    // Delegate events for todo actions (complete, delete)
    const todoList = document.getElementById('todo-list');
    if (todoList) {
        todoList.addEventListener('click', async (event) => {
            // Handle status toggle
            if (event.target.classList.contains('toggle-status')) {
                event.preventDefault();
                const todoId = event.target.dataset.id;
                await toggleTodoStatus(todoId, event.target);
            }

            // Handle delete
            if (event.target.classList.contains('delete-todo')) {
                event.preventDefault();
                const todoId = event.target.dataset.id;
                await deleteTodo(todoId, event.target);
            }
        });
    }
}

async function toggleTodoStatus(todoId, button) {
    // Show loading state
    const todoItem = button.closest('.todo-item');
    todoItem.classList.add('updating');

    try {
        const response = await fetch(`/todos/${todoId}/toggle`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Server error: ' + response.status);
        }

        const result = await response.json();

        // Update UI based on new status
        todoItem.classList.toggle('completed', result.completed);

        // Update button text
        button.textContent = result.completed ? 'Mark Incomplete' : 'Mark Complete';

        // Show success message
        showNotification('Todo status updated!', 'success');
    } catch (error) {
        console.error('Error toggling todo status:', error);
        showNotification('Failed to update todo status. Please try again.', 'error');
    } finally {
        // Remove loading state
        todoItem.classList.remove('updating');
    }
}

async function deleteTodo(todoId, button) {
    // Ask for confirmation
    if (!confirm('Are you sure you want to delete this todo?')) {
        return;
    }

    // Show loading state
    const todoItem = button.closest('.todo-item');
    todoItem.classList.add('deleting');

    try {
        const response = await fetch(`/todos/${todoId}`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error('Server error: ' + response.status);
        }

        // Remove the todo item with animation
        todoItem.classList.add('fade-out');
        setTimeout(() => {
            todoItem.remove();

            // Update todo count if needed
            updateTodoCount();

            // Show success message
            showNotification('Todo deleted successfully!', 'success');
        }, 300);
    } catch (error) {
        console.error('Error deleting todo:', error);
        showNotification('Failed to delete todo. Please try again.', 'error');
        todoItem.classList.remove('deleting');
    }
}

function addTodoToList(todo) {
    const todoList = document.getElementById('todo-list');
    if (!todoList) return;

    // Create new todo item element
    const todoItem = document.createElement('li');
    todoItem.className = `todo-item ${todo.completed ? 'completed' : ''}`;
    todoItem.id = `todo-${todo.id}`;

    // Set inner HTML with the todo content and action buttons
    todoItem.innerHTML = `
        <span class="todo-text">${escapeHtml(todo.title)}</span>
        <div class="todo-actions">
            <button class="toggle-status" data-id="${todo.id}">
                ${todo.completed ? 'Mark Incomplete' : 'Mark Complete'}
            </button>
            <button class="delete-todo" data-id="${todo.id}">Delete</button>
        </div>
    `;

    // Add with animation
    todoItem.classList.add('fade-in');
    todoList.appendChild(todoItem);

    // Update todo count
    updateTodoCount();
}

function updateTodoCount() {
    const todoCount = document.getElementById('todo-count');
    const todoItems = document.querySelectorAll('.todo-item');

    if (todoCount) {
        todoCount.textContent = todoItems.length;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        document.body.appendChild(notification);
    }

    // Set message and type
    notification.textContent = message;
    notification.className = `notification ${type}`;

    // Show notification
    notification.classList.add('show');

    // Hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Helper function to escape HTML special characters
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
