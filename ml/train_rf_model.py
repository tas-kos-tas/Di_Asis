import os
import sys
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Pridedame root kataloga i sys.path, kad galetume importuoti 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, DesignStyle, TrainingLog

def train_rf_model():
    """
    Apmoko Random Forest modeli tekstinei klasifikacijai.
    Naudojame ta pati duomenu padalinima (random_state=42) kaip ir KNN, 
    kad palyginimas butu saziningas ir tikslus.
    """
    app = create_app()
    
    with app.app_context():
        print("1. Traukiami duomenys is duomenu bazes...")
        styles = DesignStyle.query.all()
        
        if not styles:
            print("Klaida: Duomenu baze tuscia.")
            return

        # Paruosiame X ir y lygiai taip pat kaip KNN modelyje
        X = [f"{style.mood_keyword} {style.industry}" for style in styles]
        y = [style.header_font for style in styles]

        print("2. Dalinami duomenys i mokymo ir testavimo aibes...")
        # Butina naudoti random_state=42 vienodam duomenu padalinimui
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("3. Kuriama ML grandine ir mokomas Random Forest modelis...")
        rf_hyperparameters = {
            "n_estimators": 100, # Kiek sprendimu medziu bus sukurta (Misko dydis)
            "max_depth": None,   # Medziai gali augti be apribojimu
            "random_state": 42
        }
        
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('rf', RandomForestClassifier(**rf_hyperparameters))
        ])

        # Treniruojame modeli (tai gali uztrukti sekunde ilgiau nei KNN)
        pipeline.fit(X_train, y_train)

        print("4. Atliekamas modelio testavimas...")
        predictions = pipeline.predict(X_test)
        acc = accuracy_score(y_test, predictions)
        print(f"Modelio tikslumas (Accuracy): {acc:.4f}")

        print("5. Issaugomas modelis faile...")
        model_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, 'rf_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(pipeline, f)
        print(f"Modelis isaugotas: {model_path}")

        print("6. Fiksuojami testavimo rezultatai i duomenu baze...")
        log_entry = TrainingLog(
            model_type='RandomForest',
            input_type='Text_NLP',
            hyperparameters=rf_hyperparameters,
            accuracy=acc
        )
        db.session.add(log_entry)
        db.session.commit()
        print("Eksperimento rezultatai sekmingai isaugoti 'training_logs' lenteleje.")

if __name__ == "__main__":
    train_rf_model()