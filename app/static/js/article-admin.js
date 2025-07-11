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
    


    // Update label text first
    if (val === "figure") {
        contentLabel.textContent = "Caption";
    } else {
        contentLabel.textContent = "Content";
    }

    if (val === "image") {
        // no content field needed
        setVisibility(contentLabel, false);
        setVisibility(contentInput, false);

        // add url field
        setVisibility(imageUrlLabel, true);
        setVisibility(imageUrlInput, true);

        // add alt text field
        setVisibility(altTextLabel, true);
        setVisibility(altTextInput, true);

        // remove link text
        setVisibility(urlTextLabel, false);
        setVisibility(urlTextInput, false);


    } else if (val === "figure") {

        // use content label
        contentLabel.textContent = "Caption";
        setVisibility(contentLabel, true);
        setVisibility(contentInput, true);

        // caption field
        setVisibility(imageUrlLabel, true);
        setVisibility(imageUrlInput, true);

        // add alt text field for image
        setVisibility(altTextLabel, true);
        setVisibility(altTextInput, true);

        // remove link text
        setVisibility(urlTextLabel, false);
        setVisibility(urlTextInput, false);


    } else if (val === "link") {

        // use content label
        contentLabel.textContent = "URL";
        setVisibility(contentLabel, true);
        setVisibility(contentInput, true);

        // caption field
        setVisibility(imageUrlLabel, false);
        setVisibility(imageUrlInput, false);

        // no alt text
        setVisibility(altTextLabel, false);
        setVisibility(altTextInput, false);


        // add text field for link
        setVisibility(urlTextLabel, true);
        setVisibility(urlTextInput, true);


    }
    else if (val === "paragraph") {

        // use content label
        setVisibility(contentLabel, true);
        setVisibility(contentInput, true);

        // caption field
        setVisibility(imageUrlLabel, false);
        setVisibility(imageUrlInput, false);

        // no alt text
        setVisibility(altTextLabel, false);
        setVisibility(altTextInput, false);


        // add text field for link
        setVisibility(urlTextLabel, false);
        setVisibility(urlTextInput, false);


    }
    else if (val === "break") {

        // no labels
        setVisibility(contentLabel, false);
        setVisibility(contentInput, false);

        // caption field
        setVisibility(imageUrlLabel, false);
        setVisibility(imageUrlInput, false);

        // no alt text
        setVisibility(altTextLabel, false);
        setVisibility(altTextInput, false);


        // add text field for link
        setVisibility(urlTextLabel, false);
        setVisibility(urlTextInput, false);


    }
    else {
        // use content label nothing else
        contentLabel.textContent = "Content";
        setVisibility(contentLabel, true);
        setVisibility(contentInput, true);

        setVisibility(imageUrlLabel, false);
        setVisibility(imageUrlInput, false);

        setVisibility(altTextLabel, false);
        setVisibility(altTextInput, false);

        // remove link text
        setVisibility(urlTextLabel, false);
        setVisibility(urlTextInput, false);

    }
}
document.addEventListener("DOMContentLoaded", function () {

    const addBlockBtn = document.getElementById("add-block-btn");
    const blockContainer = document.getElementById("blocks-container"); // where blocks are added
    const blockTemplate = document.getElementById("block-template");
    const submitBtn = document.getElementById('article-post')
    let currentIndex = 0;


    submitBtn.addEventListener('click', function (e) {
        if (!confirm("Are you sure you want to upload this article?")) {
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
                reindexBlocks(index);
                currentIndex--;
            }

        });
    }

    function reindexBlocks(startIndex) {
        const blocks = blockContainer.querySelectorAll(".article-block");
        for (let i = 0; i < blocks.length; i++) {
            const block = blocks[i];
            const oldIndex = parseInt(block.id.split("-")[1]);
            if (oldIndex > startIndex) {
                const newIndex = oldIndex - 1;

                // Update block ID
                block.id = `block-${newIndex}`;

                // Update all name, id, for attributes inside the block
                block.querySelectorAll("[name], [id], [for]").forEach(el => {
                    if (el.name) el.name = el.name.replace(`article-blocks-${oldIndex}-`, `article-blocks-${newIndex}-`);
                    if (el.id) el.id = el.id.replace(`article-blocks-${oldIndex}-`, `article-blocks-${newIndex}-`);
                    if (el.htmlFor) el.htmlFor = el.htmlFor.replace(`article-blocks-${oldIndex}-`, `article-blocks-${newIndex}-`);
                });

                // Update remove button ID and rebind listener
                const oldBtn = block.querySelector(`#rmv-block-btn-${oldIndex}`);
                if (oldBtn) {
                    oldBtn.id = `rmv-block-btn-${newIndex}`;
                    attachRemoveListener(oldBtn, `block-${newIndex}`, newIndex);
                }
            }
        }
    }



    // Attach change listener to dropdown
    blockContainer.querySelectorAll(".article-block").forEach((block) => {
        const typeSelect = block.querySelector(".block-type");
        if (typeSelect) {
            typeSelect.addEventListener("change", () => updateBlockFields(block));
            updateBlockFields(block); // run once to initialize display state
        }
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

        blockContainer.appendChild(newBlock);
        currentIndex++;

    });

    function prefixAttributes(html, prefix = "preview-") {
        return html
            .replace(/id="([^"]+)"/g, (_, id) => `id="${prefix}${id}"`)
            .replace(/for="([^"]+)"/g, (_, id) => `for="${prefix}${id}"`)
            .replace(/name="([^"]+)"/g, (_, name) => `name="${prefix}${name}"`)
            .replace(/class="([^"]+)"/g, (_, classes) =>
                `class="${classes
                    .split(" ")
                    .map(cls => `${prefix}${cls}`)
                    .join(" ")}"`
            );
    }


    document.getElementById("preview-button").addEventListener("click", async function () {

        const form = document.getElementById("article-form");
        const formData = new FormData(form);
        const host = document.getElementById("preview-shadow-host");
        const spinner = document.getElementById('preview-spinner');
        const errorBox = document.getElementById('preview-error');


        const timestamp = Date.now();
        spinner.style.display = 'flex';
        errorBox.textContent = "";

        await fetch(`/HDPSC-admin-panel/preview-article?ts=${timestamp}`, {
            method: "POST",
            body: formData
        })
            .then(async response => {
                if (!response.ok) {
                    const data = await response.json();

                    if (data.errors) {
                        // You can loop over each field's errors
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
                const scopedHtml = prefixAttributes(html, "preview-");

                if (!host.shadowRoot) {
                    host.attachShadow({ mode: "open" });
                }

                const shadow = host.shadowRoot;
                shadow.innerHTML = "";

                const link = document.createElement("link");
                link.rel = "stylesheet";
                link.href = "/static/css/preview-base.css";
                shadow.appendChild(link);

                const link2 = document.createElement("link");
                link2.rel = "stylesheet";
                link2.href = "/static/css/preview-article.css";
                shadow.appendChild(link2);


                const wrapper = document.createElement("div");
                wrapper.innerHTML = scopedHtml;
                shadow.appendChild(wrapper);
            })
            .catch(err => {
                console.error(err);
                errorBox.textContent = err.message;
            })
            .finally(() => {
                host.classList.remove('hidden-rendered')
                spinner.style.display = 'none';
            });


    });

});

