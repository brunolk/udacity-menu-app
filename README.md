# Restaurant Menu App

This project is part of Udacity's Backend Nanodegree. It's a RESTful web application that allows users to create, edit and delete restaurants as well as their menu items. It uses the Flask framework to perform CRUD opertations on a SQL database.

## Getting Started

In this repository you will find:

* **project.py**: main module which runs the Flask application

* **database_setup.py**: module which creates the restaurants database

* **lotsofmenus.py**: modulo which populates the restaurants database

* **client_secrets.json**: json file with the application's google oauth credentials

* **templates**: folder containing the application HTML files

* **static**: folder containing the application CSS files

## Prerequisites

* [Python](https://www.python.org/downloads/)
* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Setup

1. Install Vagrant and VirtualBox
2. Clone [Udacity's repository](https://github.com/udacity/fullstack-nanodegree-vm) to download the Virtual Machine configuration
3. Access the vagrant folder within the cloned fullstack-nanodegree-vm folder and copy all the files from this repository to the catalog folder

## Start the Virtual Machine

1. Start the Virtual Machine inside Vagrant sub-directory in the downloaded fullstack-nanodegree-vm repository using the command:
  
  ```
  vagrant up
  ```

2. Log into the Virtual Machine using the command:
  
  ```
  vagrant ssh
  ```

## Create and populate the database

1. Make sure you are logged into the Virtual Machine and then change the directory to /catalog using the command:

  ```
  cd /vagrant/catalog/
  ```

2. Create the database using the command:

  ```
  python database_setup.py
  ```

3. Populate the database using the command:

  ```
  python lotsofmenus.py
  ```

## Run the project

1. Run the project.py from the vagrant directory inside the Virtual Machine using the command:

  ```
  python project.py
  ```

2. Access and test the application: [http://localhost:5000](http://localhost:5000)

## JSON Endpoints
The following are open to the public:

* `/JSON` or `/restaurants/JSON`: Shows all restaurants

* `/restaurants/<int:restaurant_id>/JSON/`: Only shows the restaurant which id is equal to restaurant_id

* `/restaurants/<int:restaurant_id>/menu/JSON/`: Shows all menu items from the restaurant which id is equal to restaurant id

* `/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/`: Only shows the menu item which id is equal to menu id and from the restaurant which id is equal to restaurant id

## Author

* Bruno Kanashiro
