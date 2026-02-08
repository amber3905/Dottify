# 🎵 Dottify — Music Management Web Application

## Overview
**Dottify** is a full-stack web application built with **Django** that allows artists to manage music content while providing customers with access to a curated music catalogue. The system supports album and song management, user authentication and authorisation, RESTful APIs, and HTML views rendered with Django templates.

This project demonstrates the design and implementation of a complete, production-style web application, covering data modelling, security, API development, testing, and front-end templating.

## Key Features
### Music Management
- Artists can create and manage **albums** and **songs**
- Albums include metadata such as cover art and associated tracks
- Fully relational data model with validations and constraints
### User Accounts & Security
- Authentication using Django’s built-in user system
- Extended user profiles with display names
- Role-based permissions for different types of users
- Secure access to protected resources using mixins and helpers
### Web Interface
- Clean, accessible HTML views using Django templates
- Responsive styling with **Bootstrap**
- Album index and detail views with media display
- Valid, standards-compliant HTML
### RESTful API
- API endpoints exposing album and song data
- Structured responses matching defined schemas
- Correct use of HTTP status codes
- Sample data compatibility for testing and development
### Testing & Quality
- Automated tests written using Django’s testing framework
- Coverage across models, views, routes, authentication, and permissions
- Code formatted to **PEP 8** standards
- Use of class-based views, viewsets, and mixins where appropriate
- Localised strings and Django’s messages framework
## Tech Stack
- **Backend:** Django, Django REST Framework
- **Frontend:** Django Templates, Bootstrap
- **Database:** SQLite (development)
- **Authentication:** Django Auth
- **Testing:** Django Test Framework
- **Version Control:** Git
## Project Structure (High-Level)
- `models/` — database schema and relationships
- `views/` — class-based HTML and API views
- `templates/` — HTML templates
- `tests/` — automated test suite
- `static/` — styles and assets
## Scenario & Design Context
The application is designed for a fictional company, **MusicDB Inc.**, which operates Dottify as a subscription-based music service.
- **Artists** manage albums and songs
- **Customers** browse the catalogue, create playlists, and interact with content
- **Employees/Admins** access summary data and administer system resources

The system was developed end-to-end to simulate real-world requirements, evolving features, and integrated components.
## What This Project Demonstrates
- Building a complete Django application from scratch
- Translating requirements into a structured data model
- Implementing authentication, authorisation, and permissions
- Designing REST APIs alongside server-rendered views
- Writing maintainable, tested, and standards-compliant code
- Managing a growing codebase with meaningful commits
## Running the Application Locally
### Prerequisites
Make sure you have the following installed:
- Python 3.10+
- pip
- Git
## Clone the repository
```bash
git clone git@github.com:amber3905/Dottify.git
cd Dottify
```
## Create and activate a virtual environment
### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
### Windows
```bash
python -m venv venv
venv\Scripts\activate
```
## Install dependencies
```bash
pip install -r requirements.txt
```
## Apply database migrations
```bash
python manage.py migrate
```
## (Optional) Create a superuser
```bash
python manage.py createsuperuser
```
This allows access to the Django admin interface.
## Run the development server
```bash
python manage.py runserver
```
The application will be available at:
```bash
http://127.0.0.1:8000/
```
## Run tests
```bash
python manage.py test
```
