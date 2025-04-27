
# Appointment Booking App

The Online Appointment Booking System is a web platform that simplifies appointment scheduling for services like medical practices and beauty salons. Users can register, view available slots, and book or cancel appointments in real time, while administrators can manage availability and monitor bookings. With role-based access for security, the system replaces manual scheduling, offering a streamlined and user-friendly experience.





## Installation Procedure

Follow these steps to set up the **Appointment Booking App** locally:

#### Clone the Repository

Start by cloning the project repository to your local machine:
```bash
git clone https://github.com/Magesh-Sundaravel/bs_booking.git
cd bs_booking

# Install Dependencies
pip install -r requirements.txt

# Set Up the Virtual Environment
conda create --name env_name python=3.x
conda activate env_name

# Run the Server
python manage.py runserver

```

## Deployment

To deploy this project run

```bash
# Build the Docker Image
docker build -t bs_booking.

# Run the Containers
docker-compose up

# Access the Application
http://localhost:8000/

# Stopping the Containers
docker-compose down
```

