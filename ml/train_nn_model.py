import os
import sys
import pickle
import numpy as np

# Nustatome Keras backend i PyTorch pries importuojant keras
os.environ["KERAS_BACKEND"] = "torch"
import keras
from keras import layers, models, optimizers

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Pridedame root kataloga i sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, DesignStyle, TrainingLog

def train_neural_network():
    """
    Kuria ir testuoja Keras neuroninius tinklus.
    Atlieka hiperparametrų testavima (Grid Search) ir issaugo geriausia modeli.
    """
    app = create_app()
    
    with app.app_context():
        print("1. Traukiami duomenys is duomenu bazes...")
        styles = DesignStyle.query.all()
        if not styles:
            print("Klaida: Duomenu baze tuscia.")
            return

        # Paruosiame tekstus (X) ir taikinius (y)
        X_text = [f"{style.mood_keyword} {style.industry}" for style in styles]
        y_text = [style.header_font for style in styles]

        print("2. Vektorizuojamas tekstas ir koduojami label'ai...")
        # Vektorizuojame teksta
        vectorizer = TfidfVectorizer()
        X_vectors = vectorizer.fit_transform(X_text).toarray() # Keras reikalauja tankiu masyvu (dense arrays)
        
        # Paverciame sriftu pavadinimus i skaicius (0, 1, 2...)
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y_text)
        
        num_classes = len(label_encoder.classes_)
        input_dim = X_vectors.shape[1]

        # Daliname i mokymo (80%) ir testavimo (20%) aibes
        X_train, X_test, y_train, y_test = train_test_split(
            X_vectors, y_encoded, test_size=0.2, random_state=42
        )

        print("3. Pradedamas hiperparametru testavimo ciklas...")
        # Apibreziame parametrus testavimui
        hidden_units_options = [32, 64, 128]
        learning_rates = [0.01, 0.005, 0.001]
        batch_sizes = [16, 32, 64]
        epochs = 10
        
        best_accuracy = 0
        best_model = None

        # Sukame ciklus per visus parametru derinius
        for units in hidden_units_options:
            for lr in learning_rates:
                for batch in batch_sizes:
                    print(f"\n--- Testuojama: Units={units}, LR={lr}, Batch={batch} ---")
                    
                    # Architekturos kurimas
                    model = models.Sequential([
                        layers.Input(shape=(input_dim,)),
                        layers.Dense(units, activation='relu'),
                        layers.Dropout(0.3), # Sumazina persimokymo rizika
                        layers.Dense(num_classes, activation='softmax') # Softmax klasifikacijai
                    ])
                    
                    # Kompiliuojame modeli
                    optimizer = optimizers.Adam(learning_rate=lr)
                    model.compile(
                        optimizer=optimizer,
                        loss='sparse_categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    # Treniruojame
                    model.fit(
                        X_train, y_train,
                        epochs=epochs,
                        batch_size=batch,
                        verbose=0 # Nerodome kiekvieno epoch'o, kad neuzsiukslinti terminalo
                    )
                    
                    # Testuojame
                    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
                    print(f"Rezultatas -> Accuracy: {test_acc:.4f}, Loss: {test_loss:.4f}")
                    
                    # Saugome log'a i duomenu baze
                    hyperparams = {
                        "hidden_units": units,
                        "learning_rate": lr,
                        "batch_size": batch,
                        "epochs": epochs
                    }
                    log_entry = TrainingLog(
                        model_type='FeedForwardNN',
                        input_type='Text_NLP',
                        hyperparameters=hyperparams,
                        accuracy=float(test_acc),
                        loss=float(test_loss)
                    )
                    db.session.add(log_entry)
                    
                    # Tikriname, ar tai geriausias modelis
                    if test_acc > best_accuracy:
                        best_accuracy = test_acc
                        best_model = model

        db.session.commit()
        print("\n4. Visi eksperimentai baigti ir isaugoti duomenu bazeje!")

        print("5. Saugomas geriausias modelis ir pagalbiniai irankiai...")
        model_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        
        # Saugome Keras modeli
        best_model.save(os.path.join(model_dir, 'best_nn_model.keras'))
        
        # Saugome vektorizatoriu ir encoderi (butina, kad atkurti prognozes Flaske)
        with open(os.path.join(model_dir, 'nn_tools.pkl'), 'wb') as f:
            pickle.dump({'vectorizer': vectorizer, 'label_encoder': label_encoder}, f)
            
        print(f"Geriausias modelis isaugotas! Geriausias tikslumas: {best_accuracy:.4f}")

if __name__ == "__main__":
    train_neural_network()