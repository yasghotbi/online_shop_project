Django Online Shop

A modular e-commerce platform built with Django, supporting customers, vendors, and admin roles. Users can browse products, add to cart, place orders, and manage their accounts. Vendors manage their stores, and admins oversee the entire system.
?? Tech Stack

    Backend: Django, DRF, SQLite/PostgreSQL

    Frontend: HTML, CSS, Bootstrap, JS, jQuery, AJAX

    Others: jdatetime, SMS verification

?? Key Features

    Product listings with categories, ratings, and discounts

    Customer panel: orders, addresses, reviews

    Vendor panel: manage products, discounts, orders

    Admin panel: full control with custom branding

    Guest cart support (login only at checkout)

?? Setup

git clone <repo-url>
cd project/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

?? Apps

    accounts, cart, customers, vendors, website, admin

?? Notes

    Persian language supported

    Use develop and master branches

    Each shop can have multiple staff roles (owner, manager, operator)