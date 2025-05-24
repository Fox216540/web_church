// Ссылка на контейнер для данных
document.addEventListener('DOMContentLoaded', async function() {
const sermonsContainer = document.getElementById('3_sermons');
    if (!sermonsContainer) {
        console.error('Элемент с id="sermon-grid" не найден.');
        return;
    }
    try {
        // Отправляем GET-запрос на сервер для получения данных
        const response = await fetch('/api/lates_3_sermons/');  // Замените на нужный URL API
        // Проверяем, успешен ли запрос
        if (!response.ok) {
            throw new Error('Не удалось загрузить данные');
        }

        // Преобразуем ответ в JSON
        const data = await response.json();
        console.log(data);
        // Проверяем, есть ли данные
        if (data.length > 0) {
            // Перебираем полученные данные и выводим их на страницу
            data.forEach(sermon => {
    const sermonDiv = document.createElement('div');
    
    // Проверка, чтобы избежать ошибок при извлечении ID видео
    const videoUrl = sermon.video_url;
    const videoId = videoUrl.includes('=') ? videoUrl.split('=')[1] : ''; // Получаем ID только если есть "="

    // Добавляем класс для div
    sermonDiv.classList.add('sermon-card');
    const html = `
        <a href="${videoUrl}" target="_blank" class="video-thumbnail">
            <img src="https://img.youtube.com/vi/${videoId}/maxresdefault.jpg" alt="Проповедь">
            <div class="play-overlay">
                <i class="fab fa-youtube"></i>
            </div>
        </a>
        <div class="sermon-info">
            <h3>${sermon.title}</h3>
            <div class="meta">
                <p class="scripture-ref">${sermon.description}</p>
                <div class="pastor">
                    <i class="fas fa-user"></i> ${sermon.autor}</div>
            </div>
        </div>
    `;
    console.log(html);
    sermonDiv.innerHTML = html;
    
    // Добавляем элемент на страницу
    sermonsContainer.appendChild(sermonDiv);
});

        } else {
            // Если данных нет
            sermonsContainer.innerHTML = '<p>Нет проповедей для отображения.</p>';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        sermonsContainer.innerHTML = '<p>Произошла ошибка при загрузке данных.</p>';
    }
})

// Загружаем данные при первоначальной загрузке страницы
//window.addEventListener('DOMContentLoaded', loadSermons_3);
