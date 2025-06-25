//Back to top button functionality
window.onscroll = function () { scrollDetected() };
backToTop = document.getElementById("backToTop");

backToTop.addEventListener("click", () => {
  document.documentElement.scrollTo({ top: 0, behavior: 'smooth' });
});

function scrollDetected() {
  if (document.body.scrollTop > 120 || document.documentElement.scrollTop > 120) {
    document.getElementById("backToTop").style.display = "block";
  } else {
    document.getElementById("backToTop").style.display = "none";
  }
}
