const body = document.body; 
        const themeToggle = document.getElementById('themeToggle'); 
 
        // Функция для установки темы 
        function setTheme(theme) { 
            if (theme === 'dark') { 
                body.classList.remove('light-theme'); 
                body.classList.add('dark-theme'); 
            } else { 
                body.classList.remove('dark-theme'); 
                body.classList.add('light-theme'); 
            } 
            localStorage.setItem('theme', theme); 
        } 
 
        // Проверяем сохраненную тему при загрузке страницы 
        const savedTheme = localStorage.getItem('theme'); 
        if (savedTheme) { 
            setTheme(savedTheme); 
        } else { 
            setTheme('light'); // По умолчанию светлая тема 
        } 
 
        // Обработчик клика по кнопке 
        themeToggle.addEventListener('click', () => { 
            const currentTheme = body.classList.contains('dark-theme') ? 'dark' : 'light'; 
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark'; 
            setTheme(newTheme); 
        });