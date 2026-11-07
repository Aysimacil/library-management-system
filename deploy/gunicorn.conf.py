import os

bind = os.environ.get("GUNICORN_BIND", "unix:/run/library/gunicorn.sock")
workers = int(os.environ.get("WEB_CONCURRENCY", "3"))
timeout = 30
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = None
errorlog = "-"
capture_output = True
# Django trusts the proxy only via its explicit TRUST_PROXY_HTTPS setting.
forwarded_allow_ips = ""
