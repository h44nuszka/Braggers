document.addEventListener("DOMContentLoaded", function() {
    const popup = document.getElementById("popup");
    const openPopupButton = document.getElementById("openPopup");
    const closePopupButton = document.getElementById("closePopup");

    // Open popup
    openPopupButton.addEventListener("click", function() {
        popup.style.display = "flex"; // Use flex to align with updated CSS
    });

    // Close popup
    closePopupButton.addEventListener("click", function() {
        popup.style.display = "none";
    });

    // Close popup if clicking outside the content
    window.addEventListener("click", function(event) {
        if (event.target === popup) {
            popup.style.display = "none";
        }
    });

    // Slideshow functions
    var slideIndex = 1;
    showSlides(slideIndex);

    function plusSlides(n) {
        showSlides(slideIndex += n);
    }

    function currentSlide(n) {
        showSlides(slideIndex = n);
    }

    function showSlides(n) {
        var slides = document.getElementsByClassName("mySlides");
        var captions = document.getElementsByClassName("caption-container");
        var dots = document.getElementsByClassName("demo");
        var captionText = document.getElementById("caption");

        if (slides.length === 0) return; // Avoid errors if no slides are present

        if (n > slides.length) { slideIndex = 1; }
        if (n < 1) { slideIndex = slides.length; }

        // Hide all slides and captions
        for (var i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
        }
        for (var i = 0; i < captions.length; i++) {
            captions[i].style.display = "none";
        }

        // Show the current slide and caption
        slides[slideIndex - 1].style.display = "block";
        if (captions.length > 0) {
            captions[slideIndex - 1].style.display = "block";
        }

        // Optional: Update dots if present
        if (dots.length > 0) {
            for (var i = 0; i < dots.length; i++) {
                dots[i].className = dots[i].className.replace(" active", "");
            }
            if (dots[slideIndex - 1]) {
                dots[slideIndex - 1].className += " active";
            }
        }

        // Update caption text
        if (captionText) {
            captionText.innerHTML = slides[slideIndex - 1].alt;
        }
    }
});
