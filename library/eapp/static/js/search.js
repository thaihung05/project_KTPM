document.querySelector('form').onsubmit = function() {
    let kwInput = this.querySelector('input[name="kw"]');
    let categoryInput = this.querySelector('input[name="category_id"]');

    if (kwInput.value.trim() === "" && categoryInput) {
        categoryInput.disabled = true;
    }
};