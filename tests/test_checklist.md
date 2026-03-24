# Todo Application Test Checklist

A simplified checklist for quick manual testing of the Todo application.

## Core CRUD Functionality

### Create
- [ ] Create todo with valid text
- [ ] Validation prevents empty todos
- [ ] Newly created todo appears in list
- [ ] Input field clears after submission

### Read
- [ ] All todos display correctly in list
- [ ] Completed todos show visual indication
- [ ] List persists after page refresh
- [ ] Long todo text handles correctly (wrapping)

### Update
- [ ] Todo can be marked complete
- [ ] Todo can be marked incomplete
- [ ] Completed state persists after refresh
- [ ] Edit functionality works (if implemented)

### Delete
- [ ] Todo can be deleted
- [ ] Deleted todo disappears immediately
- [ ] Delete action cannot be accidentally triggered
- [ ] Bulk delete works (if implemented)

## UI/UX
- [ ] Responsive on mobile (320px width)
- [ ] Responsive on tablet (768px width)
- [ ] Responsive on desktop (1024px+ width)
- [ ] All buttons/controls are easily tappable on mobile
- [ ] Visual feedback for actions (hover, click states)

## Error Handling
- [ ] Empty input validation
- [ ] Network error handling (if applicable)
- [ ] Graceful handling of unexpected errors

## Accessibility
- [ ] Tab navigation works for all controls
- [ ] Sufficient color contrast
- [ ] Screen reader compatible
- [ ] Keyboard-only usability

## Notes
<!-- Add any observations or bugs found during testing here -->
