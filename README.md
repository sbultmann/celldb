# celldb
## Table of contents
* [Introduction](#introduction)
* [Technologies](#technologies)
* [Setup](#setup)
* [Functionalities](#functionalities)
* [Acknowledgement](#acknowledgement)
## Introduction
The celldb project aims to store the information of some genetically modified cell lines. It allows users to upload, search as well as export entries of cell lines.
## Technologies
This project is created with:
* Python 3.9.2
* Flask 1.1.2
* Other python packages can be found in the file requirements.txt.
## Setup
To run the application locally:
* Install python 3.9.2
* Open command line and switch to the cellDB directory
    
    `$ cd cellDB`

* Activate the virtual environment
    
    `$ .\scripts\activate`

* Install necessary packages
    
    `$ pip install -r requirements.txt`

* Start the webapp locally
    
    `$ flask run`

* Open the bowser and turn to http://127.0.0.1:5000/
* To close the webapp , press CTRL+C on the command line interface
## Functionalities
### Registration and login
#### Registration of a normal user
For the security of the webapp, users can only be registered via python shell. A normal user has no right to do sensitive operations like deleting an entry.
    
     >>> from app import models,db
    
     >>> from app.models import User
     
     >>> new_user = User(username = 'example', email = 'example@celldb.com')
     
     >>> new_user.set_password('password_here')
     
     >>> db.session.add(new_user)
     
     >>> db.session.commit()
     
     
As for the registration of a new administrator account, just change one line of the code above slightly.

    >>> new_user = User(username = 'example', email = 'example@celldb.com', role = 'ADMIN')
    
An administrator has the permission to delete/modify any entries.
#### Login
You do not have access to any functions of celldb until you login with your username and password.
### Homepage
On the homepage of celldb, you will find most recently edited entries. Below the entries, there is a search box which allows you to find targets efficiently. With the navigation bar on top of the page, other functions can be found. You will be introduced to them later.
![Homepage](.\images\home.png)
The search box allows you to specify a keyword and the type of the keyword to help you find cell lines you want. The example usage of search function is shown below.
![Search box](.\images\search1.png)
![Results of searching](.\images\search2.png)
### Cell lines
#### All cell lines
You can easily get access to all cell lines in the database with the 'cell lines' button on the homepage. By clicking each cell line, you will find detailed information. It is noteworthy that only administrators are allowed to modify/delete any entries and a normal user can only edit entries that were created by him/her. You may notice the 'Export all cell lines' button and as its name suggested, you can export a csv file with all information of all cell lines.
![All cell lines](.\images\allcl.png)
### New entry
The new entry page enables you to create new entries of cell lines. Just fill in the form and click on submit, then your new cell line is created.
![New entry](.\images\new1.png)
## Acknowledgement
I thank my supervisor Dr. Sebastain Bultmann for his support and guidance to this project. The webapp development course taught by him also gave me a lot of inspiration.
