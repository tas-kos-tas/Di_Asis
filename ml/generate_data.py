import random
import os
import sys
import json

# Pridedame root kataloga i sys.path, kad galetume importuoti 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, DesignStyle

# Originali psichologijos baze (Pildyta naujomis industrijomis ir žodžiais)
COLOR_PSYCHOLOGY_RULES = {
    "trust_calm": {
        "keywords": ["trust", "calm", "corporate", "medical", "secure", "professional", "patikimas", "saugus", "rimtas", "institucija", "teisingumas", "stabilus"],
        "industries": ["finance", "healthcare", "ngo", "services", "real_estate"],
        "header_fonts": ["Open Sans", "Roboto", "Helvetica Neue", "Montserrat"],
        "body_fonts": ["Lato", "Inter", "Source Sans Pro"],
        "colors": ["#003049", "#023E8A", "#0077B6", "#0096C7", "#48CAE4", "#F8F9FA", "#E9ECEF", "#DEE2E6"]
    },
    "energy_action": {
        "keywords": ["energy", "passion", "action", "food", "youth", "bold", "sportas", "greitis", "motyvacija", "dinamiška", "skanu", "veiksmas", "ugnis"],
        "industries": ["entertainment", "food", "manufacturing", "technology"],
        "header_fonts": ["Impact", "Oswald", "Anton", "Bebas Neue"],
        "body_fonts": ["Roboto", "Open Sans", "PT Sans"],
        "colors": ["#D62828", "#E63946", "#F4A261", "#E76F51", "#9D0208", "#FFBA08", "#FAA307", "#212529"]
    },
    "nature_health": {
        "keywords": ["nature", "healing", "fresh", "eco", "organic", "growth", "gamta", "sveikata", "tvarumas", "ekologija", "švarus", "medicina", "harmonija"],
        "industries": ["healthcare", "ecology", "logistics"],
        "header_fonts": ["Lora", "Merriweather", "Playfair Display", "Zilla Slab"],
        "body_fonts": ["Nunito", "Quicksand", "Work Sans"],
        "colors": ["#2A9D8F", "#2D6A4F", "#40916C", "#52B788", "#74C69D", "#D8F3DC", "#FFE8D6", "#B7B7A4"]
    },
    "luxury_minimal": {
        "keywords": ["luxury", "minimal", "elegant", "premium", "balance", "neutral", "prabanga", "mada", "estetika", "grožis", "aukšta kokybė", "modernus"],
        "industries": ["fashion", "real_estate", "services", "technology"],
        "header_fonts": ["Cinzel", "Didot", "Cormorant Garamond", "Bodoni Moda"],
        "body_fonts": ["Montserrat", "Raleway", "Jost"],
        "colors": ["#000000", "#212121", "#424242", "#F5F5F5", "#FFFFFF", "#D4AF37", "#C5B358", "#B0BEC5"]
    },
    "creative_playful": {
        "keywords": ["creative", "playful", "warm", "optimistic", "fun", "kids", "kūryba", "švietimas", "inovacijos", "menas", "edukacija", "linksmas"],
        "industries": ["education", "entertainment", "other"],
        "header_fonts": ["Fredoka One", "Pacifico", "Baloo 2", "Chewy"],
        "body_fonts": ["Comic Neue", "Nunito", "Varela Round"],
        "colors": ["#FF006E", "#8338EC", "#3A86FF", "#FFBE0B", "#FB5607", "#FFD166", "#118AB2", "#06D6A0"]
    }
}

def generate_synthetic_data(num_records=1000):
    """
    Generuoja sintetinius dizaino stiliu duomenis ir issaugo juos i DB.
    """
    app = create_app()
    
    with app.app_context():
        # Isvalome senus duomenis
        db.session.query(DesignStyle).delete()
        
        generated_styles = []
        categories = list(COLOR_PSYCHOLOGY_RULES.keys())
        
        for _ in range(num_records):
            category = random.choice(categories)
            rules = COLOR_PSYCHOLOGY_RULES[category]
            
            # Paimame 2-3 žodžius ir sujungiame, kad tekstas būtų turtingesnis AI mokymui
            chosen_keywords = random.sample(rules["keywords"], k=random.randint(2, 3))
            mood_string = ", ".join(chosen_keywords)
            
            industry = random.choice(rules["industries"])
            h_font = random.choice(rules["header_fonts"])
            b_font = random.choice(rules["body_fonts"])
            
            palette = random.sample(rules["colors"], min(5, len(rules["colors"])))
            # SAUGUS FORMATAVIMAS: paverčiame Python sąrašą į JSON tekstą, kad išvengtume ankstesnių klaidų DB
            colors_json = json.dumps(palette) 
            
            new_style = DesignStyle(
                mood_keyword=mood_string,
                industry=industry,
                header_font=h_font,
                body_font=b_font,
                color_palette=colors_json,
                color_histogram=None
            )
            generated_styles.append(new_style)
        
        db.session.bulk_save_objects(generated_styles)
        db.session.commit()
        
        print(f"Sekmingai sugeneruota ir isaugota {num_records} dizaino stiliu i duomenu baze!")

if __name__ == "__main__":
    # Padidiname skaičių iki 1000, kad AI geriau išmoktų naujus žodžius
    generate_synthetic_data(1000)