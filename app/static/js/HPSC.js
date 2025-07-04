//back to top button functionality
document.addEventListener("DOMContentLoaded", function () {
    var backToTop = document.getElementById("backToTop");

    function scrollDetected() {
        if (backToTop) {
            if (document.body.scrollTop > 120 || document.documentElement.scrollTop > 120) {
                backToTop.style.display = "block";
            } else {
                backToTop.style.display = "none";
            }
        }
    }

    window.onscroll = function () { scrollDetected() };

    if (backToTop) {
        backToTop.addEventListener("click", () => {
            document.documentElement.scrollTo({ top: 0, behavior: 'smooth' });
            setTimeout(function () {
                document.getElementById("homeLogo").focus();
            }, 500);
        });
    }

    //to main body arrow functionality - not using anymore keeping for the time being
    // toBodyArrow = document.getElementById("toBodyArrow");
    // if (toBodyArrow) {
    //     main = document.getElementById("main");

    //     toBodyArrow.addEventListener("click", (e) => {
    //         e.preventDefault();
    //         main.scrollIntoView({ behavior: 'smooth' });
    //         setTimeout(() => {
    //             document.activeElement.blur();
    //         }, 700); // after scroll finishes
    //     });
    // }
    // to main accessibility functionality

    const skipToMain = document.getElementById("skipToMain");
    const main = document.getElementById("main");
    if (skipToMain && main) {
        skipToMain.addEventListener("click", function (e) {
            e.preventDefault();
            main.scrollIntoView({ behavior: "smooth" });
            main.setAttribute("tabindex", "-1"); // for accessibility focus
            main.focus({ preventScroll: true });
        });
    }

    // intersection observer for slide-up animation

    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                } else {
                    entry.target.classList.remove('in-view');
                }
            });
        },
        { threshold: 0.15 }
    );

    document.querySelectorAll('.animate-slide-up').forEach(el => {
        observer.observe(el);
    });


    document.addEventListener("scroll", function () {
        const banner = document.querySelector('.banner');
        if (!banner) return;
        const parallaxStart = 0;
        const parallaxFactor = 0.03;
        let scrolled = 0;
        if (window.scrollY > parallaxStart) {
            scrolled = (window.scrollY - parallaxStart) * parallaxFactor;
        }
        banner.style.backgroundPosition = `50% calc(120px + ${scrolled}px)`;
    });


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
                banner.setAttribute("aria-expanded", "true");
                first.setAttribute("aria-expanded", "true");
            }, 1); // 1ms delay to switch to transition animation


        } else {
            navMenu.setAttribute("aria-expanded", "false");
            button.setAttribute("data-state", "closed");
            button.setAttribute("aria-expanded", "false");
            mainContent.setAttribute("aria-expanded", "false");
            banner.setAttribute("aria-expanded", "false");
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



});





