function formatDate(dateString) {
    // Разделяем дату на части
    const [year, month, day] = dateString.split('-');
    // Возвращаем дату в формате день.месяц.год
    return `${day}.${month}.${year}`;
}

document.addEventListener('DOMContentLoaded', function() {
    const pagination = document.querySelector('.pagination');
    const itemsPerPage = 6;
    let currentPage = 1;

    // Функция для загрузки данных с сервера
    async function loadSermons(page) {
        try {
            // Замените URL на свой
            const response = await fetch(`/api/sermons/?page=${page}`);
            if (!response.ok) {
                throw new Error('Не удалось загрузить данные');
            }

            const data = await response.json();
            console.log(data)
            const sermonContainer = document.getElementById('sermons_all');
            sermonContainer.innerHTML = ''; // Очищаем контейнер для новых данных

            // Обрабатываем результаты
            data.items.forEach(sermon => {
                const sermonDiv = document.createElement('div');
                const videoId = sermon.video_url.includes('=') ? sermon.video_url.split('=')[1] : ''; // ID видео

                sermonDiv.classList.add('full-sermon-card');
                sermonDiv.innerHTML = `
                        <iframe
                            class="sermon-video"
                            src="https://www.youtube.com/embed/${videoId}"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowfullscreen>
                        </iframe>
                        <div class="sermon-meta">
                            <div class="sermon-date">${formatDate(sermon.date)}</div>
                            <h3>${sermon.title}</h3>
                            <p class="scripture-ref">${sermon.description}</p>
                            <p class="preacher">${sermon.autor}</p>
                        </div>
                `;

                sermonContainer.appendChild(sermonDiv);
            });

            updatePagination(page, data.count); // Обновляем пагинацию

        } catch (error) {
            console.error('Ошибка:', error);
            document.getElementById('sermons_all').innerHTML = '<p>Произошла ошибка при загрузке данных.</p>';
        }
    }

    // Функция для обновления пагинации
    function updatePagination(activePage, totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    pagination.innerHTML = '';

    // Кнопка "Назад"
    pagination.innerHTML += `
        <a class="page-item ${activePage === 1 ? 'disabled' : ''}" 
           data-page="${activePage - 1}">&laquo;</a>
    `;

    // Показываем первые 3 страницы
    for (let i = 1; i <= Math.min(3, totalPages); i++) {
        pagination.innerHTML += `
            <a class="page-item ${i === activePage ? 'active' : ''}" 
               data-page="${i}">${i}</a>
        `;
    }

    // Если всего больше 4 страниц, добавляем многоточие и последнюю страницу
    if (totalPages > 4) {
        // Добавляем "..." только если активная страница не одна из первых трёх или последняя
        if (activePage > 3 && activePage < totalPages) {
            pagination.innerHTML += `<span class="ellipsis">...</span>`;
        }

        // Если активная страница больше 3, показываем её
        if (activePage > 3 && activePage < totalPages) {
            pagination.innerHTML += `
                <a class="page-item active" data-page="${activePage}">${activePage}</a>
            `;
        }

        // Добавляем многоточие перед последней страницей, если активная страница далеко от конца
        if (activePage < totalPages - 1) {
            pagination.innerHTML += `<span class="ellipsis">...</span>`;
        }

        // Добавляем последнюю страницу
        pagination.innerHTML += `
            <a class="page-item ${activePage === totalPages ? 'active' : ''}" 
               data-page="${totalPages}">${totalPages}</a>
        `;
    }

    // Кнопка "Вперед"
    pagination.innerHTML += `
        <a class="page-item ${activePage === totalPages ? 'disabled' : ''}" 
           data-page="${activePage + 1}">&raquo;</a>
    `;

    // Назначение обработчиков для кнопок пагинации
    pagination.querySelectorAll('.page-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            if (!this.classList.contains('disabled')) {
                const page = parseInt(this.dataset.page);
                loadSermons(page); // Загружаем данные для выбранной страницы
            }
        });
    });
}


    // Инициализация первой страницы данных
    loadSermons(1);
});

