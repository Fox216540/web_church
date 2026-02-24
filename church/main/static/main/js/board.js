document.addEventListener("DOMContentLoaded", () => {

    const DEFAULT_PHOTO = "/static/main/img/default-person.png";

    const modal = document.getElementById("modal");
    const modalClose = document.getElementById("modalClose");

    const modalImg = document.getElementById("modalImg");
    const modalName = document.getElementById("modalName");
    const modalRole = document.getElementById("modalRole");
    const modalDesc = document.getElementById("modalDesc");

    const modalPhone = document.getElementById("modalPhone");
    const modalEmail = document.getElementById("modalEmail");
    const modalTelegram = document.getElementById("modalTelegram");

    const teamGrid = document.getElementById("teamGrid");

		function openModal(person) {
		    modal.classList.add("active");

		    const scrollBarWidth = window.innerWidth - document.documentElement.clientWidth;

		    document.body.style.overflow = "hidden";

		    // добавляем компенсацию только если есть скроллбар
		    if (scrollBarWidth > 0) {
		        document.body.style.paddingRight = scrollBarWidth + "px";
		    }

		    modalImg.src = person.photo || DEFAULT_PHOTO;
		    modalImg.onerror = () => modalImg.src = DEFAULT_PHOTO;

		    modalName.textContent = person.name;
		    modalRole.textContent = person.role;
		    modalDesc.textContent = person.short_bio || "";

		    modalPhone.textContent = person.phone ? `Телефон: ${person.phone}` : "";
		    modalEmail.textContent = person.email ? `Email: ${person.email}` : "";
		    modalTelegram.textContent = person.telegram ? `Telegram: ${person.telegram}` : "";
		}

		function closeModal() {
		    modal.classList.remove("active");
		    document.body.style.overflow = "";
		    document.body.style.paddingRight = "";
		}

    modalClose.addEventListener("click", closeModal);

    modal.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeModal();
    });

    fetch("/api/church-board/")
        .then(r => r.json())
        .then(data => {
            teamGrid.innerHTML = "";

            data.forEach(person => {

                const card = document.createElement("div");
                card.className = "person-card";

                card.innerHTML = `
                    <img src="${person.photo || DEFAULT_PHOTO}" 
                         onerror="this.src='${DEFAULT_PHOTO}'">
                    <div class="person-info">
                        <h3>${person.name}</h3>
                        <p class="role">${person.role}</p>
                    </div>
                `;

                card.addEventListener("click", () => openModal(person));

                teamGrid.appendChild(card);
            });
        })
        .catch(err => console.error("Ошибка загрузки:", err));
});