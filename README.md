# Catalog Application
The Item Catalog project consists of an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system.
It is a website that the visitor can show all categories and its items but the creator can add, edit and delete item in his own category.
## Description :
- The server side is written in python.
   - The `application.py` file include :
      - the application running on localhost:8000 .
      - implementing a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.
      - reading category and item information from a database.
      - login for user.
      - after login user can add new items, edit and delete only for those items that he has created.
      - implementing all Html endpoints that display information of items and categories in the catalog.
   - The `database_setup.py` file include creating the *catalog.db* database with *sqlalchemy*.
   - The `lotsofitems.py` file include adding users, items and categories for the database.
- The client side is written in html, css and javascript.
   - The `templates` folder includes the all HTML files.
   - The `static` folder includes the CSS file.

## How to run this project :
- Install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/).
- Launch the Vagrant VM (by typing `vagrant up` in the directory `vagrant` from the terminal).
- put the `catalog` folder in `vagrant` folder .
- In the terminal write the commend `cd /vagrant/catalog` and then execute the commend `python application.py` to run the project on *localhost:8000* .
- In the browser write `localhost:8000` .
