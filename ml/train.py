import os

# Priverčiame Keras naudoti PyTorch variklį (backend)
os.environ["KERAS_BACKEND"] = "torch"

import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout

# Nustatome kelius, kur bus išsaugoti sumodeliuoti failai
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'saved_models')
os.makedirs(MODEL_DIR, exist_ok=True)

def train_model():
    print("Pradedamas duomenų paruošimas ir modelio mokymas...")
    
    # 1. DUOMENŲ UŽKROVIMAS
    csv_path = os.path.join(BASE_DIR, 'training_data.csv')
    
    # Tikriname, ar failas egzistuoja, prieš jį skaitant
    if os.path.exists(csv_path):
        print(f"Kraunami duomenys iš: {csv_path}...")
        df = pd.read_csv(csv_path)
    else:
        # Jei failo nėra (pirmas paleidimas), naudojame bazinį karkasą
        print("CSV failas nerastas, naudojama bazinė duomenų struktūra...")
        data = {
            'keywords': ['minimalizmas', 'prabanga auksas', 'gamta ramybė', 'technologijos ateitis', 'klasika elegancija'] * 200,
            'industry': ['fashion', 'finance', 'healthcare', 'technology', 'education'] * 200,
            'font': ['Inter', 'Playfair Display', 'Lora', 'Roboto', 'Merriweather'] * 200
        }
        df = pd.DataFrame(data)
        # Išsaugome ateičiai
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ Sukurtas naujas duomenų failas: {csv_path}")
    
    # 2. DUOMENŲ PARUOŠIMAS (Preprocessing)
    # Sujungiame raktažodžius ir industriją į vieną tekstinę eilutę (kaip tai daroma routes.py faile)
    df['combined_text'] = df['keywords'] + " " + df['industry']
    
    # Tekstą verčiame į skaičius (TF-IDF matrica)
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df['combined_text']).toarray()
    
    # Šriftų pavadinimus verčiame į skaičius (klases)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['font'])
    
    # 3. DUOMENŲ DALIJIMAS (Train / Test Split)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. NEURONINIO TINKLO ARCHITEKTŪRA (Keras)
    model = Sequential([
        Dense(128, input_dim=X.shape[1], activation='relu'),
        Dropout(0.3),  # Apsauga nuo persimokymo (Overfitting)
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(len(label_encoder.classes_), activation='softmax')  # Klasifikavimas į N šriftų
    ])
    
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    # 5. MODELIO TRENIRAVIMAS
    print("Mokomas neuroninis tinklas...")
    model.fit(X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test), verbose=1)
    
    # 6. MODELIO IR ĮRANKIŲ IŠSAUGOJIMAS
    # Išsaugome Keras modelį
    model.save(os.path.join(MODEL_DIR, 'best_nn_model.keras'))
    
    # Išsaugome Vectorizer ir LabelEncoder, kad juos galėtų naudoti routes.py
    with open(os.path.join(MODEL_DIR, 'nn_tools.pkl'), 'wb') as f:
        pickle.dump({'vectorizer': vectorizer, 'label_encoder': label_encoder}, f)
        
    print(f"✅ Modelis ir įrankiai sėkmingai išsaugoti aplanke: {MODEL_DIR}")

if __name__ == '__main__':
    train_model()