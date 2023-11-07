# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN python init_db.py

# Make port 3111 available to the world outside this container
EXPOSE 3111
# tag the image as TechTrends
LABEL Name=techtrends Version=0.0.1

# Run app.py when the container launches
CMD ["python", "app.py"]
