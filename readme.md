# AI Dizaino Asistentas

Tai yra baigiamojo darbo projektas – išmani internetinė aplikacija, kuri naudoja mašininį mokymąsi (Machine Learning), kad pagal vartotojo įvestas emocijas ir raktažodžius sugeneruotų optimalų prekės ženklo vizualinį identitetą (šriftus ir spalvų paletes).

## Technologijų stekas
* **Backend:** Python, Flask, SQLAlchemy
* **Frontend:** HTML5, CSS3, JavaScript (dinaminis spalvų šviesumo skaičiavimas)
* **Machine Learning:** Keras (Neuroniniai tinklai), Scikit-Learn (TF-IDF Vectorizer, Random Forest, KNN palyginimui)
* **Duomenų bazė:** SQLite (Flask-Migrate)

## Projekto Architektūra

FINAL/
├── analytics_charts/           # Modelio vertinimo ir analitikos grafikai (tyrimo rezultatams)
│   ├── 1_f1_scores.png         # F1 įverčių palyginimo grafikas skirtingiems algoritmams
│   ├── 2_confusion_matrix.png  # Klasifikavimo klaidų matrica (Confusion Matrix)
│   ├── 3_hyperparameter_optimization.png # Hiperparametrų optimizavimo rezultatų vizualizacija
│   └── 4_data_distribution.png # Mokymo duomenų pasiskirstymo analizė
│
├── app/                        # Pagrindinė internetinės aplikacijos (Flask) logika
│   ├── static/                 # Statiniai failai (Vartotojo sąsajos išvaizda ir dinamika)
│   │   ├── css/                # Stilių failai (pvz., style.css - išdėstymas, spalvos)
│   │   ├── images/             # Paveikslėliai (pvz., header-bg.jpg - banerio fonas)
│   │   └── js/                 # JavaScript kodas (pvz., main.js - šviesumo algoritmas, interaktyvumas)
│   ├── templates/              # HTML šablonai
│   │   └── index.html          # Pagrindinis ir vienintelis vartotojo sąsajos langas
│   ├── __init__.py             # Flask aplikacijos inicializavimas ir konfigūracijų užkrovimas
│   ├── models.py               # SQLALchemy duomenų bazės lentelių struktūros modeliai
│   └── routes.py               # Sistemos „smegenys“: jungia vartotojo įvestį, AI modelį ir duomenų bazę
│
├── instance/                   # Izoliuotų, lokalių duomenų aplankas
│   └── site.db                 # SQLite duomenų bazė (saugo sugeneruotas spalvų paletes)
│
├── migrations/                 # Duomenų bazės versijų kontrolė (Alembic / Flask-Migrate)
│   ├── alembic.ini             # Migracijų įrankio konfigūracijos failas
│   └── versions/               # Konkretūs duomenų bazės schemos pakeitimų istorijos failai
│
├── ml/                         # Mašininio mokymosi (Machine Learning) laboratorija
│   ├── saved_models/           # Ištreniruoti ir darbui paruošti modeliai
│   │   ├── best_nn_model.keras # Pagrindinis giliai mokytas neuroninis tinklas (Keras)
│   │   ├── knn_model.pkl       # K-artimiausių kaimynų (KNN) modelis (palyginimui/eksperimentams)
│   │   ├── rf_model.pkl        # Atsitiktinių miškų (Random Forest) modelis (palyginimui/eksperimentams)
│   │   └── nn_tools.pkl        # Teksto ir klasių vertėjai (TF-IDF Vectorizer, LabelEncoder)
│   ├── generate_analytics.py   # Skriptas, generuojantis mokslinius grafikus į analytics_charts aplanką
│   ├── generate_data.py        # Skriptas sintetiniams dizaino/emocijų duomenims generuoti
│   ├── predict.py              # Savarankiškas įrankis AI modelio testavimui be web serverio
│   ├── train.py                # Valdantysis skriptas, automatizuojantis modelių mokymo procesus
│   ├── train_nn_model.py       # Skriptas, skirtas treniruoti ir optimizuoti neuroninį tinklą
│   ├── train_rf_model.py       # Skriptas, skirtas treniruoti atsitiktinių miškų modelį
│   ├── train_simple_model.py   # Skriptas bazinių modelių (pvz., KNN) treniravimui
│   └── training_data.csv       # Sugeneruotas duomenų rinkinys, iš kurio mokėsi visi modeliai
│
├── .env                        # Aplinkos kintamieji (slaptažodžiai, API raktai - saugumo praktika)
├── .gitignore                  # Taisyklės Git sistemai (nurodo, kokių failų nekelti į GitHub)
├── readme.md                   # Pagrindinė projekto dokumentacija (GitHub puslapiui)
├── requirements.txt            # Visų projektui reikalingų Python bibliotekų sąrašas
└── run.py                      # Aplikacijos paleidimo failas (įjungia Flask serverį)

## Kaip veikia AI modelis?
1. Vartotojas įveda raktažodžius (pvz., "minimalizmas, ramybė").
2. Tekstas paverčiamas į skaitinę išraišką naudojant `TF-IDF`.
3. Ištreniruotas neuroninis tinklas (`best_nn_model.keras`) išanalizuoja duomenis ir nuspėja tinkamiausią šrifto kategoriją.
4. Sistema atsitiktiniu būdu ištraukia suderintą spalvų paletę iš duomenų bazės, priklausančią AI parinktai kategorijai.

## Analitika ir tyrimai
Projekto kūrimo metu buvo atlikti skirtingų algoritmų (Neural Network, Random Forest, KNN) palyginimai. Rezultatų grafikai ir klaidų matricos pateikiami `analytics_charts/` aplanke.

---
*Sukūrė: tas-kos-tas*