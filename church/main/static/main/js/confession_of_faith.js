// Общие скрипты из второго файла
        const menuToggle = document.querySelector('.menu-toggle');
        const navLinks = document.querySelector('.nav-links');

        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });

        // Скрипт для аккордеона
        function toggleAccordion(event) {
            const header = event.currentTarget;
            const item = header.parentElement;
            const wasActive = item.classList.contains('active');

            const parentContent = item.parentElement;
            if (parentContent.classList.contains('confession-content')) {
                parentContent.querySelectorAll('.confession-item').forEach(sibling => {
                    if (sibling !== item) {
                        sibling.classList.remove('active');
                        sibling.querySelector('.icon').textContent = '▼';
                        sibling.querySelectorAll('.confession-item').forEach(sub => {
                            sub.classList.remove('active');
                            sub.querySelector('.icon').textContent = '▼';
                        });
                    }
                });
            }

            if (wasActive) {
                item.querySelectorAll('.confession-item').forEach(subItem => {
                    subItem.classList.remove('active');
                    subItem.querySelector('.icon').textContent = '▼';
                });
            }

            item.classList.toggle('active');
            header.querySelector('.icon').textContent = item.classList.contains('active') ? '▲' : '▼';
            event.stopPropagation();
        }

        document.querySelectorAll('.confession-item').forEach(item => {
            item.classList.remove('active');
        });