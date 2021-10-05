# sharemylist
django-project - share your lists (e.g. grocery list) with other users

## install
1. git clone https://github.com/michi-iam/sharemylist
2. create/activate your virtual enviroment
3. pip install -r requirements.txt
4. check settings.py and add **.env**
5. python manage.py makemigrations / migrate
6. python manage.py collectstatic
7. python manage.py createsuperuser
8. python manage.py runserver 
9. **create a ListUser** in admin (localhost/admin) 

## customize
1. Permissions 
    * einkaufsliste/urls.py
        * eklPerms = "einkaufsliste.can_use_list" # Your permissions 
        * loginUrl = "/admin/login/" # your login url
2. Styles
    * override static/styles
    * have a look at *js_btn_names.txt*, when you change html 

## todo
* tests
* register listusers
* styles :)
* seperate js from templates
* refactoring in general
* add contributing.md - everyone is welcome to contribute