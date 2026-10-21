"""
Routes Package
Exports authentication, profile, and feed routers.
"""
from module_3_backend_and_matching.routes.auth_routes import router as auth_router
from module_3_backend_and_matching.routes.profile_routes import router as profile_router
from module_3_backend_and_matching.routes.feed_routes import router as feed_router

__all__ = ["auth_router", "profile_router", "feed_router"]
