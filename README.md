# MPN Drift Detection Dashboard

This project consists of a FastAPI backend and a Next.js frontend. Docker and Docker Compose are used to streamline deployment and create a consistent runtime environment.

## Local Hosting

### Running the Backend

1. **Prerequisites:**

   - **Python 3.10:** Download the appropriate installer from https://www.python.org/downloads/ .
   - **pip:** Python's package installer (comes bundled with Python).
   - **configs/default.yaml:** the configs and default.yaml files are necessary if not passing a configuration in. See default.config to view essential variables.

2. **Setting up the Environment:**

   ```bash
   python -m venv env
   # Activate the environment
   env\Scripts\activate # (Windows)
   source env/bin/activate # (Linux/macOS):
   # Install the dependencies
   pip install -r requirements.txt
   ```

   Alter the default configuration file located in backend/configs or pass one in when running main.py

3. **To Run it:**
   - In the **backend/** directory:

   *Default config*
   ```bash
   python main.py 
   ```
   *Pass a config*
   ```bash
   python main.py path/to/config.yaml
   ```
   

### Running the Frontend

1. **Prerequisites:**

   - **Node.js 20.11.1:** Download the appropriate installer from https://nodejs.org/en/download .
   - **npm or yarn:** One of these package managers is required, typically included with your Node.js installation.

2. **Navigate and Run:**

   ```bash
   cd frontend/app
   npm run dev # or yarn
   ```

   - Then navigate to http://localhost:3000 to view the nextjs front end.

## Docker

- **Docker Engine:** Install Docker for your operating system. Instructions can be found on the official Docker website: https://www.docker.com/get-started
- **Docker Compose:** This is often installed alongside Docker or as part of Docker Desktop.

### To Build and Run

1.  **Navigate to the Project Directiory**

    ```bash
    cd MPN-Drift-Detection
    ```

2.  **Build and Run the Containers**
    ```bash
    docker-compose up -d --build
    ```
    The --build argument will force docker compose to build the underlying images if required.
