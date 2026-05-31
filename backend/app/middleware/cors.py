from fastapi.middleware.cors import CORSMiddleware


def cors_middleware_kwargs(origins: list[str]) -> dict[str, object]:
    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }

