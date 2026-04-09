import os
import sys
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Pridedame root kataloga i sys.path, kad galetume importuoti 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, DesignStyle, TrainingLog

def train_knn_model():
    """
    Apmoko KNN modeli pagal duomenu bazeje esancius dizaino stilius.
    Modelis ismoksta nuspeti 'header_font' pagal 'mood_keyword' ir 'industry'.
    """
    app = create_app()
    
    with app.app_context():
        print("1. Traukiami duomenys is duomenu bazes...")
        styles = DesignStyle.query.all()
        
        if not styles:
            print("Klaida: Duomenu baze tuscia. Pirmiausia paleiskite generate_data.py")
            return

        # Paruosiame X (pozymius/features) ir y (taikinius/targets)
        # X sujungsime raktažodi ir industrija i viena teksto eilute
        X = [f"{style.mood_keyword} {style.industry}" for style in styles]
        
        # Kaip taikini (y) paprastam modeliui naudosime srifto pavadinima
        y = [style.header_font for style in styles]

        print("2. Dalinami duomenys i mokymo (80%) ir testavimo (20%) aibes...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("3. Kuriama ML grandine (Pipeline) ir mokomas modelis...")
        # Naudojame Pipeline, kad sujungtume teksto vektorizacija su KNN algoritmu
        knn_hyperparameters = {
            "n_neighbors": 5,
            "weights": "distance"
        }
        
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('knn', KNeighborsClassifier(**knn_hyperparameters))
        ])

        # Treniruojame modeli
        pipeline.fit(X_train, y_train)

        print("4. Atliekamas modelio testavimas...")
        predictions = pipeline.predict(X_test)
        acc = accuracy_score(y_test, predictions)
        print(f"Modelio tikslumas (Accuracy): {acc:.4f}")

        print("5. Issaugomas modelis faile...")
        # Sukuriame saved_models kataloga, jei jis neegzistuoja
        model_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, 'knn_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(pipeline, f)
        print(f"Modelis isaugotas: {model_path}")

        print("6. Fiksuojami testavimo rezultatai i duomenu baze...")
        # Saugome eksperimento rezultatus 11-ai uzduociai
        log_entry = TrainingLog(
            model_type='KNN',
            input_type='Text_NLP',
            hyperparameters=knn_hyperparameters,
            accuracy=acc
        )
        db.session.add(log_entry)
        db.session.commit()
        print("Eksperimento rezultatai sekmingai isaugoti 'training_logs' lenteleje.")

if __name__ == "__main__":
    train_knn_model()