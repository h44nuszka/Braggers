$(document).ready(function () {
    $('#addLanguageBtn').click(function () {
        var $secondLanguage = $('#secondLanguage');
        var $removeLanguageBtn = $('#removeLanguageBtn');

        if ($secondLanguage.is(':visible')) {
            $secondLanguage.hide();
            $secondLanguage.prop('required', false);
            $secondLanguage.val(''); // Clear the value if hidden
            $removeLanguageBtn.hide();
        } else {
            $secondLanguage.show();
            $secondLanguage.prop('required', true);
            $removeLanguageBtn.show();
        }
    });
    $('#removeLanguageBtn').click(function () {
        var $secondLanguage = $('#secondLanguage');
        $secondLanguage.hide();
        $secondLanguage.prop('required', false);
        $secondLanguage.val(''); // Clear the value if hidden
        $(this).hide(); // Hide the close button
    });
    $('form').on('submit', function (event) {
        var $secondLanguage = $('#secondLanguage');
        if (!$secondLanguage.is(':visible')) {
            $secondLanguage.val(''); // Ensure the value is empty if hidden
        }
    });
    });


    $(document).ready(function () {
    // Funkcja do inicjalizacji CKEditor dla wielu elementów
    function initializeCKEditors() {
        var ids = ['menuItem2desc_l2', 'menuItem3desc_l2', 'menuItem4desc_l2'];
        ids.forEach(function(id) {
            if (document.getElementById(id)) {
                CKEDITOR.replace(id);
            }
        });
    }

    // Funkcja do niszczenia CKEditor dla wielu elementów
    function destroyCKEditors() {
        var ids = ['menuItem2desc_l2', 'menuItem3desc_l2', 'menuItem4desc_l2'];
        ids.forEach(function(id) {
            if (CKEDITOR.instances[id]) {
                CKEDITOR.instances[id].destroy();
            }
            $('#' + id).hide();
        });
    }

    // Funkcja do aktualizacji widoczności elementu warunkowego
    function updateConditionalElementVisibility() {
        var $secondLanguage = $('#secondLanguage');
        var $conditionalElement = $('.sec-lang-hide');

        // Sprawdź, czy drugi język jest ustawiony i widoczny
        if ($secondLanguage.is(':visible') && $secondLanguage.val()) {
            $conditionalElement.show();
            initializeCKEditors();
        } else {
            $conditionalElement.hide();
            destroyCKEditors();
        }
    }

    // Wywołaj funkcję po załadowaniu strony
    updateConditionalElementVisibility();

    // Wywołaj funkcję po kliknięciu przycisku dodawania drugiego języka
    $('#addLanguageBtn').click(function () {
        var $secondLanguage = $('#secondLanguage');
        $secondLanguage.show();
        $secondLanguage.prop('required', true);
        updateConditionalElementVisibility();
    });

    // Wywołaj funkcję po kliknięciu przycisku usuwania drugiego języka
    $('#removeLanguageBtn').click(function () {
        var $secondLanguage = $('#secondLanguage');
        $secondLanguage.hide();
        $secondLanguage.prop('required', false);
        $secondLanguage.val(''); // Wyczyść wartość pola
        updateConditionalElementVisibility();
    });
    // Wywołaj funkcję przed wysłaniem formularza, aby upewnić się, że widoczność jest aktualna
    $('form').on('submit', function () {
        var $secondLanguage = $('#secondLanguage');
        if (!$secondLanguage.is(':visible')) {
            $secondLanguage.val(''); // Upewnij się, że wartość jest pusta, jeśli ukryta
        }
        updateConditionalElementVisibility(); // Aktualizuj widoczność elementów warunkowych
    });

    CKEDITOR.replace('description2');
    CKEDITOR.replace('description3');
    CKEDITOR.replace('description4');

    });