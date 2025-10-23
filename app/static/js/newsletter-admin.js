function updateBlockFields(blockDiv) {
    const typeSelect = blockDiv.querySelector('.block-type');

    const contentLabel = blockDiv.querySelector('.content-label');
    const contentInput = blockDiv.querySelector('.block-content');

    const imageUrlLabel = blockDiv.querySelector('.image-url-label');
    const imageUrlInput = blockDiv.querySelector('.block-image-url');

    const altTextLabel = blockDiv.querySelector('.alt-text-label');
    const altTextInput = blockDiv.querySelector('.block-alt-text');

    const urlTextLabel = blockDiv.querySelector(".url-text-label");
    const urlTextInput = blockDiv.querySelector(".block-url-text");

    const colourLabel = blockDiv.querySelector(".colour-label");
    const colourInput = blockDiv.querySelector(".block-colour");


    if (!typeSelect) return;

    const val = typeSelect.value;

    // Helper to toggle visibility and disable state
    function setVisibility(el, show) {
        if (!el) return;
        if (show) {
            el.classList.remove("no-display");
            el.removeAttribute("disabled");
        } else {
            el.classList.add("no-display");
            el.disabled = true;
        }
    }


    // Define all the config states for different dropdown values
    const visibilityConfig = {
        image: {
            content: false,
            contentLabel: false,
            imageUrl: true,
            imageUrlLabel: true,
            altText: true,
            altTextLabel: true,
            urlText: false,
            urlTextLabel: false,
            colourInput: false,
            colourLabel: false,
            labelText: "Content"
        },
        thumbnail: {
            content: false,
            contentLabel: false,
            imageUrl: true,
            imageUrlLabel: true,
            altText: true,
            altTextLabel: true,
            urlText: false,
            urlTextLabel: false,
            colourInput: false,
            colourLabel: false,
            labelText: "Content"
        },
        subheading: {
            content: true,
            contentLabel: true,
            imageUrl: false,
            imageUrlLabel: false,
            altText: false,
            altTextLabel: false,
            urlText: false,
            urlTextLabel: false,
            colourInput: false,
            colourLabel: false,
            labelText: "Content"
        },
        paragraph: {
            content: true,
            contentLabel: true,
            imageUrl: false,
            imageUrlLabel: false,
            altText: false,
            altTextLabel: false,
            urlText: false,
            urlTextLabel: false,
            colourInput: false,
            colourLabel: false,
            labelText: "Content"
        },
        button: {
            content: true,
            contentLabel: true,
            imageUrl: false,
            imageUrlLabel: false,
            altText: false,
            altTextLabel: false,
            urlText: true,
            urlTextLabel: true,
            colourInput: true,
            colourLabel: true,
            labelText: "Button Text",
            urlLabelText: "Button Link"
        },
        default: {
            content: true,
            contentLabel: true,
            imageUrl: false,
            imageUrlLabel: false,
            altText: false,
            altTextLabel: false,
            urlText: false,
            urlTextLabel: false,
            colourInput: true,
            colourLabel: true,
            labelText: "Content"
        }
    };

    // Apply changes based on selected value

    const config = visibilityConfig[val] || visibilityConfig.default;

    // Update label text if shown
    if (config.contentLabel && typeof config.labelText === "string") {
        contentLabel.textContent = config.labelText;
    }

    if (config.urlTextLabel && typeof config.labelText === "string") {
        urlTextLabel.textContent = config.urlLabelText;
    }

    // Apply all visibility states
    setVisibility(contentLabel, config.contentLabel);
    setVisibility(contentInput, config.content);
    setVisibility(imageUrlLabel, config.imageUrlLabel);
    setVisibility(imageUrlInput, config.imageUrl);
    setVisibility(altTextLabel, config.altTextLabel);
    setVisibility(altTextInput, config.altText);
    setVisibility(urlTextLabel, config.urlTextLabel);
    setVisibility(urlTextInput, config.urlText);
    setVisibility(colourLabel, config.colourLabel);
    setVisibility(colourInput, config.colourInput);

}
document.addEventListener("DOMContentLoaded", function () {

    const addBlockBtn = document.getElementById("add-block-btn");
    const blockContainer = document.getElementById("blocks-container"); // where blocks are added
    const blockTemplate = document.getElementById("block-template");
    const submitBtn = document.getElementById('article-post')
    let currentIndex = 0;


    submitBtn.addEventListener('click', function (e) {
        if (!confirm("Are you sure you want to upload this newsletter?")) {
            e.preventDefault();
        }
    });



    // Attach change listener to remove
    function attachRemoveListener(button, blockId, index) {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const blockToRemove = document.getElementById(blockId);
            if (blockToRemove) {
                blockToRemove.remove();
                reindexAllBlocks();
                currentIndex--;
            }

        });
    }

    // Attach change listener to dropdown
    blockContainer.querySelectorAll(".article-block").forEach((block) => {
        const typeSelect = block.querySelector(".block-type");
        if (typeSelect) {
            typeSelect.addEventListener("change", () => updateBlockFields(block));
            updateBlockFields(block); // run once to initialize display state
        }
        const upBtn = block.querySelector(`#up-block-btn-${idx}`);
        if (upBtn) attachUpListener(upBtn, idx);
        const downBtn = block.querySelector(`#down-block-btn-${idx}`);
        if (downBtn) attachDownListener(downBtn, idx);
    });

    // Try to initialize index from existing blocks
    const existingBlocks = document.querySelectorAll(".article-block");
    if (existingBlocks.length) {
        if (existingBlocks.length > 0) {
            currentIndex = existingBlocks.length - 1;
        }

    }

    addBlockBtn.addEventListener("click", function (e) {
        e.preventDefault();

        // Clone the hidden template
        const newBlock = blockTemplate.cloneNode(true);
        newBlock.classList.remove("no-display");
        newBlock.removeAttribute("disabled");

        // Replace all instances of __INDEX__ with the current index
        const html = newBlock.innerHTML.replace(/__INDEX__/g, currentIndex);
        newBlock.innerHTML = html;
        newBlock.id = `block-${currentIndex}`;

        // Attach change listener to dropdown
        const typeSelect = newBlock.querySelector(".block-type");
        typeSelect.addEventListener("change", function () {
            updateBlockFields(newBlock);
        });

        // Attach remove listener
        const rmvBtn = newBlock.querySelector(`#rmv-block-btn-${currentIndex}`);
        if (rmvBtn) {
            attachRemoveListener(rmvBtn, `block-${currentIndex}`, currentIndex);
        }

        const upBtn = newBlock.querySelector(`#up-block-btn-${currentIndex}`);
        if (upBtn) {
            attachUpListener(upBtn, currentIndex);
        }

        const downBtn = newBlock.querySelector(`#down-block-btn-${currentIndex}`);
        if (downBtn) {
            attachDownListener(downBtn, currentIndex);
        }

        blockContainer.appendChild(newBlock);
        currentIndex++;

        updateBlockFields(newBlock);

    });




    document.getElementById("preview-button").addEventListener("click", async function () {

        const form = document.getElementById("article-form");
        const formData = new FormData(form);
        const spinner = document.getElementById('preview-spinner');
        const errorBox = document.getElementById('preview-error');


        const timestamp = Date.now();
        spinner.style.display = 'flex';
        errorBox.textContent = "";

        await fetch(`/HDPSC-admin-panel/download-newsletter?ts=${timestamp}`, {
            method: "POST",
            body: formData
        })
            .then(async response => {
                if (!response.ok) {
                    const data = await response.json();

                    if (data.errors) {
                        let allErrors = '';
                        for (const [field, messages] of Object.entries(data.errors)) {
                            allErrors += `${field}: ${messages.join(', ')}\n`;
                        }
                        throw new Error(allErrors);
                    }

                    throw new Error(data.error || "Something went wrong");
                }

                return response.text();
            })
            .then(html => {
                const blob = new Blob([html], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `newsletter-${timestamp}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            })
            .catch(err => {
                console.error(err);
                errorBox.textContent = err.message;
            })
            .finally(() => {
                spinner.style.display = 'none';
            });


    });

    // Move block up
    function moveBlockUp(index) {
        const block = document.getElementById(`block-${index}`);
        if (!block) return;
        const prevBlock = block.previousElementSibling;
        if (prevBlock && prevBlock.classList.contains("article-block")) {
            block.parentNode.insertBefore(block, prevBlock);
            reindexAllBlocks();
        }
    }

    // Move block down
    function moveBlockDown(index) {
        const block = document.getElementById(`block-${index}`);
        if (!block) return;
        const nextBlock = block.nextElementSibling;
        if (nextBlock && nextBlock.classList.contains("article-block")) {
            block.parentNode.insertBefore(block, nextBlock.nextSibling);
            reindexAllBlocks();
        }
    }


    // Reindex all blocks after move or remove
    function reindexAllBlocks() {
        const blocks = blockContainer.querySelectorAll(".article-block");
        blocks.forEach((block, newIndex) => {
            // Always recalc from current index
            block.id = `block-${newIndex}`;
            block.querySelectorAll("[name], [id], [for]").forEach(el => {
                if (el.name) el.name = el.name.replace(/article-blocks-\d+-/, `article-blocks-${newIndex}-`);
                if (el.id) el.id = el.id.replace(/article-blocks-\d+-/, `article-blocks-${newIndex}-`);
                if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/article-blocks-\d+-/, `article-blocks-${newIndex}-`);
            });

            // Rebind listeners safely (remove old ones first)
            const rmvBtn = block.querySelector(`[id^="rmv-block-btn-"]`);
            if (rmvBtn) {
                rmvBtn.id = `rmv-block-btn-${newIndex}`;
                rmvBtn.replaceWith(rmvBtn.cloneNode(true)); // remove old listeners
                const freshRmv = block.querySelector(`#rmv-block-btn-${newIndex}`);
                attachRemoveListener(freshRmv, `block-${newIndex}`, newIndex);
            }

            const upBtn = block.querySelector(`[id^="up-block-btn-"]`);
            if (upBtn) {
                upBtn.id = `up-block-btn-${newIndex}`;
                upBtn.replaceWith(upBtn.cloneNode(true));
                const freshUp = block.querySelector(`#up-block-btn-${newIndex}`);
                attachUpListener(freshUp, newIndex);
            }

            const downBtn = block.querySelector(`[id^="down-block-btn-"]`);
            if (downBtn) {
                downBtn.id = `down-block-btn-${newIndex}`;
                downBtn.replaceWith(downBtn.cloneNode(true));
                const freshDown = block.querySelector(`#down-block-btn-${newIndex}`);
                attachDownListener(freshDown, newIndex);
            }
        });
    }

    // Attach up/down listeners
    function attachUpListener(button, index) {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            moveBlockUp(index);
        });
    }
    function attachDownListener(button, index) {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            moveBlockDown(index);
        });
    }


});

