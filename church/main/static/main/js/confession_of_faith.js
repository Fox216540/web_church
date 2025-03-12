function closeAccordion(item) {
  item.classList.remove('active');
  item.querySelector('.icon').textContent = '▼';
}

function toggleAccordion(event) {
  const header = event.currentTarget;
  const item = header.parentElement;
  const wasActive = item.classList.contains('active');

  // Закрываем все sibling-элементы
  const parentContent = item.parentElement;
  if (parentContent.classList.contains('confession-content')) {
    parentContent.querySelectorAll('.confession-item').forEach(sibling => {
      if (sibling !== item) {
        closeAccordion(sibling);
      }
    });
  }

  // Закрываем все вложенные элементы, если текущий элемент закрывается
  if (wasActive) {
    item.querySelectorAll('.confession-item').forEach(subItem => {
      closeAccordion(subItem);
    });
  }

  // Переключаем состояние текущего элемента
  item.classList.toggle('active');
  header.querySelector('.icon').textContent = item.classList.contains('active') ? '▲' : '▼';
  event.stopPropagation();
}

// Инициализация аккордеона
document.querySelectorAll('.confession-header').forEach(header => {
  header.addEventListener('click', toggleAccordion);
});