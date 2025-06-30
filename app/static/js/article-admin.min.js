

document.addEventListener("DOMContentLoaded", function () {
    
    const addBlockBtn = document.getElementById("add-block-btn");
    const blockContainer = document.getElementById("blocks-container"); // where blocks are added
    const blockTemplate = document.getElementById("block-template");
    let currentIndex = 0;

    // Attach change listener to dropdown
        const initTypeSelect = blockContainer.querySelector(".block-type");
        initTypeSelect.addEventListener("change", function () {
            updateBlockFields(blockContainer);
        });

    // Try to initialize index from existing blocks
    const existingBlocks = document.querySelectorAll(".article-block");
    if (existingBlocks.length) {
        currentIndex = existingBlocks.length;
    }

    addBlockBtn.addEventListener("click", function (e) {
        e.preventDefault();

        // Clone the hidden template
        const newBlock = blockTemplate.cloneNode(true);
        newBlock.classList.remove("no-display");

        // Replace all instances of __INDEX__ with the current index
        const html = newBlock.innerHTML.replace(/__INDEX__/g, currentIndex);
        newBlock.innerHTML = html;

        // Optional: give each block a unique ID
        newBlock.id = `block-${currentIndex}`;

        // Attach change listener to dropdown
        const typeSelect = newBlock.querySelector(".block-type");
        typeSelect.addEventListener("change", function () {
            updateBlockFields(newBlock);
        });


        blockContainer.appendChild(newBlock);
        
        currentIndex++;
    });


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
            if (imageUrlLabel) imageUrlLabel.classList.remove("no-display");
            if (imageUrlInput) imageUrlInput.classList.remove("no-display");
        } else if (val === "figure") {
            contentLabel.textContent = "Caption";
            if (imageUrlLabel) imageUrlLabel.classList.remove("no-display");
            if (imageUrlInput) imageUrlInput.classList.remove("no-display");
        } else {
            contentLabel.textContent = "Content";
            if (imageUrlLabel) imageUrlLabel.classList.add("no-display");
            if (imageUrlInput) imageUrlInput.classList.add("no-display");
        }
    }
});