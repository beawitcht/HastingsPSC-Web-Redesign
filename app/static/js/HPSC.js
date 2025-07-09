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

    let newsletterShown = 3;
    let articleShown = 3;
    const BATCH_SIZE = 3;

    // load more newsletters
    const cards = document.querySelectorAll('.newsletter-card');
    const loadMoreBtn = document.getElementById('load-more-btn');

    loadMoreBtn.addEventListener('click', () => {
        const nextBatch = Array.from(cards).slice(newsletterShown, newsletterShown + BATCH_SIZE);

        nextBatch.forEach(card => {
            card.classList.remove('hidden');

            const img = card.querySelector('img[data-src]');
            if (img) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            }
        });

        newsletterShown += nextBatch.length;

        if (newsletterShown >= cards.length) {
            loadMoreBtn.style.display = 'none';
        }
    });

    // load more articles
    const articleCards = document.querySelectorAll('.article-card');
    const loadMoreBtnArticle = document.getElementById('load-more-btn-article');


    loadMoreBtnArticle.addEventListener('click', () => {
        const nextBatch = Array.from(articleCards).slice(articleShown, articleShown + BATCH_SIZE);

        nextBatch.forEach(card => {
            card.classList.remove('hidden');

            const img = card.querySelector('img[data-src]');
            if (img) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            }
        });

        articleShown += nextBatch.length;

        if (articleShown >= articleCards.length) {
            loadMoreBtnArticle.style.display = 'none';
        }
    });

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
        if (window.innerWidth < 778) return;
        const parallaxStart = 0;
        const parallaxFactor = 0.03;
        let scrolled = 0;
        if (window.scrollY > parallaxStart) {
            scrolled = (window.scrollY - parallaxStart) * parallaxFactor;
        }
        banner.style.backgroundPosition = `50% calc(120px + ${scrolled}px)`;
    });

});





