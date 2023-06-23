
# Ticket Show Booking

A web application using python and flask where admin has the privilege to add venues and create shows and then these shows can be assigned to venues .The user can view the shows in different venues and can book tickets for a desired show in a venue of their choice.


## Features

- Creating venues and shows.
- Updating and deleting venues and shows.
- Search for venues.
- Visualisation of ratings of shows.
- Book shows at venues of your choice.
- Search for shows you booked.
- Different logins for admin and users.


## Tech Stack

**Frontend:** Jinja2,HTML5,CSS,Bootstrap

**Backend:** Flask

**Database** SQLite



## Running Tests Locally

Install dependencies

```bash
  pip install -r requirements.txt
```

Python command line

```bash
  python
```
Initiate the Database

```bash
  from app import *
```
Create Database 

```bash
  db.create_all()
```
Start the server

```bash
  python app.py 
```
