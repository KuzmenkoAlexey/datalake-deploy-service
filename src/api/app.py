import asyncio

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.dependencies import UnauthenticatedException
from api.error_handling import handle_unauthenticated_exception
from api.router.full_project_structure import full_project_router
from api.router.project import projects_router
from api.router.project_credentials import project_credentials_router
from api.router.project_deploy import project_deploy_router
from config import settings
from database.db import DatabaseWrapper


def get_application(loop=None):
    sentry_sdk.init(dsn=settings.sentry_url, traces_sample_rate=1.0)

    DatabaseWrapper.set_event_loop(loop or asyncio.get_event_loop())

    app = FastAPI(title="Deploy Service")

    app.include_router(projects_router)
    app.include_router(project_credentials_router)
    app.include_router(project_deploy_router)
    app.include_router(full_project_router)
    app.add_exception_handler(
        UnauthenticatedException, handle_unauthenticated_exception
    )
    return SentryAsgiMiddleware(app)
