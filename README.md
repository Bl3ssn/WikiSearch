# WikiSearch- A Wikipedia distributed Web Application


## Overview

This project is a distributed web application built using Flask. It allows users to search for people, places, and events using Wikipedia.

The system is distributed across multiple components:

* A Flask web application (host machine)
* A remote Ubuntu EC2 virtual machine (Wikipedia processing)
* A MySQL database running in a Docker container (caching)

---

## System Architecture

The application workflow is as follows:

1. The user enters a search query in the web interface.
2. Flask checks the MySQL database to see if the query already exists (cache).
3. If found → the cached result is returned (**CACHE HIT**).
4. If not found → Flask connects to the EC2 instance via SSH.
5. The EC2 instance runs `wiki.py` to query Wikipedia.
6. Results are returned to Flask and displayed in the browser.
7. The first page of results is stored in MySQL for future use.

---

## Features

* Flask-based web interface
* Wikipedia search using Python API
* Remote execution using SSH (Paramiko)
* MySQL caching to improve performance
* Pagination (10 results per page)
* Each result includes:

  * Title
  * URL
  * 5-sentence summary

---

## Project Structure

```
Assignment/
│
├── main.py                # Flask application
├── wiki.py                # Runs on EC2 (Wikipedia search)
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
│
├── templates/
│   └── wikihome.html      # Web interface
│
├── static/
│   └── style.css          # Styling
```

---

## Requirements

### Host Machine (Flask App)

* Python 3
* Flask
* Paramiko
* mysql-connector-python

### EC2 Ubuntu VM

* Python 3
* wikipedia Python package

### Database (Docker Container)

* MySQL Server
* Port exposed: **7888**

---

## Installation

### 1. Install Python dependencies

```bash
pip install flask paramiko mysql-connector-python
```

### 2. Install Wikipedia package on EC2

SSH into EC2:

```bash
sudo apt update
sudo apt install python3-pip
pip3 install wikipedia
```

---

### 3. Setup MySQL Database

Login to MySQL:

```bash
mysql -h 127.0.0.1 -P 7888 -u root -p
```

Create database and table:

```sql
CREATE DATABASE MYDB;
USE MYDB;

CREATE TABLE wiki_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query VARCHAR(255) NOT NULL UNIQUE,
    result TEXT NOT NULL
);
```

---

## Configuration

Update the following values in `main.py`:

```python
INSTANCE_IP = "63.33.189.35"
KEY_FILE = "newkey.pem"

DB_HOST = "63.33.189.35"
DB_PORT = 7888
DB_NAME = "MYDB"
DB_USER = "root"
DB_PASSWORD = "mypassword"
```

---

## Running the Application

### 1. Start MySQL container

```bash
docker run -d \
--name mysqlcontainer \
-e MYSQL_ROOT_PASSWORD=mypassword \
-p 7888:3306 \
mysql/mysql-server:latest
```

---

### 2. Ensure `wiki.py` is on EC2

Place it in:

```bash
/home/ubuntu/wiki.py
```

Test:

```bash
python3 wiki.py "cat" 1
```

---

### 3. Run Flask app

```bash
python main.py
```

Open in browser:

```
http://127.0.0.1:8888
```

---

## How to Use

1. Enter a search term (e.g. *cat*, *Dublin*, *Barack Obama*)
2. Click **Search**
3. View results
4. Use:

   * **Next** → next page
   * **Previous** → previous page
5. Click **Clear** to reset

---

## Pagination

* 5 results per page
* Up to 20 results fetched from Wikipedia
* Navigation supported via Next/Previous buttons

---

## Caching Mechanism

### First search:

```
CACHE MISS: cat
```

* Data fetched from EC2
* Stored in MySQL

### Second search:

```
CACHE HIT: cat
```

* Data returned from database
* Faster response

---

## Clearing Cache

To reset cache:

```sql
TRUNCATE TABLE wiki_cache;
```

---

## Notes

* Only the **first page** of results is cached
* Later pages are fetched dynamically
* Wikipedia results are limited by API constraints
* Warnings from Wikipedia are suppressed for clean output

---


## Author

* Name: Blessing Omoruyi
* Student ID: 25105061
* Module: CT5169

---
