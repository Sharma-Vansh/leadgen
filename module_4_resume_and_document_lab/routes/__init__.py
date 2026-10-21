"""
Routes Package for Module 4
"""
from module_4_resume_and_document_lab.routes.resume_routes import router as resume_router
from module_4_resume_and_document_lab.routes.document_routes import router as document_router

__all__ = ["resume_router", "document_router"]
