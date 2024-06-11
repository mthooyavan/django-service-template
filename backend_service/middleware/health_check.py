import logging
import uuid

import psutil
import redis
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import DefaultStorage
from django.db import connection, connections
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.utils import timezone

from backend_service.celery import app as celery_app
from backend_service.logging import thread_local_storage

logger = logging.getLogger(__name__)


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            if request.path == "/liveliness/":
                return self.liveness(request)
            elif request.path == "/readiness/":
                return self.readiness(request)
            elif request.path == "/health-check/":
                return self.health_check(request)
        # Generate a unique correlation id for each request
        request.correlation_id = uuid.uuid4()
        thread_local_storage.request_initiated_time = timezone.now()
        thread_local_storage.correlation_id = request.correlation_id
        return self.get_response(request)

    @staticmethod
    def liveness(request):
        """
        Returns that the server is alive.
        """
        return HttpResponse("OK")

    @staticmethod
    def readiness(request):
        """
        Connect to each database and do a generic standard SQL query
        that doesn't write any data and doesn't depend on any tables
        being present.
        """
        try:
            for name in connections:
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    return HttpResponseServerError(
                        "Database: Returned invalid response."
                    )
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            return HttpResponseServerError("Database: Cannot connect to the database.")

        try:
            r = redis.StrictRedis.from_url(settings.REDIS_URL)
            r.ping()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            return HttpResponseServerError("Redis: Cannot connect to the database.")

        return HttpResponse("OK")

    def health_check(self, _request):
        status = {}

        # Cache & Redis
        self._check_cache(status)

        # Celery
        self._check_celery(status)

        # Database & Migrations
        self._check_database(status)

        # Storage, Disk usage & Memory usage
        self._check_system(status)

        status_code = 200
        if "failed" in status.values():
            status_code = 400

        return JsonResponse(data=status, status=status_code)

    @staticmethod
    def _check_cache(status):
        try:
            logger.debug("Setting cache key")
            cache.set("health_check_key", "value")
            status["Cache backend: default"] = (
                "working" if cache.get("health_check_key") == "value" else "failed"
            )
        except Exception as e:  # pylint: disable=broad-except
            status["Cache backend: default"] = "failed"
            logger.error("Cache backend: default failed due to %s", e)

        try:
            logger.debug("Pinging Redis")
            r = redis.StrictRedis.from_url(settings.REDIS_URL)
            r.ping()
            status["RedisHealthCheck"] = "working"
        except Exception as e:  # pylint: disable=broad-except
            status["RedisHealthCheck"] = "failed"
            logger.error("RedisHealthCheck failed due to %s", e)

    @staticmethod
    def _check_celery(status):
        try:
            logger.debug("Pinging Celery")
            i = celery_app.control.inspect()
            active_nodes = i.ping()
            status["CeleryPingHealthCheck"] = "working" if active_nodes else "failed"
        except Exception as e:  # pylint: disable=broad-except
            status["CeleryPingHealthCheck"] = "failed"
            logger.error("CeleryPingHealthCheck failed due to %s", e)

    @staticmethod
    def _check_database(status):
        try:
            logger.debug("Checking database connection")
            status["DatabaseBackend"] = "working"
            for name in connections:
                logger.debug("Checking database connection for %s", name)
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    status["DatabaseBackend"] = "failed"
                    logger.error("DatabaseBackend returned invalid response")
        except Exception as e:  # pylint: disable=broad-except
            status["DatabaseBackend"] = "failed"
            logger.error("DatabaseBackend failed due to %s", e)

        try:
            logger.debug("Checking migrations")
            executor = MigrationExecutor(connection)
            targets = executor.loader.graph.leaf_nodes()
            if not executor.migration_plan(targets):
                status["MigrationsHealthCheck"] = "working"
            else:
                status["MigrationsHealthCheck"] = "failed"
                logger.error("MigrationsHealthCheck failed due to pending migrations")
        except Exception as e:  # pylint: disable=broad-except
            status["MigrationsHealthCheck"] = "failed"
            logger.error("MigrationsHealthCheck failed due to %s", e)

    @staticmethod
    def _check_system(status):
        try:
            logger.debug("Checking storage")
            storage = DefaultStorage()
            with storage.open("health_check.txt", "w") as f:
                f.write("test")
            storage.delete("health_check.txt")
            status["DefaultFileStorageHealthCheck"] = "working"
        except Exception as e:  # pylint: disable=broad-except
            status["DefaultFileStorageHealthCheck"] = "failed"
            logger.error("DefaultFileStorageHealthCheck failed due to %s", e)

        try:
            logger.debug("Checking disk usage")
            disk_usage = psutil.disk_usage("/")
            if disk_usage.free < getattr(settings, "DISK_USAGE_MAX", 0):
                status["DiskUsage"] = "failed"
                logger.error(
                    "DiskUsage failed due to %s free disk space", disk_usage.free
                )
            else:
                status["DiskUsage"] = "working"
        except Exception as e:  # pylint: disable=broad-except
            status["DiskUsage"] = "failed"
            logger.error("DiskUsage failed due to %s", e)

        try:
            logger.debug("Checking memory usage")
            memory = psutil.virtual_memory()
            if memory.available < getattr(settings, "MEMORY_MIN", 0):
                status["MemoryUsage"] = "failed"
                logger.error(
                    "MemoryUsage failed due to %s available memory", memory.available
                )
            else:
                status["MemoryUsage"] = "working"
        except Exception as e:  # pylint: disable=broad-except
            status["MemoryUsage"] = "failed"
            logger.error("MemoryUsage failed due to %s", e)
