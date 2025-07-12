# alx_travel_app_0x01

## Objective

```
Objective : Build API views to manage listings and bookings, and ensure the endpoints are documented with Swagger.

Instructions

Duplicate Project:

Duplicate the project alx_travel_app_0x00 to alx_travel_app_0x01
Create ViewSets:

In listings/views.py, create viewsets for Listing and Booking using Django REST framework’s ModelViewSet.
Ensure that these views provide CRUD operations for both models.
Configure URLs:

Use a router to configure URLs for the API endpoints.
Ensure endpoints follow RESTful conventions and are accessible under /api/.
Test Endpoints:

Test each endpoint (GET, POST, PUT, DELETE) using a tool like Postman to ensure they work as expected.
```

```bash
0. Background Task Management with Celery and Email Notifications in Django

Objective

Configure Celery with RabbitMQ to handle background tasks and implement an email notification feature for bookings.

Instructions

Duplicate Project:

Duplicate the project alx_travel_app_0x02 to alx_travel_app_0x03


Configure Celery:
Set up Celery with RabbitMQ as the message broker.
Add Celery configurations in settings.py and create a celery.py file in the project root.
Define Email Task:

In listings/tasks.py, create a shared task function to send a booking confirmation email.
Ensure the email task uses the Django email backend configured in settings.py.
Trigger Email Task:

Modify the BookingViewSet to trigger the email task upon booking creation using delay().
Test Background Task:

Test the background task to ensure the email is sent asynchronously when a booking is created.

Repo:
GitHub repository: alx_travel_app_0x03
Directory: alx_travel_app
File: alx_travel_app/settings.py, listings/tasks.py, listings/views.py, README.md
```
