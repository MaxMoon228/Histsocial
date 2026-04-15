SOURCE_TYPE_CHOICES = [
    ("external_education", "Внешний образовательный"),
    ("external_library", "Внешняя библиотека"),
    ("external_testing", "Внешнее тестирование"),
    ("external_calendar", "Внешний календарь"),
    ("internal_file", "Внутренний файл"),
]

TAG_TYPE_CHOICES = [
    ("topic", "Тема"),
    ("era", "Эпоха"),
    ("region", "Регион"),
    ("period", "Период"),
    ("format", "Формат"),
    ("level", "Уровень"),
    ("event_type", "Тип события"),
    ("exam_type", "Тип экзамена"),
    ("scope", "Область"),
]

SECTION_CHOICES = [("world", "Всеобщая история"), ("russia", "История России"), ("social", "Обществознание")]

MATERIAL_KIND_CHOICES = [
    ("textbook", "Учебник"),
    ("lesson", "Урок"),
    ("presentation", "Презентация"),
    ("collection", "Коллекция"),
    ("pdf", "PDF"),
    ("video", "Видео"),
    ("image", "Изображение"),
    ("article", "Статья"),
    ("archive", "Архив"),
]

LEVEL_CHOICES = [
    ("school_basic", "Школьный базовый"),
    ("advanced", "Продвинутый"),
    ("exam", "Экзамен"),
    ("general", "Общий"),
]

LINK_PRIORITY_CHOICES = [
    ("external", "Внешняя ссылка"),
    ("file", "Локальный файл"),
]

ATTACHMENT_KIND_CHOICES = [
    ("pdf", "PDF"),
    ("ppt", "PPT"),
    ("pptx", "PPTX"),
    ("image", "Изображение"),
    ("video", "Видео"),
    ("audio", "Аудио"),
    ("archive", "Архив"),
    ("other", "Другое"),
]

EXAM_TYPE_CHOICES = [
    ("ege", "ЕГЭ"),
    ("oge", "ОГЭ"),
    ("school_trainer", "Школьный тренажер"),
    ("control", "Контроль знаний"),
    ("exam", "Экзамен"),
]

TASK_TYPE_CHOICES = [
    ("dates", "Даты"),
    ("chronology", "Хронология"),
    ("sources", "Источники"),
    ("maps", "Карты"),
    ("persons", "Личности"),
    ("reforms", "Реформы"),
    ("wars", "Войны"),
    ("terms", "Термины"),
    ("mixed", "Смешанный"),
]

DIFFICULTY_CHOICES = [("basic", "Базовый"), ("medium", "Средний"), ("hard", "Сложный")]

EVENT_TYPE_CHOICES = [
    ("war", "Война"),
    ("birth", "Рождение"),
    ("death", "Смерть"),
    ("reform", "Реформа"),
    ("treaty", "Договор"),
    ("culture", "Культура"),
    ("discovery", "Открытие"),
    ("holiday", "Праздник"),
    ("other", "Другое"),
]

SCOPE_CHOICES = [("russia", "Россия"), ("world", "Мир"), ("both", "Все")]

SCALE_CHOICES = [("year", "Год"), ("decade", "Десятилетие"), ("century", "Век"), ("era", "Эпоха")]
