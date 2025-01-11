"""Script para verificar la configuración del sistema"""
import sys
import redis
from uruz.config import settings
from uruz.utils.logging import logger

def check_redis():
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        r.ping()
        return True
    except redis.ConnectionError:
        return False

def check_environment():
    checks = {
        "Redis": check_redis(),
        "OpenAI API Key": bool(settings.OPENAI_API_KEY),
        "Database URL": bool(settings.DATABASE_URL),
    }
    
    all_passed = all(checks.values())
    
    print("\nVerificación del Sistema:")
    print("------------------------")
    for service, status in checks.items():
        print(f"{service}: {'✓' if status else '✗'}")
    
    if not all_passed:
        print("\n⚠️  Algunos servicios necesitan configuración")
        sys.exit(1)
    
    print("\n✓ Sistema configurado correctamente")

if __name__ == "__main__":
    check_environment() 