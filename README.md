<div align="center">

# ☪️ HalalMarket

### Онлайн-маркетплейс халяльных товаров

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-REST_API-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)

<br/>

> 🌙 Покупай и продавай с уверенностью — только сертифицированные халяльные товары

</div>

---

## 📌 О проекте

**HalalMarket** — это современная платформа для покупки и продажи халяльных товаров. Проект предоставляет удобный REST API для управления каталогом продуктов, заказами и пользователями, обеспечивая прозрачность и доверие в каждой сделке.

---

## ✨ Возможности

- 🛒 Каталог товаров с категориями и фильтрацией
- 🔍 Поиск по продуктам и продавцам
- 👤 Регистрация покупателей и продавцов
- 📦 Управление заказами
- ⭐ Рейтинг и отзывы на товары
- 🔐 JWT-аутентификация
- 🐳 Полная контейнеризация с Docker
- 🚀 Автоматический деплой через GitHub Actions

---

## 🛠️ Технологический стек

| Слой             | Технология                        |
|------------------|-----------------------------------|
| Backend          | Python 3.11+, Django 4.x          |
| API              | Django REST Framework             |
| Аутентификация   | JWT (SimpleJWT)                   |
| Контейнеризация  | Docker, Docker Compose            |
| CI/CD            | GitHub Actions                    |
| IDE              | PyCharm / VS Code                 |

---

## 🚀 Быстрый старт

### Предварительные требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Установка и запуск

```bash
# 1. Клонируй репозиторий
git clone https://github.com/KadyrovErjan/HalalMarket.git
cd HalalMarket

# 2. Создай файл переменных окружения
cp .env.example .env
# Отредактируй .env под свои настройки

# 3. Запусти контейнеры
docker compose up -d --build

# 4. Примени миграции
docker compose exec web python manage.py migrate

# 5. Создай суперпользователя
docker compose exec web python manage.py createsuperuser

# 6. (Опционально) Загрузи тестовые данные
docker compose exec web python manage.py loaddata fixtures/products.json
```

🌐 Приложение: **http://localhost:8000**  
🔧 Панель администратора: **http://localhost:8000/admin**  
📖 Swagger docs: **http://localhost:8000/api/schema/swagger-ui/**

---

## ⚙️ Переменные окружения

Создай файл `.env` в корне проекта:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=halalmarket_db
POSTGRES_USER=halalmarket_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 📡 API Endpoints

### 🛍️ Товары

| Метод    | URL                              | Описание                      |
|----------|----------------------------------|-------------------------------|
| `GET`    | `/api/products/`                 | Список всех товаров           |
| `POST`   | `/api/products/`                 | Добавить товар                |
| `GET`    | `/api/products/{id}/`            | Детали товара                 |
| `PUT`    | `/api/products/{id}/`            | Обновить товар                |
| `DELETE` | `/api/products/{id}/`            | Удалить товар                 |
| `GET`    | `/api/categories/`               | Список категорий              |

### 📦 Заказы

| Метод    | URL                              | Описание                      |
|----------|----------------------------------|-------------------------------|
| `GET`    | `/api/orders/`                   | Мои заказы                    |
| `POST`   | `/api/orders/`                   | Создать заказ                 |
| `GET`    | `/api/orders/{id}/`              | Детали заказа                 |

### 👤 Пользователи

| Метод    | URL                              | Описание                      |
|----------|----------------------------------|-------------------------------|
| `POST`   | `/api/auth/register/`            | Регистрация                   |
| `POST`   | `/api/auth/token/`               | Получить JWT токен            |
| `POST`   | `/api/auth/token/refresh/`       | Обновить токен                |

---

## 📁 Структура проекта

```
HalalMarket/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD пайплайны
├── .idea/                  # Настройки IDE
├── mysite/
│   ├── manage.py
│   ├── mysite/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── products/       # Товары и категории
│       ├── orders/         # Заказы
│       └── users/          # Пользователи и аутентификация
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🔄 CI/CD Pipeline

Проект оснащён автоматическим деплоем через **GitHub Actions**:

```
push / pull_request
       │
       ▼
  ✅ Lint & Tests
       │
       ▼
  🐳 Docker Build
       │
       ▼
  🚀 Deploy (master branch)
```

---

## 🧪 Запуск тестов

```bash
# Запуск всех тестов
docker compose exec web python manage.py test

# С покрытием кода
docker compose exec web coverage run manage.py test
docker compose exec web coverage report
```

---

## 👤 Автор

**Erjan Kadyrov**

[![GitHub](https://img.shields.io/badge/GitHub-KadyrovErjan-181717?style=for-the-badge&logo=github)](https://github.com/KadyrovErjan)

---

<div align="center">

**☪️ Сделано с уважением к традициям и современным технологиям**

</div>
