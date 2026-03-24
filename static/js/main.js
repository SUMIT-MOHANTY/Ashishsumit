document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Add datepicker enhancement if the browser doesn't support date inputs well
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs.length > 0) {
        // Check if the browser properly supports date inputs
        const test = document.createElement('input');
        test.type = 'date';
        // If the browser doesn't convert the type, it doesn't support date inputs
        if (test.type === 'text') {
            // Here you would ideally initialize a datepicker library
            console.log('Browser does not support date inputs natively');
        }
    }

    // Add confirmation for delete actions
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('Are you sure you want to delete this item?');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
