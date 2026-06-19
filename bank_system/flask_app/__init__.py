from flask import Flask

def create_app():
    app = Flask(__name__,
                static_folder='static',
                static_url_path='/',
                template_folder='templates')
    app.config['SECRET_KEY'] = 'nextgen-banking-secret-key-2026'

    from flask_app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
