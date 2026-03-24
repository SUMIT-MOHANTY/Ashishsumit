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

        // Handle edit button
        if (event.target.classList.contains('edit-btn')) {
            const todoItem = event.target.closest('.todo-item');
            if (todoItem) {
                const todoId = todoItem.getAttribute('data-id');
                const todoTitle = todoItem.querySelector('.todo-title').textContent;
                editTodo(todoId, todoTitle);
            }
        }
    });

    // Handle checkbox changes
    document.addEventListener('change', (event) => {
        if (event.target.classList.contains('todo-checkbox')) {
            const todoItem = event.target.closest('.todo-item');
            if (todoItem) {
                const todoId = todoItem.getAttribute('data-id');
                toggleTodoStatus(todoId, event.target.checked);
            }
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
        todoItem.className = `todo-item`;
        todoItem.setAttribute('data-id', todo.id);

        const todoDate = new Date(todo.created_at);
        const formattedDate = todoDate.toLocaleString();
        
        const isCompleted = todo.completed || todo.complete;

        todoItem.innerHTML = `
            <div class="todo-content ${isCompleted ? 'completed' : ''}">
                <input type="checkbox" class="todo-checkbox" ${isCompleted ? 'checked' : ''}>
                <span class="todo-title">${escapeHtml(todo.title)}</span>
            </div>
            <div class="todo-header">
                <div class="todo-actions">
                    <button class="edit-btn">Edit</button>
                    <button class="delete-todo" data-id="${todo.id}">Delete</button>
                    <button class="toggle-status" data-id="${todo.id}">
                        ${isCompleted ? 'Mark Incomplete' : 'Mark Complete'}
                    </button>
                </div>
            </div>
            ${todo.description ? `<p class="todo-description">${escapeHtml(todo.description)}</p>` : ''}
            <span class="todo-date">Created: ${formattedDate}</span>
            <span class="todo-status">${isCompleted ? 'Completed' : 'Active'}</span>
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

    const titleInput = document.getElementById('todo-title') || document.getElementById('todo-input');
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
 * @param {boolean} isCompleted - The new completion status
 */
async function toggleTodoStatus(todoId, isCompleted) {
    try {
        // Get the current status of the todo if not provided
        const todoElement = document.querySelector(`.todo-item[data-id="${todoId}"]`);
        const todoContent = todoElement.querySelector('.todo-content');
        
        if (isCompleted === undefined) {
            isCompleted = !todoContent.classList.contains('completed');
        }

        // Optimistically update UI
        if (isCompleted) {
            todoContent.classList.add('completed');
        } else {
            todoContent.classList.remove('completed');
        }
        
        const statusButton = todoElement.querySelector('.toggle-status');
        const statusSpan = todoElement.querySelector('.todo-status');
        const checkbox = todoElement.querySelector('.todo-checkbox');

        if (checkbox) {
            checkbox.checked = isCompleted;
        }

        if (statusButton) {
            statusButton.innerText = isCompleted ? 'Mark Incomplete' : 'Mark Complete';
        }

        if (statusSpan) {
            statusSpan.innerText = isCompleted ? 'Completed' : 'Active';
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
                completed: isCompleted
            })
        });

        if (!response.ok) {
            // Revert UI changes if request failed
            if (isCompleted) {
                todoContent.classList.remove('completed');
            } else {
                todoContent.classList.add('completed');
            }
            
            if (checkbox) {
                checkbox.checked = !isCompleted;
            }
            
            if (statusButton) {
                statusButton.innerText = isCompleted ? 'Mark Complete' : 'Mark Incomplete';
            }
            
            if (statusSpan) {
                statusSpan.innerText = isCompleted ? 'Active' : 'Completed';
            }

            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to update todo: ${response.status}`);
        }

        showSuccessMessage(`Todo ${isCompleted ? 'completed' : 'marked as active'}!`);
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
 * Edit a todo
 * @param {string} todoId - The ID of the todo to edit
 * @param {string} currentTitle - Current todo title
 */
async function editTodo(todoId, currentTitle) {
    const newTitle = prompt('Edit todo:', currentTitle);

    if (newTitle === null) {
        // User cancelled the prompt
        return;
    }

    if (newTitle.trim() === '') {
        showErrorMessage('Todo title cannot be empty');
        return;
    }

    try {
        const todoElement = document.querySelector(`.todo-item[data-id="${todoId}"]`);
        todoElement.classList.add('updating');

        const response = await fetch(`${API_URL}/${todoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: newTitle })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to update todo: ${response.status}`);
        }

        const updatedTodo = await response.json();
        
        const todoTitle = todoElement.querySelector('.todo-title');
        if (todoTitle) {
            todoTitle.textContent = updatedTodo.title;
        }

        showSuccessMessage('Todo updated successfully!');
    } catch (error) {
        console.error('Error updating todo:', error);
        showErrorMessage(error.message || 'Failed to update todo. Please try again.');
    } finally {
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
            
            showSuccessMessage('Todo deleted successfully!');
        }, 300);
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
 * Escape HTML special characters to prevent XSS
 * @param {string} unsafe - String that might contain HTML
 * @return {string} - Escaped safe string
 */
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Show a success message to the user
 * @param {string} message - The message to display
 */
function showSuccessMessage(message) {
    // Implementation depends on how you want to show messages
    // Could use a toast notification, alert box, or dedicated message area
    const messageArea = document.getElementById('message-area');
    
    if (messageArea) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message success';
        messageElement.textContent = message;
        
        messageArea.appendChild(messageElement);
        
        // Remove after a few seconds
        setTimeout(() => {
            messageElement.classList.add('hiding');
            setTimeout(() => messageElement.remove(), 300);
        }, 3000);
    } else {
        console.log('Success:', message);
    }
}

/**
 * Show an error message to the user
 * @param {string} message - The error message to display
 */
function showErrorMessage(message) {
    // Implementation depends on how you want to show errors
    const messageArea = document.getElementById('message-area');
    
    if (messageArea) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message error';
        messageElement.textContent = message;
        
        messageArea.appendChild(messageElement);
        
        // Remove after a few seconds
        setTimeout(() => {
            messageElement.classList.add('hiding');
            setTimeout(() => messageElement.remove(), 300);
        }, 5000);
    } else {
        console.error('Error:', message);
    }
}

/**
 * Show loading indicator
 */
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'block';
    }
}

/**
 * Hide loading indicator
 */
function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}
