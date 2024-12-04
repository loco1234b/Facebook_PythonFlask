document.addEventListener("DOMContentLoaded", function () {
    const addStoryBtn = document.getElementById("addStoryBtn");
    const storyModal = document.getElementById("storyModal");
    const closeModal = document.querySelector(".modal .close");

    // Abrir modal
    addStoryBtn.addEventListener("click", () => {
        storyModal.style.display = "flex";
    });

    // Cerrar modal
    closeModal.addEventListener("click", () => {
        storyModal.style.display = "none";
    });

    // Cerrar modal al hacer clic fuera de él
    window.addEventListener("click", (e) => {
        if (e.target === storyModal) {
            storyModal.style.display = "none";
        }
    });
});