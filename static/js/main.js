document.querySelectorAll(".book-cover img").forEach((image) => {
    const hideMissingCover = () => { image.hidden = true; };
    image.addEventListener("error", hideMissingCover);
    if (image.complete && !image.naturalWidth) hideMissingCover();
});

document.querySelectorAll("[data-loading-form]").forEach((form) => {
    const button = form.querySelector("button[data-busy-text]");
    const status = form.querySelector(".loading-status");
    form.addEventListener("submit", () => {
        button.disabled = true;
        button.textContent = button.dataset.busyText;
        form.setAttribute("aria-busy", "true");
        status.textContent = "Kitaplar değerlendiriliyor.";
    });
    window.addEventListener("pageshow", () => {
        button.disabled = false;
        button.textContent = button.dataset.idleText;
        form.removeAttribute("aria-busy");
        status.textContent = "";
    });
});
