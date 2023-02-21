# Телеграм-бот и ВК-бот для викторин (вопрос/ответ)

Это чат боты ВК и телеграм, в которые загружаются викторины и
пользователь может проверить свои знания отвечая на вопросы.

## Примеры работы ботов:
### Телеграм бот

![max example](gifs/telegram.gif)

### ВК бот

![max example](gifs/VK.gif)


Работу бота можно посмотреть скачав телеграм бот 
```
https://t.me/Anikeev1Bot
```
Или написав в группу в ВК "Тестовая для Девмана"
```
https://vk.com/club214461314
```
## Запуск:

### 1. Копируем содержимое проекта себе в рабочую директорию
```
git clone <метод копирования>
```
У вас будет 2 рабочих файла:
- tg_quiz_bot.py - этот файл для работы с ТГ ботом
- vk_quiz_bot.py - это файл для работы с ВК

### 2. Устанавливаем библиотеки:
```
pip install -r requirements.txt
```

### 3. Для хранения переменных окружения создаем файл .env:
```
touch .env
```
Для тестирования телеграм-бота добавляем токен в `.env` файл: `TG_BOT_TOKEN='токен вашего бота'`

Для тестирования ВК-бота добавляем токен в `.env` файл: `VK_TOKEN='токен группы в ВК куда бот будет отправлять сообщения'`

### 4. Скачайте файл с викториной
Можно использовать викторины, которые лежат в `quiz_questios` или скачать свои [викторины](https://dvmn.org/media/modules_dist/quiz-questions.zip)


### 5. Запуск

```
python tg_quiz_bot.py  
```

По умолчанию будет загружена викторина `quiz-questions/1vs1200.txt`. Если необходима другая,
укажите это при запуске файла.
```
python tg_quiz_bot.py quiz-questions/1vs1500.txt
```

Для запуска бота для ВК нужно запустить `redis` на компьютере в Ubuntu
```pycon
$ sudo apt upgrade
$ sudo apt upgrade
$ sudo apt install redis-server
$ redis-server
```
А далее стандартно запустить файл с ВК ботом
```
python vk_quiz_bot.py quiz-questions/1vs1500.txt
```
## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
