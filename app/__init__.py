from flask import Flask
from flask_migrate import Migrate  # Prideta: importuojame Migrate
from app.models import db

# Inicijuojame Migrate objekta
migrate = Migrate()

def create_app():
    """
    Inicijuoja Flask aplikacija (Factory pattern).
    Tai leidzia lengvai testuoti ir valdyti konfiguacijas.
    """
    app = Flask(__name__)
    
    # Duomenu bazes konfiguacija (naudojame SQLite vietineje 'instance' papkeje)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Prijungiame SQLAlchemy ir Migrate prie Flask aplikacijos
    db.init_app(app)
    migrate.init_app(app, db) # Prideta: sujungia Flask, SQLAlchemy ir Alembic
    
    # Cia veliau registruosime 'blueprints' (routes.py logika)
    with app.app_context():
        pass

    return app