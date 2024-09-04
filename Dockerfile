# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 to allow access to the Streamlit app
EXPOSE 8501

# Define environment variables (optional if you don't want to pass them during runtime)
ENV MONGO_PWD=${MONGO_PWD}
ENV OPKEY=${OPKEY}

# Run the Streamlit app when the container launches
CMD ["streamlit", "run", "app.py"]
