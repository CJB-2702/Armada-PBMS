from app import create_app
from app.utils.logger import get_logger

logger = get_logger()

if __name__ == '__main__':
    try:
        app = create_app()
        logger.info('Starting application')
        app.run(debug=True)
    except Exception as e:
        logger.error('Application failed to start', extra={'log_data': {'error': str(e)}})
        raise 