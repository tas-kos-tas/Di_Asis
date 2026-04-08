import random
import os
import sys

# Pridedame root kataloga i sys.path, kad galetume importuoti 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, DesignStyle

# Spalvu psichologijos teorijos baze
COLOR_PSYCHOLOGY_RULES = {
    "trust_calm": {
        "keywords": ["trust", "calm", "corporate", "medical", "secure", "professional"],
        "industries": ["finance", "healthcare", "technology", "insurance"],
        "header_fonts": ["Open Sans", "Roboto", "Helvetica Neue", "Montserrat"],
        "body_fonts": ["Lato", "Inter", "Source Sans Pro"],
        # Melyni ir neutralus atspalviai
        "colors": ["#003049", "#023E8A", "#0077B6", "#0096C7", "#48CAE4", "#F8F9FA", "#E9ECEF", "#DEE2E6"]
    },
    "energy_action": {
        "keywords": ["energy", "passion", "action", "food", "youth", "bold"],
        "industries": ["fitness", "fast_food", "entertainment", "sports"],
        "header_fonts": ["Impact", "Oswald", "Anton", "Bebas Neue"],
        "body_fonts": ["Roboto", "Open Sans", "PT Sans"],
        # Raudoni, oranziniai atspalviai
        "colors": ["#D62828", "#E63946", "#F4A261", "#E76F51", "#9D0208", "#FFBA08", "#FAA307", "#212529"]
    },
    "nature_health": {
        "keywords": ["nature", "healing", "fresh", "eco", "organic", "growth"],
        "industries": ["agriculture", "vegan", "wellness", "sustainability"],
        "header_fonts": ["Lora", "Merriweather", "Playfair Display", "Zilla Slab"],
        "body_fonts": ["Nunito", "Quicksand", "Work Sans"],
        # Zali ir zemes atspalviai
        "colors": ["#2A9D8F", "#2D6A4F", "#40916C", "#52B788", "#74C69D", "#D8F3DC", "#FFE8D6", "#B7B7A4"]
    },
    "luxury_minimal": {
        "keywords": ["luxury", "minimal", "elegant", "premium", "balance", "neutral"],
        "industries": ["fashion", "jewelry", "architecture", "high_end_tech"],
        "header_fonts": ["Cinzel", "Didot", "Cormorant Garamond", "Bodoni Moda"],
        "body_fonts": ["Montserrat", "Raleway", "Jost"],
        # Juoda, balta, auksine, pilka
        "colors": ["#000000", "#212121", "#424242", "#F5F5F5", "#FFFFFF", "#D4AF37", "#C5B358", "#B0BEC5"]
    },
    "creative_playful": {
        "keywords": ["creative", "playful", "warm", "optimistic", "fun", "kids"],
        "industries": ["education", "toys", "creative_agency", "events"],
        "header_fonts": ["Fredoka One", "Pacifico", "Baloo 2", "Chewy"],
        "body_fonts": ["Comic Neue", "Nunito", "Varela Round"],
        # Geltoni, roziniai, violetiniai atspalviai
        "colors": ["#FF006E", "#8338EC", "#3A86FF", "#FFBE0B", "#FB5607", "#FFD166", "#118AB2", "#06D6A0"]
    }
}

def generate_synthetic_data(num_records=500):
    """
    Generuoja sintetinius dizaino stiliu duomenis ir issaugo juos i DB.
    """
    app = create_app()
    
    with app.app_context():
        # Pasirinktinai: Isvalome senus duomenis, kad nesidubliuotu jei skripta leisime kelis kartus
        db.session.query(DesignStyle).delete()
        
        generated_styles = []
        categories = list(COLOR_PSYCHOLOGY_RULES.keys())
        
        for _ in range(num_records):
            # 1. Atsitiktinai pasirenkame kategorija
            category = random.choice(categories)
            rules = COLOR_PSYCHOLOGY_RULES[category]
            
            # 2. Generuojame atsitiktines reiksmes is teorijos baseino
            mood = random.choice(rules["keywords"])
            industry = random.choice(rules["industries"])
            h_font = random.choice(rules["header_fonts"])
            b_font = random.choice(rules["body_fonts"])
            
            # 3. Sukuriame 5 spalvu palete is leistinu atspalviu
            # (Naudojame sample, kad nebutu besidubliuojanciu spalvu paleteje)
            palette = random.sample(rules["colors"], min(5, len(rules["colors"])))
            
            # 4. Sukuriame SQLAlchemy objekta
            new_style = DesignStyle(
                mood_keyword=mood,
                industry=industry,
                header_font=h_font,
                body_font=b_font,
                color_palette=palette,
                color_histogram=None # Paliekame ateiciai (Bonus balams)
            )
            generated_styles.append(new_style)
        
        # Saugome i duomenu baze
        db.session.bulk_save_objects(generated_styles)
        db.session.commit()
        
        print(f"Sekmingai sugeneruota ir isaugota {num_records} dizaino stiliu i duomenu baze!")

if __name__ == "__main__":
    generate_synthetic_data(500)