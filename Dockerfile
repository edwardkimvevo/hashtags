# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory to /app
WORKDIR /hashtag-flask

# Copy the current directory contents into the container at /app
COPY . /hashtag-flask

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80


# Run hashtag.py when the container launches
CMD ["python", "hashtag.py"]