/**
 * Todo Application JavaScript
 * Handles asynchronous CRUD operations for Todo items
 */

// Base URL for API endpoints
const API_URL = '/todos';

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    loadTodos();

    // Set up event listeners
    setupEventListeners();
});

/**
 * Set up event listeners for the application
 */
function setupEventListeners() {
    // Form submission for creating new todos
    const todoForm = document.getElementById('todo-form');
    if (todoForm) {
        todoForm.addEventListener('submit', handleTodoFormSubmit);
    }

    // For handling dynamic elements that might be added later
    document.addEventListener('click', (event) => {
        // Handle complete/incomplete toggle
        if (event.target.classList.contains('toggle-status')) {
            const todoId = event.target.getAttribute('data-id');
            toggleTodoStatus(todoId);
        }

        // Handle delete button
        if (event.target.classList.contains('delete-todo')) {
            const todoId = event.target.getAttribute('data-id');
            deleteTodo(todoId);
        }
    });
}

/**
 * Load all todos from the API and display them
 */
async function loadTodos() {
    try {
        showLoader();
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`Failed to load todos: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        displayTodos(data.todos || []);
    } catch (error) {
        console.error('Error loading todos:', error);
        showErrorMessage('Failed to load todos. Please try again.');
    } finally {
        hideLoader();
    }
}

/**
 * Display todos in the UI
 * @param {Array} todos - The todos to display
 */
function displayTodos(todos) {
    const todoList = document.getElementById('todo-list');
    if (!todoList) return;

    // Clear existing todos
    todoList.innerHTML = '';

    if (todos.length === 0) {
        todoList.innerHTML = '<li class="no-todos">No todos yet. Create one!</li>';
        return;
    }

    // Sort todos by creation date (newest first)
    todos.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    // Create DOM elements for each todo
    todos.forEach(todo => {
        const todoItem = document.createElement('li');
        todoItem.className = `todo-item ${todo.completed ? 'completed' : ''}`;
        todoItem.setAttribute('data-id', todo.id);

        const todoDate = new Date(todo.created_at);
        const formattedDate = todoDate.toLocaleString();

        todoItem.innerHTML = `
            <div class="todo-header">
                <h3 class="todo-title">${escapeHtml(todo.title)}</h3>
                <div class="todo-actions">
                    <button class="toggle-status" data-id="${todo.id}">
                        ${todo.completed ? 'Mark Incomplete' : 'Mark Complete'}
                    </button>
                    <button class="delete-todo" data-id="${todo.id}">Delete</button>
                </div>
            </div>
            <p class="todo-description">${escapeHtml(todo.description || '')}</p>
            <span class="todo-date">Created: ${formattedDate}</span>
            <span class="todo-status">${todo.completed ? 'Completed' : 'Active'}</span>
        `;

        todoList.appendChild(todoItem);
    });
}

/**
 * Handle form submission for creating a new todo
 * @param {Event} event - The form submission event
 */
async function handleTodoFormSubmit(event) {
    event.preventDefault();

    const titleInput = document.getElementById('todo-title');
    const descriptionInput = document.getElementById('todo-description');

    if (!titleInput || !titleInput.value.trim()) {
        showErrorMessage('Title is required!');
        return;
    }

    const newTodo = {
        title: titleInput.value.trim(),
        description: descriptionInput ? descriptionInput.value.trim() : '',
        completed: false
    };

    try {
        showLoader();
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newTodo)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to create todo: ${response.status}`);
        }

        // Reset form
        if (titleInput) titleInput.value = '';
        if (descriptionInput) descriptionInput.value = '';

        // Show success message
        showSuccessMessage('Todo created successfully!');

        // Reload todos to show the new one
        loadTodos();
    } catch (error) {
        console.error('Error creating todo:', error);
        showErrorMessage(error.message || 'Failed to create todo. Please try again.');
    } finally {
        hideLoader();
    }
}

/**
 * Toggle the completed status of a todo
 * @param {string} todoId - The ID of the todo to update
 */
