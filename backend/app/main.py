"""
Aplicação principal FastAPI para Motor Biomecânico Paramétrico.
Inicializa a API com configuração, CORS, documentação, e endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import logging

from app.api import api_router
from app.database import initialize_database, get_database_info

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== INICIALIZAÇÃO DA APP ==========

def create_app() -> FastAPI:
    """Factory function para criar e configurar a aplicação FastAPI."""

    app = FastAPI(
        title="Motor Biomecânico Paramétrico",
        description="Sistema de IA para geração de palmilhas ortopédicas 3D customizadas",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ========== MIDDLEWARE ==========

    # CORS: origens permitidas via env CORS_ORIGINS (separadas por vírgula).
    # Sem a variável, libera qualquer origem (sem credenciais) para desenvolvimento.
    cors_origins = [o.strip().rstrip("/") for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    allow_all = not cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else cors_origins,
        allow_credentials=not allow_all,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ========== ROUTERS ==========

    # Inclui routers de API
    app.include_router(api_router)

    # ========== ROOT ENDPOINTS ==========

    @app.get("/", tags=["root"], summary="Root endpoint")
    async def root():
        """Root endpoint com informações básicas da API."""
        return {
            "service": "Motor Biomecânico Paramétrico",
            "version": "0.1.0",
            "status": "running",
            "docs": "/docs",
            "health": "/api/cases/health",
        }

    @app.get("/health", tags=["health"], summary="Health check geral")
    async def health():
        """Health check da aplicação."""
        db_info = get_database_info()
        return {
            "status": "healthy",
            "service": "motor-biomecanico-backend",
            "database": db_info,
        }

    @app.get("/api/health", tags=["health"], summary="Health check API")
    async def api_health():
        """Health check do backend API."""
        db_info = get_database_info()
        return {
            "status": "healthy",
            "service": "motor-biomecanico-api",
            "database": db_info,
        }

    # ========== STARTUP EVENTS ==========

    @app.on_event("startup")
    async def startup_event():
        """Executado ao iniciar a aplicação."""
        print("🚀 Motor Biomecânico iniciando...")

        # Initialize database
        logger.info("Initializing database...")
        db_init_result = initialize_database(seed=True)

        if db_init_result['status'] == 'success':
            logger.info("✓ Database initialization successful")
            # Get database info
            db_info = get_database_info()
            if db_info['status'] == 'healthy':
                logger.info(f"✓ Database healthy: {db_info['tables']}")
        else:
            logger.warning(f"⚠ Database initialization warning: {db_init_result}")

        print("📚 Documentação disponível em: http://localhost:8000/docs")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Executado ao encerrar a aplicação."""
        print("🛑 Motor Biomecânico encerrado")

    return app


# ========== INSTÂNCIA DA APP ==========

app = create_app()

# ========== ENTRYPOINT ==========

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Em produção: False
        log_level="info",
    )
