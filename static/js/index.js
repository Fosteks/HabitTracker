var btns = document.querySelectorAll(".openModalBtn");

btns.forEach(function(btn) {
    btn.onclick = function() {
        var modalId = "myModal" + btn.getAttribute("name").substring(5); // Получаем `id` нужного модального окна
        var modal = document.getElementById(modalId);
        modal.style.display = "flex";

        // Добавляем обработчики закрытия внутри кнопки, чтобы они работали с правильным модальным окном
        var span = modal.querySelector(".close");
        span.onclick = function() {
            modal.style.display = "none";
        };

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };
    };
});