async function toggleTodoStatus(todoId) {
    try {
        // Get the current status of the todo
        const todoElement = document.querySelector(`.todo-item[data-id="${todoId}"]`);
        const isCurrentlyCompleted = todoElement.classList.contains('completed');

        // Optimistically update UI
        todoElement.classList.toggle('completed');
        const statusButton = todoElement.querySelector('.toggle-status');
        const statusSpan = todoElement.querySelector('.todo-status');

        if (statusButton) {
            statusButton.innerText = isCurrentlyCompleted ? 'Mark Complete' : 'Mark Incomplete';
        }

        if (statusSpan) {
            statusSpan.innerText = isCurrentlyCompleted ? 'Active' : 'Completed';
        }

        // Show mini loader on the todo item
        todoElement.classList.add('updating');

        // Send the request to the server
        const response = await fetch(`${API_URL}/${todoId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                completed: !isCurrentlyCompleted
            })
        });

        if (!response.ok) {
            // Revert UI changes if request failed
            todoElement.classList.toggle('completed');
            if (statusButton) {
                statusButton.innerText = isCurrentlyCompleted ? 'Mark Incomplete' : 'Mark Complete';
            }
            if (statusSpan) {
                statusSpan.innerText = isCurrentlyCompleted ? 'Completed' : 'Active';
            }

            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to update todo: ${response.status}`);
        }

        showSuccessMessage(`Todo ${!isCurrentlyCompleted ? 'completed' : 'marked as active'}!`);
    } catch (error) {
        console.error('Error updating todo:', error);
        showErrorMessage(error.message || 'Failed to update todo status. Please try again.');
    } finally {
        // Remove the updating class
        const todoElement = document.querySelector(`.todo-item[data-id="${todoId}"]`);
        if (todoElement) {
            todoElement.classList.remove('updating');
        }
    }
}

/**
 * Delete a todo
 * @param {string} todoId - The ID of the todo to delete
 */
async function deleteTodo(todoId) {
    // Ask for confirmation
    if (!confirm('Are you sure you want to delete this todo?')) {
        return;
    }

    try {
        const todoElement = document.querySelector(`.todo-item[data-id="${todoId}"]`);
        if (todoElement) {
            // Animate removal
            todoElement.classList.add('deleting');
        }

        const response = await fetch(`${API_URL}/${todoId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to delete todo: ${response.status}`);
        }

        // Remove from DOM after animation completes
        setTimeout(() => {
            if (todoElement) {
                todoElement.remove();

                // Check if we need to show "No todos" message
                const todoList = document.getElementById('todo-list');
                if (todoList && todoList.children.length === 0) {
                    todoList.innerHTML = '<li class="no-todos">No todos yet. Create one!</li>';
                }
            }
        }, 300);

        showSuccessMessage('Todo deleted successfully!');
    } catch (error) {
        console.error('Error deleting todo:', error);
        showErrorMessage(error.message || 'Failed to delete todo. Please try again.');

        // Remove the deleting class if there was an error
        const todoElement = document.querySelector(`.todo-item[data-id="${todoId}"]`);
        if (todoElement) {
            todoElement.classList.remove('deleting');
        }
    }
}

/**
 * Show loader while operations are in progress
 */
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.classList.add('active');
    } else {
        // Create loader if it doesn't exist
        const newLoader = document.createElement('div');
        newLoader.id = 'loader';
        newLoader.className = 'loader active';
        newLoader.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(newLoader);
    }
}

/**
 * Hide loader after operations complete
 */
function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.classList.remove('active');
    }
}

/**
 * Show error message to the user
 * @param {string} message - The error message to display
 */
function showErrorMessage(message) {
    showNotification(message, 'error');
}

/**
 * Show success message to the user
 * @param {string} message - The success message to display
 */
function showSuccessMessage(message) {
    showNotification(message, 'success');
}

/**
 * Show a notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification ('error' or 'success')
 */
function showNotification(message, type = 'info') {
    const notifications = document.getElementById('notifications');

    if (!notifications) {
        // Create notifications container if it doesn't exist
        const notificationsContainer = document.createElement('div');
        notificationsContainer.id = 'notifications';
        document.body.appendChild(notificationsContainer);
    }

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerText = message;

    document.getElementById('notifications').appendChild(notification);

    // Auto-remove after a delay
    setTimeout(() => {
        notification.classList.add('hide');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - The text to escape
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';

    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}
