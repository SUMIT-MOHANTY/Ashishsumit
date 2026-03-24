/**
 * Secure Todo Application JavaScript
 * Implements client-side interactivity with security mitigations
 */

document.addEventListener('DOMContentLoaded', function() {
    // CSRF token handling
    const getCsrfToken = () => {
        // Get CSRF token from meta tag or cookie
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    };

    // Sanitize input to prevent XSS
    const sanitizeHTML = (str) => {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    };

    // Show feedback to user
    const showFeedback = (message, isError = false) => {
        const feedbackDiv = document.getElementById('feedback') ||
                          document.createElement('div');

        if (!document.getElementById('feedback')) {
            feedbackDiv.id = 'feedback';
            document.querySelector('body').insertAdjacentElement('afterbegin', feedbackDiv);
        }

        feedbackDiv.textContent = message;
        feedbackDiv.className = isError ? 'error-message' : 'success-message';
        feedbackDiv.style.display = 'block';

        // Auto-hide after 3 seconds
        setTimeout(() => {
            feedbackDiv.style.display = 'none';
        }, 3000);
    };

    // Error handler for fetch requests
    const handleFetchError = (error) => {
        console.error('Request failed:', error);
        showFeedback('An error occurred. Please try again.', true);
    };

    // Rate limiting for API requests
    let lastRequestTime = 0;
    const MIN_REQUEST_INTERVAL = 500; // ms

    const throttledFetch = (url, options) => {
        const now = Date.now();
        if (now - lastRequestTime < MIN_REQUEST_INTERVAL) {
            showFeedback('Please wait before making another request.', true);
            return Promise.reject(new Error('Rate limited'));
        }

        lastRequestTime = now;
        return fetch(url, options).catch(handleFetchError);
    };

    // Add Todo Form Submission
    const todoForm = document.getElementById('todo-form');
    if (todoForm) {
        todoForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const titleInput = document.getElementById('title');
            const descriptionInput = document.getElementById('description');

            // Validate inputs
            if (!titleInput.value.trim()) {
                showFeedback('Title cannot be empty', true);
                return;
            }

            // Prepare form data
            const formData = new FormData(todoForm);

            // Show loading state
            const submitBtn = todoForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            submitBtn.textContent = 'Adding...';
            submitBtn.disabled = true;

            // Submit form via AJAX
            throttledFetch('/todos', {
                method: 'POST',
                headers: {
                    'X-CSRF-Token': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Add new todo to the list without full page reload
                addTodoToList(data.todo);

                // Reset form
                todoForm.reset();
                showFeedback('Todo added successfully!');
            })
            .catch(error => {
                console.error('Error adding todo:', error);
                showFeedback('Failed to add todo. Please try again.', true);
            })
            .finally(() => {
                // Restore button state
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
            });
        });
    }

    // Add a new todo to the list
    function addTodoToList(todo) {
        const todoList = document.getElementById('todo-list');
        if (!todoList) return;

        const todoItem = document.createElement('div');
        todoItem.className = 'todo-item';
        todoItem.dataset.id = todo.id;

        // Sanitize content before insertion to prevent XSS
        todoItem.innerHTML = `
            <h3>${sanitizeHTML(todo.title)}</h3>
            <p>${sanitizeHTML(todo.description || '')}</p>
            <div class="todo-actions">
                <input type="checkbox" class="todo-status"
                       ${todo.completed ? 'checked' : ''}>
                <button class="delete-todo">Delete</button>
            </div>
        `;

        // Add event listeners to the new item
        addTodoEventListeners(todoItem);

        todoList.appendChild(todoItem);
    }

    // Add event listeners to todo items
    function addTodoEventListeners(todoItem) {
        // Status toggle
        const statusCheckbox = todoItem.querySelector('.todo-status');
        if (statusCheckbox) {
            statusCheckbox.addEventListener('change', function() {
                updateTodoStatus(todoItem.dataset.id, this.checked);
            });
        }

        // Delete button
        const deleteBtn = todoItem.querySelector('.delete-todo');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                deleteTodo(todoItem.dataset.id);
            });
        }
    }

    // Update todo status
    function updateTodoStatus(todoId, completed) {
        // Validate input
        if (!todoId || typeof completed !== 'boolean') {
            console.error('Invalid input for status update');
            return;
        }

        throttledFetch(`/todos/${todoId}/status`, {
            method: 'PUT',
            headers: {
                'X-CSRF-Token': getCsrfToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ completed })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            showFeedback(`Todo marked as ${completed ? 'completed' : 'not completed'}`);
        })
        .catch(error => {
            console.error('Error updating todo status:', error);
            showFeedback('Failed to update status. Please try again.', true);

            // Revert checkbox state on error
            const todoItem = document.querySelector(`.todo-item[data-id="${todoId}"]`);
            if (todoItem) {
                const checkbox = todoItem.querySelector('.todo-status');
                if (checkbox) checkbox.checked = !completed;
            }
        });
    }

    // Delete todo
    function deleteTodo(todoId) {
        if (!todoId) {
            console.error('Invalid todo ID for deletion');
            return;
        }

        if (!confirm('Are you sure you want to delete this todo?')) {
            return;
        }

        const todoItem = document.querySelector(`.todo-item[data-id="${todoId}"]`);
        if (!todoItem) return;

        // Visual feedback while deleting
        todoItem.style.opacity = '0.5';

        throttledFetch(`/todos/${todoId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRF-Token': getCsrfToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Remove from DOM
            todoItem.remove();
            showFeedback('Todo deleted successfully');
        })
        .catch(error => {
            console.error('Error deleting todo:', error);
            showFeedback('Failed to delete todo. Please try again.', true);
            // Restore visibility
            todoItem.style.opacity = '1';
        });
    }

    // Initialize existing todo items
    const todoItems = document.querySelectorAll('.todo-item');
    todoItems.forEach(addTodoEventListeners);
});
