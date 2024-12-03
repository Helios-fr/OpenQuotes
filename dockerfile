# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Copy the admin secret to the container at /app
COPY admin.secret .

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory contents into the container at /app/src
COPY src/ ./src

# Set the default command to run the main.py file
CMD ["python", "./src/main.py"]

# To build the Docker image, run the following command in the terminal:
# docker build -t openquotes .
# To run the Docker container, run the following command in the terminal:
# docker run -d openquotes -p 8900:8000