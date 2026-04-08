from app import create_app
from app.models import db

# Sukuriame aplikacijos instancija
app = create_app()

if __name__ == '__main__':
    # Pries paleidziant serveri, patikriname ir sukuriame DB lenteles
    with app.app_context():
        db.create_all()
        print("Duomenu baze sekmingai inicializuota!")
    
    # Paleidziame aplikacija debug rezimu
    app.run(debug=True)