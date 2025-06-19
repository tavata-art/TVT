# Tavata CMS 🐝

A modern, robust, and multilingual Content Management System built with Python and Django. This project is a comprehensive case study on building a feature-rich web application from the ground up, focusing on clean architecture, best practices, and scalability.

![Tavata CMS Screenshot](link-to-a-cool-screenshot-of-your-app.png) 
<!-- TODO: Add a nice screenshot of the homepage or blog list here! -->

---

## ✨ Features

Tavata CMS is not just a simple blog. It's a powerful platform designed with a professional feature set:

*   **Dual Content Types:**
    *   **Static Pages:** For "evergreen" content like "About Us" or "Terms and Conditions".
    *   **Blog Posts:** A complete, time-based blogging engine.
*   **Rich Content Editing:** Powered by **django-summernote**, providing a beautiful WYSIWYG editing experience.
*   **Dynamic, Configurable Widgets:**
    *   Build and place widgets (Recent Posts, Most Viewed, Categories, etc.) in different "zones" (e.g., sidebars) directly from the admin panel.
    *   Widget behavior (like item count) is configurable.
*   **Full Internationalization (i18n):**
    *   Supports English, Spanish, and Catalan out-of-the-box.
    *   Translates everything: database content (using `django-modeltranslation`), interface text (`.po` files), and URLs.
*   **User & Profile Management:**
    *   Complete user authentication flow (Login, Logout, Signup).
    *   Extended user profiles with custom avatars and biographical information.
*   **Interactive Comment System:**
    *   Nested (threaded) comments with reply functionality, powered by `django-mptt`.
    *   Admin-configurable comment moderation (auto-approve or manual).
*   **Advanced Navigation:**
    *   Fully database-driven menu system. Administrators can build and reorder multiple menus (e.g., main navigation, footer links, social links) via the admin.
*   **Global Site Configuration:**
    *   A central settings panel (using `django-solo`) to manage site-wide parameters like pagination, caching timeouts, and branding without touching the code.
*   **Performance-Oriented:**
    *   A configurable caching system for widgets and menus to reduce database load.
    *   Pagination implemented on all content lists.
*   **SEO Ready:** All content types include fields for custom Meta Titles and Meta Descriptions.

---

## 🛠️ Tech Stack

This project is built with a modern and robust stack:
*   **Backend:** Python 3.11, Django 5.2
*   **Database:** SQLite (for development), MySQL (for production)
*   **Frontend:** Bootstrap 5, FontAwesome
*   **Key Django Libraries:**
    *   `django-modeltranslation` for database content translation.
    *   `django-summernote` for WYSIWYG editing.
    *   `django-mptt` for hierarchical data (comments).
    *   `django-solo` for singleton configuration models.
    *   `python-decouple` for managing environment settings.

---

## 🚀 Getting Started

Instructions on how to set up and run a local instance of this project.

### Prerequisites

*   Python 3.11+
*   `pip` and `venv`
*   GNU gettext (for internationalization commands)
    *   On Debian/Ubuntu: `sudo apt install gettext`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tavata-art/tvt-cms.git # Replace with your actual repo URL
    cd tavata-cms
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up the environment variables:**
    *   Copy the `.env.example` file to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and set `SECRET_KEY` to a new, unique value.

5.  **Run the database migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The site will now be available at `http://127.0.0.1:8000/`.

---

## 🏛️ Architecture & Philosophy

This project was built with a few key principles in mind:
*   **Modularity:** Each distinct piece of functionality (blog, pages, widgets) is encapsulated in its own Django app.
*   **Configuration over Code:** Empowering the site administrator to control as much as possible (menus, widgets, settings) from the admin panel without needing developer intervention.
*   **Cleanliness and Best Practices:** Adhering to Django's design philosophies, internationalization standards, and professional development workflows (e.g., using Git branches for features).

<!--
## 🤝 Contributing

(Optional) If you ever make this open-source, you can add contribution guidelines here.
-->

## 🐝 About the Authors

This project was collaboratively developed by **Gustavo** and his AI colleague, **MSc. Tavata**.
