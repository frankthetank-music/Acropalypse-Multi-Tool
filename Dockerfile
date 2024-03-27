# Using an official Python runtime image as the parent image
FROM python:3.10

# Setting the working directory in the container
WORKDIR /usr/src/app

# Installing dependencies
# Copying the 'requirements.txt' file into the container directory '/usr/src/app'
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copying the source code into the container directory '/usr/src/app'
COPY . .

# Command that is executed when the container starts
CMD [ "python", "./gui.py" ]
