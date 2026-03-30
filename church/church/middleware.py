import logging


error_logger = logging.getLogger("app.exceptions")


class ExceptionLoggingMiddleware:
	"""Log unhandled exceptions with request context before Django returns HTTP 500."""

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		try:
			return self.get_response(request)
		except Exception:
			error_logger.exception(
				"Unhandled exception: %s %s user=%s",
				request.method,
				request.get_full_path(),
				getattr(request.user, "username", "anonymous"),
			)
			raise
