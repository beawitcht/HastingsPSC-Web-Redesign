document.addEventListener("DOMContentLoaded", function () {
    // MOBILE NAV STUFF
    button = document.getElementById("hamburger");
    navMenu = document.getElementById("mobile");
    mainContent = document.getElementById("mainContent");
    banner = document.getElementById("banner");
    first = document.getElementById("first");
    body = document.getElementById("html");

    button.addEventListener("click", () => {
        const currentState = button.getAttribute("data-state");
        if (!currentState || currentState === "closed") {
            navMenu.setAttribute("class", "nav-bar-mobile-expanding");
            button.setAttribute("data-state", "opened");
            button.setAttribute("aria-expanded", "true");
            setTimeout(() => {
                navMenu.setAttribute("aria-expanded", "true");
                navMenu.setAttribute("class", "nav-bar-mobile");

                body.setAttribute("aria-expanded", "true");
                mainContent.setAttribute("aria-expanded", "true");
                if (banner) {
                    banner.setAttribute("aria-expanded", "true");
                }
                if (first) {
                    first.setAttribute("aria-expanded", "true");
                }
            }, 1); // 1ms delay to switch to transition animation


        } else {
            navMenu.setAttribute("class", "nav-bar-mobile-collapsing");
            button.setAttribute("data-state", "closed");
            button.setAttribute("aria-expanded", "false");
            // apply instantly on index (only page with banner)
            if (banner) {
                button.setAttribute("data-state", "closed");
                button.setAttribute("aria-expanded", "false");
                body.setAttribute("aria-expanded", "false");
                mainContent.setAttribute("aria-expanded", "false");

                banner.setAttribute("aria-expanded", "false");
            }
            if (first) {
                first.setAttribute("aria-expanded", "false");
            }


            setTimeout(() => {
                navMenu.setAttribute("aria-expanded", "false");
                navMenu.setAttribute("class", "nav-bar-mobile");
                if (!banner) {

                    body.setAttribute("aria-expanded", "false");
                    mainContent.setAttribute("aria-expanded", "false");
                    if (first) {
                        first.setAttribute("aria-expanded", "false");
                    }
                }
            }, 310);
        }
    });

    // if scroll locked highlight the burger to prompt unlock
    function isScrollLocked() {
        return getComputedStyle(document.getElementById("html")).overflow === 'hidden';
    }

    function highlightHamburger() {
        const hamburger = document.getElementById('hamImg');
        if (hamburger) {
            hamburger.classList.add('highlight-hamburger');
            setTimeout(() => hamburger.classList.remove('highlight-hamburger'), 1000);
        }
    }

    function handleScrollAttempt(e) {
        if (isScrollLocked()) {
            e.preventDefault();
            highlightHamburger();
        }
    }

    // Listen for scroll attempts
    window.addEventListener('wheel', handleScrollAttempt, { passive: false });
    window.addEventListener('touchmove', handleScrollAttempt, { passive: false });
    window.addEventListener('keydown', (e) => {
        const keys = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', ' '];
        if (keys.includes(e.key) && isScrollLocked()) {
            e.preventDefault();
            highlightHamburger();
        }
    });

});