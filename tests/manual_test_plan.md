# Todo Application Manual Test Plan

This document outlines a comprehensive plan for manually testing the Todo application to ensure all features work as expected per the requirements.

## 1. Creating New Todos

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| Create todo with valid input | 1. Enter todo text in input field<br>2. Click "Add Todo" button | - New todo appears in the list<br>- Input field is cleared | |
| Create todo with empty input | 1. Leave input field empty<br>2. Click "Add Todo" button | - Form validation error appears<br>- Todo is not created | |
| Create todo with whitespace only | 1. Enter only spaces in input field<br>2. Click "Add Todo" button | - Form validation error appears<br>- Todo is not created | |
| Create todo with max length text | 1. Enter text at the maximum allowed length<br>2. Click "Add Todo" button | - Todo is created successfully<br>- Full text is visible (may wrap) | |
| Create multiple todos | 1. Create several todos in succession | - All todos appear in the list in the order they were created | |

## 2. Viewing the Todo List

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| View empty list | 1. Delete all existing todos<br>2. Refresh page | - Empty list message displayed or empty list with no error | |
| View list with multiple items | 1. Create multiple todo items<br>2. Observe list | - All created todos are visible<br>- Scrolling works if list is long | |
| View todos after page refresh | 1. Create several todos<br>2. Refresh browser | - All previously created todos still appear in the list<br>- Todo states (complete/incomplete) preserved | |
| Check list sorting order | 1. Create multiple todos<br>2. Observe their order | - Newest todos appear according to the app's sorting logic (newest first/last based on requirements) | |

## 3. Marking Todos as Complete/Incomplete

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| Mark todo as complete | 1. Click the checkbox/toggle for an incomplete todo | - Visual indication shows todo is completed (strikethrough, checkbox checked, etc.)<br>- State persists after page refresh | |
| Mark completed todo as incomplete | 1. Click the checkbox/toggle for a completed todo | - Visual indication shows todo is incomplete again<br>- State persists after page refresh | |
| Mark multiple todos in succession | 1. Toggle multiple todos quickly | - All todos reflect correct state with no errors | |
| Check completed todos filter (if available) | 1. Mark some todos as complete<br>2. Use filter for completed/active todos | - Only matching todos displayed when filtered | |

## 4. Deleting Todos

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| Delete a single todo | 1. Click delete button/icon on a todo | - Todo is removed from list<br>- No error messages | |
| Delete the last remaining todo | 1. Delete all but one todo<br>2. Delete the final todo | - Todo list is empty<br>- Empty state is handled properly | |
| Cancel delete operation (if confirmation exists) | 1. Click delete<br>2. Cancel the confirmation | - Todo remains in the list | |
| Delete completed todos (if bulk action available) | 1. Mark multiple todos as complete<br>2. Use "Clear completed" or similar function | - Only completed todos are removed<br>- Incomplete todos remain | |

## 5. Form Validation

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| Submit with empty input | 1. Leave input empty<br>2. Submit form | - Appropriate validation error shown<br>- Form not submitted | |
| Submit with only whitespace | 1. Type only spaces<br>2. Submit form | - Validation error shown<br>- Form not submitted | |
| Submit with extremely long text | 1. Enter text exceeding maximum length (if any)<br>2. Submit form | - Text truncated or error shown<br>- Appropriate handling occurs | |
| Input field character limit | 1. Try to type beyond character limit (if any) | - Input properly limits characters or shows warning | |

## 6. UI Responsiveness

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| Mobile view (small screen) | 1. Resize browser to mobile dimensions or use device emulation<br>2. Use the application | - UI adapts to small screen<br>- All functions accessible<br>- No overflow issues | |
| Tablet view (medium screen) | 1. Resize browser to tablet dimensions | - UI adapts appropriately<br>- All elements properly sized and positioned | |
| Desktop view (large screen) | 1. View on full desktop browser | - UI takes appropriate advantage of space<br>- No stretched or distorted elements | |
| Landscape vs portrait orientation | 1. Switch device/emulator between orientations | - UI adapts properly to both orientations | |

## 7. Edge Cases

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| Special characters in todo text | 1. Create todo with special characters (e.g., emoji, non-Latin scripts, HTML-like tags) | - Todo displays correctly<br>- No rendering issues | |
| Very large number of todos | 1. Create many todos (20+) | - Performance remains acceptable<br>- UI handles list correctly (scrolling, etc.) | |
| Network interruption (if app has backend) | 1. Disable network connection<br>2. Try to perform actions | - Appropriate error messages<br>- No data loss when connection restored | |
| Browser refresh during action | 1. Start creating/editing a todo<br>2. Refresh the browser before completing | - No corrupted state<br>- Clear user experience after refresh | |

## 8. Accessibility Testing

| Test Case | Steps | Expected Result | Actual Result |
|-----------|-------|-----------------|--------------|
| Keyboard navigation | 1. Navigate using only Tab, Enter, Space keys | - All interactive elements accessible<br>- Focus indicators visible | |
| Screen reader compatibility | 1. Enable screen reader<br>2. Navigate through the app | - All content readable<br>- Actions announced properly | |
| Color contrast | 1. Inspect text and background colors | - Sufficient contrast for readability | |
| Text scaling | 1. Increase browser text size to 200% | - Layout maintains functionality<br>- No text overflow issues | |

## Test Execution Record

| Test Date | Tester | Browser/Device | Overall Result | Major Issues Found |
|-----------|--------|---------------|----------------|---------------------|
|           |        |               |                |                     |

## Regression Testing

After any significant changes or bug fixes, retest the following critical functions:

1. Todo creation
2. Todo completion toggle
3. Todo deletion
4. Persistence after page refresh
