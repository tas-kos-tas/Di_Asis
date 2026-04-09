import os
import pickle
import numpy as np
import ast
from flask import Blueprint, render_template, request

# 1. Priverčiame Keras naudoti PyTorch variklį (backend) PRIEŠ importuojant pačią biblioteką.
# Tai išsprendžia mūsų anksčiau turėtas NumPy versijų suderinamumo problemas.
os.environ["KERAS_BACKEND"] = "torch"
import keras

from app.models import DesignStyle

# 2. Sukuriame Blueprint. Tai yra Flask įrankis, leidžiantis grupuoti maršrutus (routes).
# Taip išlaikome kodą švarų ir atskirtą nuo pagrindinio serverio failo (__init__.py).
main = Blueprint('main', __name__)

# 3. Sukuriame globalius kintamuosius AI modeliams.
# Kodėl globalius? Kad Neuroninis tinklas būtų užkraunamas tik VIENĄ kartą, kai serveris įsijungia.
# Jei to nepadarytume, modelis būtų kraunamas iš naujo po kiekvieno vartotojo mygtuko paspaudimo (tai labai sulėtintų svetainę).
nn_model = None
vectorizer = None
label_encoder = None

def load_ai_models():
    """Ši funkcija nuskaito išsaugotus .keras ir .pkl failus iš kietojo disko į operatyviąją atmintį (RAM)."""
    global nn_model, vectorizer, label_encoder
    
    # Dinamiškai surandame kelią iki 'ml/saved_models' aplanko
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml', 'saved_models'))
    
    try:
        # Užkrauname patį Neuroninį Tinklą (Keras)
        nn_model = keras.models.load_model(os.path.join(model_dir, 'best_nn_model.keras'))
        
        # Užkrauname teksto vertėją (Vectorizer) ir etikečių iškoduotoją (Label Encoder)
        with open(os.path.join(model_dir, 'nn_tools.pkl'), 'rb') as f:
            tools = pickle.load(f)
            vectorizer = tools['vectorizer']
            label_encoder = tools['label_encoder']
            
        print("✅ AI modeliai sėkmingai užkrauti ir paruošti darbui!")
    except Exception as e:
        print(f"❌ Klaida užkraunant AI modelius: {e}")

# 4. Apibrėžiame pagrindinį puslapį ('/').
# methods=['GET', 'POST'] reiškia, kad puslapis gali ir RODYTI vaizdą (GET), ir PRIIMTI duomenis iš formos (POST).
@main.route('/', methods=['GET', 'POST'])
def index():
    """Pagrindinis puslapis ir AI prognozės logika."""
    
    # Jei modeliai dar neužkrauti (pirmas puslapio atidarymas), užkrauname juos.
    if nn_model is None:
        load_ai_models()
        
    prediction_result = None
    
    # Jei vartotojas paspaudė mygtuką "Generuoti" (Išsiuntė POST užklausą)
    if request.method == 'POST':
        # --- A. DUOMENŲ SURINKIMAS ---
        # Paimame tai, ką vartotojas įvedė HTML formoje (žiūrime į 'name' atributus iš index.html)
        user_keywords = request.form.get('keywords', '')
        user_industry = request.form.get('industry', '')
        
        # --- B. DUOMENŲ PARUOŠIMAS MODELIUI ---
        # Sujungiame žodžius į vieną eilutę (taip pat, kaip darėme treniruojant modelį)
        combined_text = f"{user_keywords} {user_industry}"
        # Paverčiame tekstą į skaičių masyvą (TF-IDF matrica)
        X_input = vectorizer.transform([combined_text]).toarray()
        
        # --- C. AI PROGNOZĖ ---
        # Paduodame skaičius Neuroniniam Tinklui ir gauname tikimybes
        predictions = nn_model.predict(X_input, verbose=0)
        
        # Randame indekso numerį, kuris turi didžiausią tikimybę (argmax)
        predicted_class_id = np.argmax(predictions[0]) 
        
        # Paverčiame skaičių (pvz., 3) atgal į šrifto pavadinimą (pvz., "Cinzel")
        predicted_font = label_encoder.inverse_transform([predicted_class_id])[0] 
        
        # --- D. DUOMENŲ BAZĖS UŽKLAUSA ---
        # AI atspėjo šriftą. Dabar ieškome duomenų bazėje pirmo pasitaikiusio dizaino stiliaus,
        # kuris naudoja šį atspėtą šriftą, kad galėtume ištraukti su juo suderintas spalvas.
        style_db = DesignStyle.query.filter_by(header_font=predicted_font).first()
        
        # --- E. REZULTATO FORMATAVIMAS HTML PUSLAPIUI ---
        if style_db:
            try:
                # Spalvos duomenų bazėje saugomos kaip tekstas: "['#FF0000', '#00FF00']"
                # ast.literal_eval saugiai paverčia šį tekstą į tikrą Python sąrašą (list)
                colors = ast.literal_eval(style_db.color_palette)
            except:
                colors = ["#000000", "#FFFFFF"] # Atsarginis variantas, jei įvyktų klaida
                
            # Supakuojame viską į vieną žodyną (dictionary), kurį išsiųsime į HTML
            prediction_result = {
                'header_font': predicted_font,
                'body_font': style_db.body_font,
                'colors': colors,
                'industry': user_industry,
                'keywords': user_keywords
            }
            
    # Atvaizduojame index.html šabloną ir paduodame jam mūsų rezultatą (jei jis yra)
    return render_template('index.html', result=prediction_result)