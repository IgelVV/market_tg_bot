# Телеграм Бот для интеграции с Django приложением
## Установка

- Убедиться в соответствии моделей `UserModel`, `Shop`, 
`Storage`, используемых в целевом проекте, с моделями, 
используемыми в этом репозитории. При необходимости 
адаптировать соответствующие `services`. 
- Убедиться в существовании пользовательской группы `"telegram_admins"`. 
Добавить суперпользователя в эту группу.
- Добавить в настройки проекта константы указанные в 
.env.template 
- Установить зависимости
- Скопировать содержимое приложения `tg_bot` в проект и добавить в 
`installed_app`

## Описание
### Назначение
Приложение создано с целью расширения конкретного django проекта 
функционалом телеграм бота, для предоставления `Продавцам` 
возможности взаимодействовать со своим `Магазином` через 
удобный интерфейс.

### Структура 
Весь код связанный с ботом находится в приложении `tg_bot`.
В приложении `shop` находится код имитирующий поведение 
целевого проекта, он должен совпадать (в первую очередь модели). 
Так же в сервисах приложения бота находится `UserService`, отвечающий
за взаимодействие со стандартной моделью User. Если используется кастомный 
User, то необходима адаптация.

### tg_bot

- Запуск бота осуществляется через django команду: 
```bash 
python manage.py run_tg_bot
```
- `bot.py` является основным файлом, через него происходит
настройка и запуск бота

