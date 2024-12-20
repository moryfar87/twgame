document.addEventListener('DOMContentLoaded', function() {
    const loginBtn = document.querySelector('.login-btn');
    const registerBtn = document.querySelector('.register-btn');
    const userInfo = document.querySelector('.user-info');
    const usernameSpan = document.querySelector('.username');
    const logoutBtn = document.querySelector('.logout-btn');

    function updateAuthDisplay() {
        const username = localStorage.getItem('username');
        if (username) {
            loginBtn.style.display = 'none';
            registerBtn.style.display = 'none';
            userInfo.style.display = 'inline-block';
            usernameSpan.textContent = username;
        } else {
            loginBtn.style.display = 'inline-block';
            registerBtn.style.display = 'inline-block';
            userInfo.style.display = 'none';
        }
    }

    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        localStorage.removeItem('username');
        localStorage.removeItem('email');
        localStorage.removeItem('password');
        updateAuthDisplay();
        window.location.href = 'index.html';
    });

    updateAuthDisplay();

    document.getElementById('createPostForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = localStorage.getItem('email');
        const password = localStorage.getItem('password');

        if (!email || !password) {
            document.getElementById('message').textContent = 'Пожалуйста, войдите в систему для создания поста.';
            document.getElementById('message').style.display = 'block';
            document.getElementById('message').className = 'message error';
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        const title = document.getElementById('post-title').value;
        const game = document.getElementById('post-game').value;
        const content_text = document.getElementById('post-content').value;

        const postData = { title, game, content_text };

        try {
            const response = await axios.post('http://localhost:8000/posts', postData, {
                auth: {
                    username: email,
                    password: password
                },
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });

            document.getElementById('message').textContent = 'Пост успешно создан!';
            document.getElementById('message').style.display = 'block';
            document.getElementById('message').className = 'message success';

            // Очистка формы
            document.getElementById('createPostForm').reset();

            // Перенаправление на главную страницу через 2 секунды
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);

        } catch (error) {
            let errorMessage = 'Произошла ошибка при создании поста.';
            if (error.response) {
                errorMessage = error.response.data.detail || errorMessage;
                if (error.response.status === 401) {
                    localStorage.removeItem('username');
                    localStorage.removeItem('email');
                    localStorage.removeItem('password');
                    errorMessage = 'Сессия истекла. Пожалуйста, войдите снова.';
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 2000);
                }
            }
            document.getElementById('message').textContent = errorMessage;
            document.getElementById('message').style.display = 'block';
            document.getElementById('message').className = 'message error';
        }
    });
});