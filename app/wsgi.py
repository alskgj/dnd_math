from app import app, setup_logging

if __name__ == '__main__':
    setup_logging()
    app.run()