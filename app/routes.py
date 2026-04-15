import os
import pickle
import numpy as np
import ast
import random
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
# Kad Neuroninis tinklas būtų užkraunamas tik VIENĄ kartą, kai serveris įsijungia.
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
@main.route('/', methods=['GET', 'POST'])
def index():
    """Pagrindinis puslapis ir AI prognozės logika."""
    
    # Jei modeliai dar neužkrauti (pirmas puslapio atidarymas), užkrauname juos.
    if nn_model is None:
        load_ai_models()
        
    prediction_result = None
    
    # Sukuriame tuščius kintamuosius, kad puslapis žinotų, ką atvaizduoti pirmą kartą jį atidarius
    user_keywords = ""
    user_industry = ""
    
    # Jei vartotojas paspaudė mygtuką "Generuoti" (Išsiuntė POST užklausą)
    if request.method == 'POST':
        # --- A. DUOMENŲ SURINKIMAS ---
        user_keywords = request.form.get('keywords', '')
        user_industry = request.form.get('industry', '')
        
        # --- B. DUOMENŲ PARUOŠIMAS MODELIUI ---
        combined_text = f"{user_keywords} {user_industry}"
        X_input = vectorizer.transform([combined_text]).toarray()
        
        # --- C. AI PROGNOZĖ ---
        predictions = nn_model.predict(X_input, verbose=0)
        predicted_class_id = np.argmax(predictions[0]) 
        predicted_font = label_encoder.inverse_transform([predicted_class_id])[0] 
        
        # --- D. DUOMENŲ BAZĖS UŽKLAUSA ---
        # Užuot ėmę pirmą pasitaikiusį (.first()), ištraukiame VISUS tinkančius (.all())
        matching_styles = DesignStyle.query.filter_by(header_font=predicted_font).all()
        
        # Jei radome bent vieną, atsitiktinai pasirenkame vieną iš jų!
        if matching_styles:
            style_db = random.choice(matching_styles)
        else:
            style_db = None
        
        # --- E. REZULTATO FORMATAVIMAS HTML PUSLAPIUI ---
        if style_db:
            raw_colors = style_db.color_palette
            
            if isinstance(raw_colors, list):
                colors = raw_colors
            elif isinstance(raw_colors, str):
                try:
                    if '[' in raw_colors:
                        colors = ast.literal_eval(raw_colors)
                    else:
                        colors = [c.strip() for c in raw_colors.split(',')]
                except:
                    colors = ["#2c3e50", "#e74c3c"]
            else:
                colors = ["#2c3e50", "#e74c3c"]
                
            prediction_result = {
                'header_font': predicted_font,
                'body_font': style_db.body_font,
                'colors': colors,
                'industry': user_industry,
                'keywords': user_keywords
            }
            
    # Atvaizduojame index.html šabloną ir perduodame jam REZULTATĄ bei IŠSAUGOTUS DUOMENIS (State Persistence)
    return render_template('index.html', 
                           result=prediction_result, 
                           keywords=user_keywords, 
                           selected_industry=user_industry)

from app.models import TrainingLog
import ast

@main.route('/logs')
def view_logs():
    # Ištraukiame visus testų rezultatus iš DB, surikiuotus pagal geriausią tikslumą
    logs = TrainingLog.query.order_by(TrainingLog.accuracy.desc()).all()
    
    # Kadangi hiperparametrai DB greičiausiai išsaugoti kaip tekstas (JSON/Dict), paverčiame juos atgal
    parsed_logs = []
    for log in logs:
        try:
            hp = ast.literal_eval(log.hyperparameters) if isinstance(log.hyperparameters, str) else log.hyperparameters
        except:
            hp = {}
            
        parsed_logs.append({
            'id': log.id,
            'model_type': log.model_type,
            # Saugus apvalinimas: patikriname, ar accuracy ir loss nėra tušti
            'accuracy': round(log.accuracy * 100, 2) if log.accuracy is not None else '-',
            'loss': round(log.loss, 4) if log.loss is not None else '-',
            'units': hp.get('hidden_units', '-'),
            'lr': hp.get('learning_rate', '-'),
            'batch': hp.get('batch_size', '-')
        })
        
    return render_template('logs.html', logs=parsed_logs)