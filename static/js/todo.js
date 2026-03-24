document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const todoForm = document.getElementById('todo-form');
    const todoList = document.getElementById('todo-list');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Error message display function
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.querySelector('.container').prepend(errorDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Success message display function
    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.querySelector('.container').prepend(successDiv);

        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    // Add CSRF token to all AJAX requests
    function addCSRFToken(xhr) {
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
    }

    // Handle form submission for creating new todos
    if (todoForm) {
        todoForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(todoForm);
            const title = formData.get('title');

            if (!title || title.trim() === '') {
                showError('Todo title cannot be empty');
                return;
            }

            // Show loading state
            const submitButton = todoForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
            submitButton.disabled = true;

            // Send AJAX request
            fetch('/add', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server responded with an error');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Add the new todo to the list without reloading
                    const newTodo = createTodoElement(data.todo);
                    todoList.prepend(newTodo);
                    todoForm.reset();
                    showSuccess('Todo added successfully!');
                } else {
                    showError(data.error || 'Failed to add todo');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Failed to add todo: ' + error.message);
            })
            .finally(() => {
                // Reset button state
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            });
        });
    }

    // Create a new todo element
    function createTodoElement(todo) {
        const li = document.createElement('li');
        li.className = `list-group-item d-flex justify-content-between align-items-center ${todo.completed ? 'list-group-item-success' : ''}`;
        li.dataset.id = todo.id;

        const titleSpan = document.createElement('span');
        titleSpan.className = todo.completed ? 'text-decoration-line-through' : '';
        titleSpan.textContent = todo.title;

        const actionsDiv = document.createElement('div');

        // Toggle status button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'btn btn-sm ' + (todo.completed ? 'btn-warning' : 'btn-success');
        toggleButton.textContent = todo.completed ? 'Mark Undone' : 'Mark Done';
        toggleButton.addEventListener('click', () => toggleTodoStatus(todo.id, !todo.completed));

        // Delete button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-sm btn-danger ms-2';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => deleteTodo(todo.id));

        actionsDiv.appendChild(toggleButton);
        actionsDiv.appendChild(deleteButton);

        li.appendChild(titleSpan);
        li.appendChild(actionsDiv);

        return li;
    }

    // Toggle todo status
    function toggleTodoStatus(todoId, newStatus) {
        const todoItem = document.querySelector(`li[data-id="${todoId}"]`);
        if (!todoItem) return;

        // Optimistic UI update
        const statusText = newStatus ? 'Done' : 'Undone';
        const toggleButton = todoItem.querySelector('.btn-success, .btn-warning');
        const titleSpan = todoItem.querySelector('span');

        // Show loading state on button
        const originalText = toggleButton.textContent;
        toggleButton.textContent = 'Updating...';
        toggleButton.disabled = true;

        fetch('/toggle/' + todoId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ completed: newStatus })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Update UI based on new status
                if (newStatus) {
                    todoItem.classList.add('list-group-item-success');
                    titleSpan.classList.add('text-decoration-line-through');
                    toggleButton.textContent = 'Mark Undone';
                    toggleButton.classList.remove('btn-success');
                    toggleButton.classList.add('btn-warning');
                } else {
                    todoItem.classList.remove('list-group-item-success');
                    titleSpan.classList.remove('text-decoration-line-through');
                    toggleButton.textContent = 'Mark Done';
                    toggleButton.classList.remove('btn-warning');
                    toggleButton.classList.add('btn-success');
                }
                showSuccess(`Todo marked as ${statusText}!`);
            } else {
                // Revert optimistic update
                toggleButton.textContent = originalText;
                showError(data.error || 'Failed to update todo status');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            toggleButton.textContent = originalText;
            showError('Error updating todo: ' + error.message);
        })
        .finally(() => {
            toggleButton.disabled = false;
        });
    }

    // Delete todo
    function deleteTodo(todoId) {
        const todoItem = document.querySelector(`li[data-id="${todoId}"]`);
        if (!todoItem) return;

        if (!confirm('Are you sure you want to delete this todo?')) {
            return;
        }

        // Show loading state
        todoItem.classList.add('opacity-50');
        const deleteButton = todoItem.querySelector('.btn-danger');
        const originalText = deleteButton.textContent;
        deleteButton.textContent = 'Deleting...';
        deleteButton.disabled = true;

        fetch('/delete/' + todoId, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Animate removal
                todoItem.style.height = todoItem.offsetHeight + 'px';
                todoItem.classList.add('fade-out');
                setTimeout(() => {
                    todoItem.remove();
                    showSuccess('Todo deleted successfully!');
                }, 300);
            } else {
                // Revert loading state
                todoItem.classList.remove('opacity-50');
                deleteButton.textContent = originalText;
                deleteButton.disabled = false;
                showError(data.error || 'Failed to delete todo');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            todoItem.classList.remove('opacity-50');
            deleteButton.textContent = originalText;
            deleteButton.disabled = false;
            showError('Error deleting todo: ' + error.message);
        });
    }

    // Add event delegation for todo actions
    if (todoList) {
        todoList.addEventListener('click', function(e) {
            const target = e.target;

            // Check if clicked element is a button
            if (target.tagName === 'BUTTON') {
                const todoItem = target.closest('li');
                if (!todoItem) return;

                const todoId = todoItem.dataset.id;

                if (target.classList.contains('btn-success') || target.classList.contains('btn-warning')) {
                    // Toggle button clicked
                    const isCompleted = target.textContent.includes('Undone');
                    toggleTodoStatus(todoId, !isCompleted);
                } else if (target.classList.contains('btn-danger')) {
                    // Delete button clicked
                    deleteTodo(todoId);
                }
            }
        });
    }
});
