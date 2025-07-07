// MOBILE NAV STUFF
    button = document.getElementById("hamburger");
    navMenu = document.getElementById("mobile");
    mainContent = document.getElementById("mainContent");
    banner = document.getElementById("banner");
    first = document.getElementById("first");

    button.addEventListener("click", () => {
        const currentState = button.getAttribute("data-state");
        if (!currentState || currentState === "closed") {
            navMenu.setAttribute("class", "nav-bar-mobile-expanding");
            setTimeout(() => {
                navMenu.setAttribute("aria-expanded", "true");
                navMenu.setAttribute("class", "nav-bar-mobile");
                button.setAttribute("data-state", "opened");
                button.setAttribute("aria-expanded", "true");
                mainContent.setAttribute("aria-expanded", "true");
                if(banner){
                    banner.setAttribute("aria-expanded", "true");
                }
                first.setAttribute("aria-expanded", "true");
            }, 1); // 1ms delay to switch to transition animation


        } else {
            navMenu.setAttribute("aria-expanded", "false");
            button.setAttribute("data-state", "closed");
            button.setAttribute("aria-expanded", "false");
            mainContent.setAttribute("aria-expanded", "false");
            if(banner){
                    banner.setAttribute("aria-expanded", "false");
                }
            first.setAttribute("aria-expanded", "false");
        }
    });

    // if scroll locked highlight the burger to prompt unlock
//     function isScrollLocked() {
//         return getComputedStyle(document.body).overflow === 'hidden';
//     }

//     function highlightHamburger() {
//         const hamburger = document.getElementById('hamImg');
//         if (hamburger) {
//             hamburger.classList.add('highlight-hamburger');
//             setTimeout(() => hamburger.classList.remove('highlight-hamburger'), 1000);
//         }
//     }

//     function handleScrollAttempt(e) {
//         if (isScrollLocked()) {
//             e.preventDefault();
//             highlightHamburger();
//         }
//     }

//     // Listen for scroll attempts
//     window.addEventListener('wheel', handleScrollAttempt, { passive: false });
//     window.addEventListener('touchmove', handleScrollAttempt, { passive: false });
//     window.addEventListener('keydown', (e) => {
//         const keys = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', ' '];
//         if (keys.includes(e.key) && isScrollLocked()) {
//             e.preventDefault();
//             highlightHamburger();
//         }
//     });