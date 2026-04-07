"""Middleware for request logging, rate limiting, and error handling."""

import time
import logging
from functools import wraps
from collections import defaultdict
from flask import request, jsonify

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if client IP is within rate limit."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > window_start
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        self.requests[client_ip].append(now)
        return True

    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for a client."""
        now = time.time()
        window_start = now - self.window_seconds
        active = [ts for ts in self.requests[client_ip] if ts > window_start]
        return max(0, self.max_requests - len(active))


rate_limiter = RateLimiter()


def rate_limit(f):
    """Decorator to enforce rate limiting on endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after_seconds": 60,
            }), 429
        return f(*args, **kwargs)
    return decorated_function


def setup_request_logging(app):
    """Configure request/response logging middleware."""

    @app.before_request
    def log_request():
        request.start_time = time.time()

    @app.after_request
    def log_response(response):
        latency = round(time.time() - getattr(request, "start_time", time.time()), 3)
        logger.info(
            f"{request.method} {request.path} | "
            f"status={response.status_code} | "
            f"latency={latency}s | "
            f"ip={request.remote_addr}"
        )
        response.headers["X-Response-Time"] = f"{latency}s"
        return response


def setup_error_handlers(app):
    """Register global error handlers."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": "Resource not found."}), 404

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"error": "Too Many Requests", "message": "Rate limit exceeded."}), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal Server Error", "message": "Something went wrong."}), 500
