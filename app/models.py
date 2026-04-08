from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inicijuojame SQLAlchemy objekta
db = SQLAlchemy()

class DesignStyle(db.Model):
    """
    Lentele skirta saugoti dizaino stilius, sriftu poras ir spalvu paletes.
    Naudosime sintetinio duomenu rinkinio saugojimui ir modelio mokymui.
    """
    __tablename__ = 'design_styles'

    id = db.Column(db.Integer, primary_key=True)
    mood_keyword = db.Column(db.String(100), nullable=False, index=True) # Pvz.: 'minimalist', 'luxury'
    industry = db.Column(db.String(100), nullable=True) # Pvz.: 'technology', 'beauty'
    
    # Sriftu poros
    header_font = db.Column(db.String(100), nullable=False)
    body_font = db.Column(db.String(100), nullable=False)
    
    # Paletes informacija (saugoma kaip JSON sarasas)
    color_palette = db.Column(db.JSON, nullable=False) # Pvz.: ["#FFFFFF", "#000000", "#E5E5E5"]
    
    # Spalvu histogramos duomenys (pakeiciame HOG pozymius dizaino kontekstui ateiciai)
    color_histogram = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        # Reprezentacija patogesniam debugingui
        return f"<DesignStyle {self.mood_keyword} - {self.header_font}>"


class TrainingLog(db.Model):
    """
    Lentele skirta saugoti ML modeliu (KNN, Neural Network) eksperimentu rezultatus.
    Butina 11-ai uzduociai (hyperparametru testavimo isvados).
    """
    __tablename__ = 'training_logs'

    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(50), nullable=False) # 'KNN' arba 'FeedForwardNN'
    input_type = db.Column(db.String(50)) # 'Dropdown' arba 'Text_NLP'
    
    # Hyperparametrai (JSON formatu del lankstumo skirtingiems modeliams)
    hyperparameters = db.Column(db.JSON, nullable=False) 
    
    # Metrikos is modelio ivertinimo
    accuracy = db.Column(db.Float, nullable=True)
    loss = db.Column(db.Float, nullable=True)
    
    # Iraso sukurimo laikas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingLog {self.model_type} - Acc: {self.accuracy}>"