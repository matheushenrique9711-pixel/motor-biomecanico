"""
Database initialization module.
Handles database setup, migrations, and seeding on application startup.
"""

import os
import logging
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database.config import engine, SessionLocal, init_db
from app.database.seed import seed_database

logger = logging.getLogger(__name__)


def check_database_connection() -> bool:
    """
    Check if database connection is available.
    Retries up to 5 times with increasing delays.
    """
    import time

    max_retries = 5
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("✓ Database connection established")
                return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"✗ Failed to connect to database after {max_retries} attempts: {str(e)}")
                return False

    return False


def check_tables_exist() -> bool:
    """Check if database tables already exist."""
    try:
        with engine.connect() as conn:
            # Query to check if patients table exists
            result = conn.execute(text(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='patients')"
            ))
            exists = result.scalar()
            if exists:
                logger.info("✓ Database tables already exist")
            return exists
    except Exception as e:
        logger.warning(f"Error checking tables: {str(e)}")
        return False


def run_migrations() -> bool:
    """
    Run database migrations using Alembic.
    This creates all tables defined in the ORM models.
    """
    try:
        # Import here to avoid circular imports
        from alembic.config import Config as AlembicConfig
        from alembic.command import upgrade as alembic_upgrade
        import sys
        from pathlib import Path

        backend_dir = Path(__file__).parent.parent.parent
        alembic_config_path = backend_dir / "alembic.ini"

        if not alembic_config_path.exists():
            logger.warning("alembic.ini not found, using ORM table creation instead")
            return False

        config = AlembicConfig(str(alembic_config_path))
        config.set_main_option('script_location', str(backend_dir / "alembic"))

        # Set database URL from environment
        database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://motor_user:motor_password@localhost:5432/motor_biomecanico'
        )
        config.set_main_option('sqlalchemy.url', database_url)

        # Run migrations
        alembic_upgrade(config, 'head')
        logger.info("✓ Database migrations completed successfully")
        return True

    except Exception as e:
        logger.warning(f"Migration failed: {str(e)}, falling back to ORM table creation")
        return False


def create_tables_from_orm() -> bool:
    """
    Create tables directly from SQLAlchemy ORM models.
    Fallback method when Alembic is not available.
    """
    try:
        init_db()
        logger.info("✓ Database tables created from ORM models")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create tables from ORM: {str(e)}")
        return False


def seed_if_empty() -> Dict[str, Any]:
    """
    Seed database with test data if it's empty.
    """
    try:
        db = SessionLocal()
        result = seed_database(db)
        db.close()

        if result['status'] == 'success':
            logger.info(f"✓ Database seeded: {result['statistics']}")
        else:
            logger.info(f"Database already contains data")

        return result
    except Exception as e:
        logger.error(f"✗ Seeding failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


def initialize_database(seed: bool = True) -> Dict[str, Any]:
    """
    Complete database initialization workflow.

    Args:
        seed: Whether to seed database with test data if empty

    Returns:
        Dictionary with initialization status and statistics
    """
    logger.info("=" * 60)
    logger.info("MOTOR BIOMECÂNICO - DATABASE INITIALIZATION")
    logger.info("=" * 60)

    results = {
        'status': 'success',
        'steps': {},
        'timestamp': None
    }

    from datetime import datetime
    results['timestamp'] = datetime.utcnow().isoformat()

    # Step 1: Check database connection
    logger.info("\n[1/4] Checking database connection...")
    if not check_database_connection():
        results['status'] = 'error'
        results['steps']['connection'] = 'failed'
        logger.error("Database initialization FAILED")
        return results
    results['steps']['connection'] = 'success'

    # Step 2: Check if tables exist
    logger.info("\n[2/4] Checking database schema...")
    tables_exist = check_tables_exist()
    results['steps']['schema_check'] = 'already_exists' if tables_exist else 'not_found'

    # Step 3: Create/migrate tables if needed
    logger.info("\n[3/4] Setting up database schema...")
    if not tables_exist:
        # Try Alembic migrations first
        if not run_migrations():
            # Fallback to ORM table creation
            if not create_tables_from_orm():
                results['status'] = 'error'
                results['steps']['schema_creation'] = 'failed'
                logger.error("Database initialization FAILED")
                return results
        results['steps']['schema_creation'] = 'success'
    else:
        results['steps']['schema_creation'] = 'skipped'

    # Step 4: Seed database if enabled
    if seed:
        logger.info("\n[4/4] Seeding database with test data...")
        seed_result = seed_if_empty()
        results['steps']['seeding'] = seed_result['status']
        if 'statistics' in seed_result:
            results['seed_statistics'] = seed_result['statistics']
    else:
        logger.info("\n[4/4] Skipping database seeding (seed=False)")
        results['steps']['seeding'] = 'skipped'

    logger.info("\n" + "=" * 60)
    logger.info("✓ DATABASE INITIALIZATION COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)

    return results


def get_database_info() -> Dict[str, Any]:
    """Get information about current database state."""
    try:
        db = SessionLocal()

        from sqlalchemy import text

        # Count records in each table
        result = db.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM patients) as patient_count,
                (SELECT COUNT(*) FROM clinical_cases) as case_count,
                (SELECT COUNT(*) FROM adjustment_history) as adjustment_count,
                (SELECT COUNT(*) FROM case_analyses) as analysis_count,
                (SELECT COUNT(*) FROM case_notes) as notes_count,
                (SELECT COUNT(*) FROM case_files) as files_count
        """))

        row = result.fetchone()
        db.close()

        return {
            'status': 'healthy',
            'tables': {
                'patients': row[0],
                'clinical_cases': row[1],
                'adjustment_history': row[2],
                'case_analyses': row[3],
                'case_notes': row[4],
                'case_files': row[5],
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
