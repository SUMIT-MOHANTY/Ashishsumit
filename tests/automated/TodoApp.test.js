import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoApp from '../../src/components/TodoApp';

// Mock localStorage
const localStorageMock = (function() {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
    getAll: () => store,
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('TodoApp Component', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('renders the todo app with form and empty list', () => {
    render(<TodoApp />);
    expect(screen.getByText(/todo app/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/add new todo/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add/i })).toBeInTheDocument();
  });

  test('can add a new todo', async () => {
    render(<TodoApp />);

    // Add a new todo
    const input = screen.getByPlaceholderText(/add new todo/i);
    const addButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(input, { target: { value: 'Test todo item' } });
    fireEvent.click(addButton);

    // Check if the todo appears in the list
    await waitFor(() => {
      expect(screen.getByText('Test todo item')).toBeInTheDocument();
    });

    // Verify localStorage was updated
    expect(localStorage.setItem).toHaveBeenCalled();
  });

  test('shows validation error for empty todos', async () => {
    render(<TodoApp />);

    // Try to add an empty todo
    const addButton = screen.getByRole('button', { name: /add/i });
    fireEvent.click(addButton);

    // Check for error message
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid todo/i)).toBeInTheDocument();
    });

    // Verify localStorage was not updated
    expect(localStorage.setItem).not.toHaveBeenCalled();
  });

  test('can mark a todo as complete', async () => {
    render(<TodoApp />);

    // Add a new todo
    const input = screen.getByPlaceholderText(/add new todo/i);
    const addButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(input, { target: { value: 'Test todo item' } });
    fireEvent.click(addButton);

    // Find and click the checkbox
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    // Check if the todo is marked as completed
    await waitFor(() => {
      expect(checkbox).toBeChecked();
    });

    // Verify localStorage was updated
    expect(localStorage.setItem).toHaveBeenCalledTimes(2); // Once for add, once for update
  });

  test('can delete a todo', async () => {
    render(<TodoApp />);

    // Add a new todo
    const input = screen.getByPlaceholderText(/add new todo/i);
    const addButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(input, { target: { value: 'Test todo item' } });
    fireEvent.click(addButton);

    // Find and click the delete button
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    // Check if the todo is removed
    await waitFor(() => {
      expect(screen.queryByText('Test todo item')).not.toBeInTheDocument();
    });

    // Verify localStorage was updated
    expect(localStorage.setItem).toHaveBeenCalledTimes(2); // Once for add, once for delete
  });
});
