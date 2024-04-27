var modal = document.getElementById("myModal");
var btns = document.querySelectorAll(".openModalBtn");
var span = document.getElementsByClassName("close")[0];

// Открытие модального окна при нажатии на любую кнопку
btns.forEach(function(btn) {
    btn.onclick = function() {
        modal.style.display = "flex";
    };
});

// Закрытие модального окна при нажатии на крестик
span.onclick = function() {
    modal.style.display = "none";
};

// Закрытие модального окна при клике за его пределами
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};
