"""
Gunicorn Configuration File for APS Production

Usage:
    gunicorn --config gunicorn_config.py config.wsgi:application
"""
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests
max_requests_jitter = 50  # Add randomness to max_requests
timeout = 120  # Workers silent for more than this are killed
graceful_timeout = 30  # Timeout for graceful workers restart
keepalive = 2  # Wait time for requests on Keep-Alive connections

# Logging
accesslog = '/var/www/aps/logs/gunicorn-access.log'
errorlog = '/var/www/aps/logs/gunicorn-error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'aps_gunicorn'

# Server mechanics
daemon = False
pidfile = '/var/www/aps/gunicorn.pid'
user = os.getenv('GUNICORN_USER', 'ubuntu')
group = os.getenv('GUNICORN_GROUP', 'ubuntu')
umask = 0o007
tmp_upload_dir = None

# SSL (uncomment if using SSL)
# keyfile = '/path/to/keyfile.pem'
# certfile = '/path/to/certfile.pem'

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("Gunicorn is starting...")

def on_reload(server):
    """Called to recycle workers during a reload."""
    print("Gunicorn is reloading...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"Gunicorn is ready. Listening on {bind}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("Gunicorn is shutting down...")

# Statsd (optional monitoring)
# statsd_host = 'localhost:8125'
# statsd_prefix = 'aps'
