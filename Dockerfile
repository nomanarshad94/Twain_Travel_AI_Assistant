FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /travel_assistant

# Create logs directory and set permissions
RUN mkdir -p /travel_assistant/logs && chmod 777 /travel_assistant/logs

# Install pip and enable cache
RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt /travel_assistant/
RUN pip install -r requirements.txt

# Copy project files
COPY . /travel_assistant/

# Create directory for faiss indexing
RUN mkdir -p /travel_assistant/data/faiss_index

# Expose the port Flask runs on
EXPOSE 5000

# Run the application with gunicorn
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "--timeout", "60", "--log-level", "info", "--keep-alive", "60",  "run:app"]
