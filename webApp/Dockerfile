# Use the official Python image as the base image
FROM python:3.8.2

# Set the working directory in the container
WORKDIR /webApp

# Copy the application files into the working directory
COPY . /webApp

# Install the application dependencies
RUN pip install -r requirements.txt

# Define the entry point for the container
CMD ["/usr/local/bin/python -m pip install --upgrade pip", "python main.py"]