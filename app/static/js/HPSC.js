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

    //to main body arrow functionality
    toBodyArrow = document.getElementById("toBodyArrow");
    if (toBodyArrow) {
        $main = document.getElementById("main");

        toBodyArrow.addEventListener("click", (e) => {
            e.preventDefault();
            $main.scrollIntoView({ behavior: 'smooth' });
            setTimeout(() => {
                document.activeElement.blur();
            }, 700); // after scroll finishes
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
        // Parallax: adjust the 0.5 for more/less effect
        const scrolled = window.scrollY * 0.1;
        banner.style.backgroundPosition = `45% calc(50% + ${scrolled}px)`;
    });


});





