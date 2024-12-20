    document.addEventListener('DOMContentLoaded', () => {
        const themeToggle = document.getElementById('theme-toggle');
        const icon = themeToggle.querySelector('i');
    
        // Проверяем предпочтения системы
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
        // Получаем сохраненную тему или используем системные предпочтения
        const currentTheme = localStorage.getItem('theme') ||
                            (prefersDarkScheme.matches ? 'dark' : 'light');
    
        // Устанавливаем начальную тему
        setTheme(currentTheme);
    
        // Обработчик клика по кнопке
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    
        // Функция установки темы
        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
    
            // Обновляем иконку
            if (theme === 'dark') {
                icon.classList.replace('fa-moon', 'fa-sun');
                themeToggle.setAttribute('title', 'Switch to light mode');
            } else {
                icon.classList.replace('fa-sun', 'fa-moon');
                themeToggle.setAttribute('title', 'Switch to dark mode');
            }
    
            // Добавляем анимацию при переключении
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    
            // Вызываем пользовательское событие для оповещения других скриптов
            const event = new CustomEvent('themeChanged', { detail: { theme } });
            document.dispatchEvent(event);
        }
    
        // Слушаем изменения системных предпочтений
        prefersDarkScheme.addListener((e) => {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    });
    
        