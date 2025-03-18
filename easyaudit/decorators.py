import time
import functools

from requests.models import Response
from .models import ExternalServiceLog

PROTOCOLS = ("http", "sftp")


def log_http_operation(service_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = kwargs.get("url", "")
            method = kwargs.get("method", "GET")
            request_headers = kwargs.get("headers", {})
            request_body = kwargs.get("data", {})

            try:
                # Execute the function
                response, error = func(*args, **kwargs)
                execution_time = time.time() - start_time

                request_repr = {
                    "endpoint": endpoint,
                    "method": method,
                    "headers": request_headers,
                    "body": request_body,
                }

                if isinstance(response, Response):
                    response_repr = {
                        "status_code": response.status_code,
                        "body": response.json(),
                    }
                else:
                    response_repr = str(response)

                # Create log entry
                ExternalServiceLog.objects.create(
                    service=service_name,
                    protocol=PROTOCOLS[0],
                    request_repr=str(request_repr),
                    response_repr=str(response_repr),
                    error_message=str(error) if error else "",
                    execution_time=execution_time,
                )

                return response, error

            except Exception as e:
                execution_time = time.time() - start_time
                ExternalServiceLog.objects.create(
                    service=service_name,
                    protocol=PROTOCOLS[0],
                    request_repr=str(request_repr),
                    error_message=str(e),
                    execution_time=execution_time,
                )
                raise

        return wrapper

    return decorator


def log_sftp_operation(operation):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                # Get SFTP details from self (instance)
                instance = args[0]
                service_name = kwargs.get("service_name", "")
                host = getattr(instance, "sftp_host", None)
                file_name = kwargs.get("filename", "")
                file_size = kwargs.get("file_size", 0)
                remote_path = kwargs.get("path_to_folder", "")
                extension = kwargs.get("extension", "")
                print("Data", kwargs.get("data", []))

                request_repr = {
                    "host": host,
                    "operation": operation,
                    "remote_path": remote_path,
                    "file_name": file_name,
                    "extension": extension,
                    "file_size": file_size,
                }

                # Execute SFTP operation
                result, error = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Create log entry
                ExternalServiceLog.objects.create(
                    service=service_name,
                    protocol=PROTOCOLS[1],
                    request_repr=str(request_repr),
                    response_repr=str(result),
                    error_message=str(error) if error else "",
                    execution_time=execution_time,
                )

                return result, error

            except Exception as e:
                execution_time = time.time() - start_time
                ExternalServiceLog.objects.create(
                    service=service_name,
                    protocol=PROTOCOLS[1],
                    request_repr=str(request_repr),
                    error_message=str(e),
                    execution_time=execution_time,
                )
                raise

        return wrapper

    return decorator
