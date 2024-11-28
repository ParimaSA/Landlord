# The Room's taken, but IM AVAILABLE
Our project is about collecting the data of apartment properties for helping the landlord to manage their property.


## Installation

1. Clone the project from Github (https://github.com/ParimaSA/Landlord.git)
    ```
    git clone https://github.com/ParimaSA/Landlord.git
    ```
2. Open the project file in your IDE
3. Go to Landlord directory
    ```
    cd Landlord
    ```
4. Create your virtual environment
    ```
    python3 -m venv env
    ```
5. Activate virtual environment
   ```
   # On Mac/Linux
   source env/bin/activate
   
   # On Window
   env\Scripts\activate
   ```
6. Install requirements.txt
    ```
    pip install -r requirements.txt
    ```
7. Run Migrations
    ```
    python manage.py migrate
    ```
8. Load fixture data
    ```
    python manage.py loaddata data/user.json data/all-data.json
    ```
9. Run server
    ```
    python manage.py runserver
    ```

## Running the Application
1. Activate the virtual environment
    ```
    # on Mac/Linux
    source venv/bin/activate
    
    # on Window
    venv\Scripts\activate 
    ```
2. Start Django Development server
    ```
   # Recommended python version >= 3.11
    python manage.py runserver
    ```
If the port is not available, you can kill the port by following these steps:
   ```
   # Find the process using port 8000 on Mac/Linux
   sudo lsof -i :8000
   
   #kill the port using PID
   sudo kill -9 PID
   ```
   ```
   # Find the process using port 8000 on Window
   netstat -ano | findstr :8000
   
   #kill the port using PID
   taskkill /PID PID /F
   ```
3. Access the server on your browser http://127.0.0.1:8000/

## How to use

You can filter the data, edit and add new data to each table by logging in using these demo account.

### Demo User
| Username  | Password |
|-----------|----------|
| landlord1 | hackme11 |
| landlord2 | hackme22 |
| landlord3 | hackme33 |
| landlord4 | hackme44 |
| landlord5 | hackme55 |
| landlord6 | hackme66 |
| landlord7 | hackme77 |
| landlord8 | hackme88 |
| landlord9 | hackme99 |


Additional: The lease contract data can only be added to the room with 'available' status.

