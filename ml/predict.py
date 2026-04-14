import os
import pickle
import numpy as np

# 1. PRIVALOMA: Nustatome Keras variklį (kaip ir train.py)
os.environ["KERAS_BACKEND"] = "torch"
import keras

# Nustatome kelius iki failų
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'best_nn_model.keras')
TOOLS_PATH = os.path.join(BASE_DIR, 'saved_models', 'nn_tools.pkl')

def test_prediction(user_input, industry):
    """Savarankiška funkcija testuoti modelį be Flask serverio"""
    
    # Krauname modelį ir įrankius
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TOOLS_PATH):
        print("❌ Klaida: Modelio failai nerasti!")
        return

    model = keras.models.load_model(MODEL_PATH)
    with open(TOOLS_PATH, 'rb') as f:
        tools = pickle.load(f)
        vectorizer = tools['vectorizer']
        label_encoder = tools['label_encoder']

    # Paruošiame tekstą (lygiai taip pat, kaip serveryje)
    combined_text = f"{user_input} {industry}"
    X_input = vectorizer.transform([combined_text]).toarray()

    # Atliekame prognozę
    prediction = model.predict(X_input, verbose=0)
    predicted_class = np.argmax(prediction[0])
    predicted_font = label_encoder.inverse_transform([predicted_class])[0]

    print("-" * 30)
    print(f"ĮVESTIS: {user_input} ({industry})")
    print(f"AI PROGNOZĖ (Šriftas): {predicted_font}")
    print("-" * 30)

if __name__ == "__main__":
    # Čia gali greitai patikrinti bet kokį derinį
    test_prediction("minimalizmas ir elegancija", "fashion")
    test_prediction("modernios technologijos", "technology")