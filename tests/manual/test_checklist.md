# Todo Application Manual Test Checklist

## Creating New Todos
- [ ] Create a new todo with valid input
- [ ] Try creating a todo with empty input (should show validation error)
- [ ] Try creating a todo with just spaces (should show validation error)
- [ ] Create a todo with special characters
- [ ] Create a todo with a very long text (100+ characters)

## Viewing the Todo List
- [ ] Verify newly added todos appear in the list
- [ ] Verify todos persist after page refresh
- [ ] Check that todos maintain their correct order
- [ ] Verify completed todos show with the proper styling
- [ ] Test the list with 0, 1, few (3-5), and many (10+) todos

## Marking Todos as Complete/Incomplete
- [ ] Mark an incomplete todo as complete
- [ ] Mark a complete todo as incomplete
- [ ] Verify the UI updates immediately upon status change
- [ ] Verify the completed state persists after page refresh
- [ ] Test rapid toggling of the complete status

## Deleting Todos
- [ ] Delete a todo from the list
- [ ] Verify the todo is immediately removed from the UI
- [ ] Verify the deletion persists after page refresh
- [ ] Delete the first todo in the list
- [ ] Delete the last todo in the list
- [ ] Delete all todos one by one

## Form Validation
- [ ] Submit form with empty input (should show error)
- [ ] Submit form with only whitespace (should show error)
- [ ] Verify error message is clear and visible
- [ ] Verify form clears after successful submission
- [ ] Test form submission with keyboard (Enter key)

## UI Responsiveness
- [ ] Test application on desktop (19201080)
- [ ] Test application on tablet (7681024)
- [ ] Test application on mobile (375667)
- [ ] Verify all elements are properly visible on all screen sizes
- [ ] Check that interactive elements have appropriate size for touch screens
- [ ] Test with different browsers (Chrome, Firefox, Safari if available)

## Additional Tests
- [ ] Verify todos are sorted correctly (newest first or as per requirements)
- [ ] Check for any console errors during normal operation
- [ ] Test keyboard navigation and accessibility
- [ ] Check color contrast for accessibility
- [ ] Test with a screen reader if possible
