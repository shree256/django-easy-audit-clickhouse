=======================
django-easy-audit-clickhouse
=======================

Logging implementation with clickhouse integration on top of django-easy-audit==1.3.7.

Quick start
-----------
1. Prerequisites::
    - django==4.2
    - clickhouse-connect>=0.8.15
    - celery>=5.4.0
    - djangorestframework>=3.15

2. Add "easyaudit" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'easyaudit',
    ]

3. Add django-easy-audit's middleware to your MIDDLEWARE (or MIDDLEWARE_CLASSES) setting like this::

    MIDDLEWARE = (
        ...
        'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
    )

4. Run 'python manage.py migrate easyaudit' to create the audit models.

5. Configure the ClickHouse connection in your settings.py::

    CLICKHOUSE_USER = 'user'
    CLICKHOUSE_PASSWORD = 'password'
    CLICKHOUSE_HOST = 'localhost'
    CLICKHOUSE_PORT = 8123
    CLICKHOUSE_DATABASE = 'default'
    CLICKHOUSE_SECURE = False

6. Create shared task of `send_logs_to_clickhouse` to sync data from django to clickhouse::

    @shared_task
    def send_audit_logs_to_clickhouse():
        from easyaudit.tasks import send_logs_to_clickhouse
        send_logs_to_clickhouse()

    app.conf.beat_schedule = {
        "send-logs-to-clickhouse": {
            "task": "path.to.send_logs_to_clickhouse",
            "schedule": crontab(hour=9, minute=10),  # 12:00 AM PST
        },
    }

7. Add `SEND_LOGS_TO_CLICKHOUSE` to settings with True/False for enable/disable data push to clickhouse.