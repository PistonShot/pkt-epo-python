FROM tiangolo/uwsgi-nginx-flask:python3.12

# Set environment variables
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

# Set working directory
WORKDIR /app

# Copy application files
COPY ./app /app/app
COPY ./wsgi.py /app/wsgi.py
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the default port
EXPOSE 8000