#### Handlers
- Основная коммуникация с пользователем происходит через 
`ConversationHandler`. Однако, из-за настройки
`per_message=True`, он может содержать только обработчики
основанные на коллбэках (`CallbackHandlers). Вследствие чего,
прочие обработчики располагаются отдельно(обработчики 
команд, и текста).
- Все текстовые сообщения обрабатываются одним 
`MessageHandler`, в зависимости от состояния, сохраняемого 
в `context.chat_data['expected_input']`. `text_message.dispatcher`
получает любое текстовое сообщение, если ожидается конкретное
сообщение (например пароль или api_key), то вызывается 
соответствующий обработчик, если нет, то дефолтный. 
Логика его работы похожа, на `ConversationHandler`, однако, смена 
состояний происходит через `context.chat_data['expected_input']`.
Такая логика позволила вынести из `main_conv` все обработчики
текста, и сделать его `per_message=True`. 
  - В процессе работы происходит следующее:
  В основном диалоге (основанном на коллбэках), обработчик запрашивает 
  у пользователя текстовый ввод, и выставляет `expected_input` в нужное
  значение. Пользователь отправляет текст, он обрабатывается 
  `text_message.dispatcher`, проверяется `expected_input` вызывается 
  другой обработчик для нужного типа инпута. Когда ввод больше не нужен
  `expected_input` выставляется равным `None`. Так же ввод может быть 
  отменен командой `/cancel`

- Бот имеет настройку 
`application.arbitrary_callback_data(True)`, что позволяет 
использовать python объекты как callback_data и приводит к 
некоторым ограничениям описанным в документации
`python-telegram-bot`. При перезапуске бота и при 
заполнении памяти выделенной на коллбэки, они устаревают. 
Чтобы обработать такой коллбэк, используется хэндлер:
```python
CallbackQueryHandler(invalid_button.handle_invalid_button,
                     pattern=InvalidCallbackData)
```

#### Services
- Основная логика взаимодействия с данными (моделями) 
содержится в `services`. Для каждой модели существует свой 
сервис, а так же отдельный сервис, для логики связанной 
с чатом, и для взаимодействия с `context.chat_data`.
  - Не предполагается взаимодействия обработчиков с 
  DjangoORM напрямую, исключительно через сервисы.

- `context.chat_data` используется как аналог сессии, для 
хранения временной информации о взаимодействии пользователя 
с ботом, такой как роль, текущий выбранный магазин, 
ожидаемый ввод с клавиатуры и тд. Взаимодействие с 
`chat_data` осуществляется только с помощью геттеров 
и сеттеров `ChatService`.

#### Authentication/Registration
- Регистрация для `Продавцов` и для `Админов` происходит по разному
  - для `Продавцов` проверяется `api_key` магазина, если введенный ключ 
  соответствует какому угодно магазину, то авторизация считается пройденной,
  создается запись о продавце в `TelegramUser` и привязывается к записи 
  магазина, ключ которого был введен. Т.е для успешной авторизации 
  пользователь должен заранее знать ключ от своего магазина, 
  и держать его в секрете.
  - для `Админа` проверяются `username` и `password` от записи в таблице 
  `User` django. Если это верные данные, и они соответствуют пользователю, 
  состоящему в группе `"telegram_admins"`, то пользователь считается 
  авторизованным как Админ. Создается запись о пользователе в той же таблице, 
  что и о продавце (`TelegramUser`), однако никакой магазин не привязывается
  к этой записи, так как админ имеет доступы ко всем магазинам. (если в 
  дальнейшем к записи Админа привяжутся какие-либо магазины, это ни на 
  что не повлияет). Обратите внимание, что запись в таблице `TelegramUser`
  не имеет связи с таблицей `User`, следовательно регистрироваться как админ
  можно с любого количества аккаунтов телеграм, используя django пользователя
  состоящего в группе `"telegram_admins"`.

#### Texts and Keyboards
- Текстовые статические данные, вынесены в `texts.py`, для
удобства изменения. Тексты хранятся как строки, некоторые 
из них, подразумевают форматирование, которое происходит 
в хэндлерах. Список текстов:
  - Описания команд
  - Описание бота
  - Все сообщения
  - Тексты ответов на коллбэки
  - ! Тексты клавиатур находятся в конструкторах клавиатур
  для удобства.

- В боте используются исключительно инлайн клавиатуры, 
они хранятся в `keyboards` в качестве функций 
конструкторов. Там же хранится текст отображаемый на кнопках.

#### Models
- Бот использует модель `TelegramUser`, которая предназначена 
для хранения информации о зарегистрированных пользователях.
Все пользователи делятся по ролям (admin, seller), и 
поведение бота зависит от роли.
- Регистрация происходит один раз при правильном вводе 
данных, соответственно роли. Для Продавца - это `api_key` 
магазина. Для админа - `username` и `password`, от его 
аккаунта в django приложении (`UserModel`). При регистрации
в базе данных создается запись о пользователе. В дальнейшем, 
при входе пользователя с этим telegram id ему будет 
предоставлен доступ в соответствии с правами. 
  - Возможно частично пройти регистрацию повторно, для этого
  предусмотрен флаг `is_logged_out` в модели `TelegramUser`.
  Если он установлен на `True` пользователь пройдет процедуру
  выбора роли и ввода проверочных данный, а в базе данных 
  его запись обновится, сохранив при этом `is_banned`, 
  `is_active` неизменными. Такая процедура повторного входа 
  может потребоваться для смены роли, или обновления данных о
  пользователе.
- `is_banned` отвечает за проверки связанные с баном, 
забаненный пользователь не может совершать никаких действий.
- `is_active` отвечает за проверки связанные с подписочной 
системой. Неактивный пользователь имеет ограниченный доступ,
как минимум, ему доступно продление подписки.
- `Админ` имеет доступ ко всем магазинам, и изначально не привязывается 
к конкретным магазинам.
- `Продавец` имеет доступ только к тем магазинам, которые он когда-либо 
привязывал, используя `api_key`. Изначально он привязывается к магазину,
`api_key` которого он указал при регистрации. Остальные магазины можно 
привязать/отвязать через меню пользователя в телеграм.

- Модель `Shop` отражает данные о магазине. Через бота пользователи получают 
возможность изменять поля у записей это модели, например `is_active`.
Эта модель привязывается к `TelegramUser` через Many-to-Many, а это значит 
у одного магазина может быть множество "продавцов", например продавец 
может иметь несколько телеграм аккаунтов (для каждого из которых будет 
создаваться свой `Продавец`), или он может передать ключ своему помощнику.
Причем у одного Продавца может быть доступ к нескольким магазинам, а у 
помощника, только к части, в зависимости от количества известных ему api_keys.
## Deploy 

```bash
docker run --rm --name tg_app -v ./market/database:/app/database -d -e "DJANGO_DEBUG=1" tg_market python manage.py run_tg_bot
```

```bash
docker run --rm --name tg_django -p 8000:8000 -d -e "DJANGO_DEBUG=1" tg_market python manage.py runserver 0.0.0.0:8000
```
##
##