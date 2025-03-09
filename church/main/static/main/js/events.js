// Ссылка на контейнер для данных
function formatDate(dateString) {
    // Разделяем дату на части
    const [year, month, day] = dateString.split('-');
    // Возвращаем дату в формате день.месяц.год
    return `${day}.${month}.${year}`;
}

document.addEventListener('DOMContentLoaded', async function() {
const eventsContainer = document.getElementById('events');
    if (!eventsContainer) {
        console.error('Элемент с id="events" не найден.');
        return;
    }
    try {
        // Отправляем GET-запрос на сервер для получения данных
        const response = await fetch('/api/events/');  // Замените на нужный URL API
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
            data.forEach(event => {
    const eventDiv = document.createElement('div');
    
    // Проверка, чтобы избежать ошибок при извлечении ID видео
    // Добавляем класс для div
    eventDiv.classList.add('events-calendar');
    let date_start = formatDate(event.date_start);
    let date_finish = event.date_finish
    if (event.date_finish) {
        date_start = date_start + ' -';
        date_finish = formatDate(date_finish)
    } else {
        date_finish = ''
    };
    const html = `
            <div class="card event-card">
                <div class="event-date">
                    <span class="day">${date_start}</span>
                    <span class="day">${date_finish}</span>
                </div>
                <div class="event-info">
                    <h3>${event.name}</h3>
                    <p>${event.description}<p>
                </div>
            </div>
    `;
    console.log(html);
    eventDiv.innerHTML = html;
    
    // Добавляем элемент на страницу
    eventsContainer.appendChild(eventDiv);
});

        } else {
            // Если данных нет
            eventsContainer.innerHTML = '<p>Нет проповедей для отображения.</p>';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        eventsContainer.innerHTML = '<p>Произошла ошибка при загрузке данных.</p>';
    }
})

// Загружаем данные при первоначальной загрузке страницы
//window.addEventListener('DOMContentLoaded', loadSermons_3);
