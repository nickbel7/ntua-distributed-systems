# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose port 8000 for the FastAPI app to run on
EXPOSE ${PORT}

# Run the command to start the FastAPI app
CMD ["sh", "-c", "python api.py --port ${PORT} --ip ${IP}"]