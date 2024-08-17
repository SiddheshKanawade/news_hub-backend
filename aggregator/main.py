from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from aggregator.exceptions import CustomException
from aggregator.routes import router

APP_URL_PREFIX: str = "/weather"


def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_listeners(app: FastAPI) -> None:
    # Exception handler
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"errorCode": exc.error_code, "msg": exc.message},
        )


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"errorCode": error_code, "message": message},
    )


def init_middleware(app: FastAPI) -> None:
    return


def create_app() -> FastAPI:
    app = FastAPI(
        title="News Aggregator",
        description="API service to fetch hailstorm data for given time frame and location",
        version="0.0.1",
        docs_url="/aggregator/swagger-ui",
        redoc_url="/aggregator/swagger-redoc",
        openapi_url="/aggregator/swagger.json",
        # dependencies=[Depends(get_db)],
    )
    init_cors(app=app)
    init_listeners(app=app)
    init_middleware(app=app)
    app.include_router(router)

    return app


app = create_app()
