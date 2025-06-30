document.addEventListener("DOMContentLoaded", function() {
    // Dynamic field labeling and show/hide logic
    function updateBlockFields(blockDiv) {
        const typeSelect = blockDiv.querySelector('.block-type');
        const contentLabel = blockDiv.querySelector('.content-label');
        const imageUrlLabel = blockDiv.querySelector('.image-url-label');
        const imageUrlInput = blockDiv.querySelector('.block-image-url');
        if (!typeSelect) return;

        const val = typeSelect.value;
        if (val === "image") {
            contentLabel.textContent = "Alt Text";
            imageUrlLabel.style.display = "";
            imageUrlInput.style.display = "";
        } else if (val === "figure") {
            contentLabel.textContent = "Caption";
            imageUrlLabel.style.display = "";
            imageUrlInput.style.display = "";
        } else {
            contentLabel.textContent = "Content";
            imageUrlLabel.style.display = "none";
            imageUrlInput.style.display = "none";
        }
    }

    // Initial update for all blocks
    document.querySelectorAll('.article-block').forEach(updateBlockFields);

    // Listen for block type changes
    document.querySelectorAll('.block-type').forEach(function(select) {
        select.addEventListener('change', function() {
            updateBlockFields(select.closest('.article-block'));
        });
    });

    // Add new block dynamically (AJAX-less, just submits with extra entry)
    document.getElementById('add-block-btn').addEventListener('click', function(e) {
        // Add a hidden input to trigger WTForms to add a block
        let form = document.getElementById('article-form');
        let input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'add_block';
        input.value = '1';
        form.appendChild(input);
        form.submit();
    });
});