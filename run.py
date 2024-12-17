# Main entry point to start the app and FTP monitor.

from app import create_app, socketio
from app.routes import main

app = create_app()
app.register_blueprint(main)

if __name__ == '__main__':

    # Run the Flask app
    socketio.run(app, debug=True)
