document.addEventListener('DOMContentLoaded', function () {
    
    document.querySelectorAll('.delete-user-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!btn.disabled) {
                if (!confirm("Are you sure you want to delete this user?")) {
                    e.preventDefault();
                }
            }
        });
    });

    document.querySelectorAll('.update-user-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!btn.disabled) {
                if (!confirm("Are you sure you want to update this user?")) {
                    e.preventDefault();
                }
            }
        });
    });
});