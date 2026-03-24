/**
 * Todo Application Client-Side Script
 * Handles AJAX requests to the Todo API and UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {

    // Elements
    const todoForm = document.getElementById('todo-form');
    const todoList = document.getElementById('todo-list');
    const todoInput = document.getElementById('todo-input');
    const errorMessage = document.getElementById('error-message');

    // Event listeners
    if (todoForm) {
        todoForm.addEventListener('submit', addTodo);
    }

    // Initial load
    loadTodos();

    /**
     * Load all todos from the API and display them
     */
    function loadTodos() {
        fetch('/todos')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch todos');
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.todos) {
                    renderTodos(data.todos);
                } else {
                    showError('Failed to load todos');
                }
            })
            .catch(error => {
                console.error('Error fetching todos:', error);
                showError('Failed to load todos: ' + error.message);
            });
    }

    /**
     * Render todo items in the list
     * @param {Array} todos - Array of todo objects
     */
    function renderTodos(todos) {
        if (!todoList) return;

        todoList.innerHTML = '';

        if (todos.length === 0) {
            todoList.innerHTML = '<li class="no-todos">No todos yet! Add one above.</li>';
            return;
        }

        todos.forEach(todo => {
            const li = document.createElement('li');
            li.className = 'todo-item';
            li.dataset.id = todo.id;

            // Create todo item structure
            li.innerHTML = `
                <div class="todo-content ${todo.complete ? 'completed' : ''}">
                    <input type="checkbox" class="todo-checkbox" ${todo.complete ? 'checked' : ''}>
                    <span class="todo-title">${escapeHtml(todo.title)}</span>
                </div>
                <div class="todo-actions">
                    <button class="edit-btn">Edit</button>
                    <button class="delete-btn">Delete</button>
                </div>
            `;

            // Add event listeners
            const checkbox = li.querySelector('.todo-checkbox');
            const editBtn = li.querySelector('.edit-btn');
            const deleteBtn = li.querySelector('.delete-btn');

            checkbox.addEventListener('change', () => toggleTodoComplete(todo.id, checkbox.checked));
            editBtn.addEventListener('click', () => editTodo(todo.id, todo.title));
            deleteBtn.addEventListener('click', () => deleteTodo(todo.id));

            todoList.appendChild(li);
        });
    }

    /**
     * Add a new todo
     * @param {Event} e - Form submit event
     */
    function addTodo(e) {
        e.preventDefault();

        const title = todoInput.value.trim();
        if (!title) {
            showError('Todo title cannot be empty');
            return;
        }

        fetch('/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to create todo');
                });
            }
            return response.json();
        })
        .then(todo => {
            todoInput.value = '';
            hideError();
            loadTodos(); // Reload all todos to get the updated list
        })
        .catch(error => {
            console.error('Error adding todo:', error);
            showError(error.message);
        });
    }

    /**
     * Toggle the completion status of a todo
     * @param {number} id - Todo ID
     * @param {boolean} complete - New completion status
     */
    function toggleTodoComplete(id, complete) {
        fetch(`/todos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ complete })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to update todo');
                });
            }
            return response.json();
        })
        .then(updatedTodo => {
            const todoItem = document.querySelector(`.todo-item[data-id="${id}"] .todo-content`);
            if (todoItem) {
                if (updatedTodo.complete) {
                    todoItem.classList.add('completed');
                } else {
                    todoItem.classList.remove('completed');
                }
            }
            hideError();
        })
        .catch(error => {
            console.error('Error updating todo:', error);
            showError(error.message);
        });
    }

    /**
     * Edit a todo
     * @param {number} id - Todo ID
     * @param {string} currentTitle - Current todo title
     */
    function editTodo(id, currentTitle) {
        const newTitle = prompt('Edit todo:', currentTitle);

        if (newTitle === null) {
            // User cancelled the prompt
            return;
        }

        if (newTitle.trim() === '') {
            showError('Todo title cannot be empty');
            return;
        }

        fetch(`/todos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: newTitle })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to update todo');
                });
            }
            return response.json();
        })
        .then(updatedTodo => {
            const todoTitle = document.querySelector(`.todo-item[data-id="${id}"] .todo-title`);
            if (todoTitle) {
                todoTitle.textContent = updatedTodo.title;
            }
            hideError();
        })
        .catch(error => {
            console.error('Error updating todo:', error);
            showError(error.message);
        });
    }

    /**
     * Delete a todo
     * @param {number} id - Todo ID
     */
    function deleteTodo(id) {
        if (!confirm('Are you sure you want to delete this todo?')) {
            return;
        }

        fetch(`/todos/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to delete todo');
                });
            }
            return response.json();
        })
        .then(data => {
            const todoItem = document.querySelector(`.todo-item[data-id="${id}"]`);
            if (todoItem) {
                todoItem.remove();
            }

            // Check if list is empty
            if (todoList.children.length === 0) {
                todoList.innerHTML = '<li class="no-todos">No todos yet! Add one above.</li>';
            }

            hideError();
        })
        .catch(error => {
            console.error('Error deleting todo:', error);
            showError(error.message);
        });
    }

    /**
     * Show an error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        if (!errorMessage) return;

        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    /**
     * Hide the error message
     */
    function hideError() {
        if (!errorMessage) return;

        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} html - String to escape
     * @return {string} Escaped HTML string
     */
    function escapeHtml(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
});
