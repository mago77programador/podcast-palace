// js.js
function hideDivs(clickedIndex) {
    const divs = document.getElementsByClassName("div-box");
    for (let i = 0; i < divs.length; i++) {
        if (i !== clickedIndex) {
            divs[i].classList.add("div_hidden");
        }
    }
}

// Assign Event Listeners to the right elements
document.addEventListener("DOMContentLoaded", function () {
    const divBoxes = document.getElementsByClassName("div-box");
    for (let i = 0; i < divBoxes.length; i++) {
        divBoxes[i].addEventListener("click", function () {
            hideDivs(i);
        });
    }

    const reloadButton = document.querySelector("#reload input[type='button']");
    reloadButton.addEventListener("click", function () {
        window.location.reload();
    });
});