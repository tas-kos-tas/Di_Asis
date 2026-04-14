import os
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

# Priverčiame Keras naudoti PyTorch variklį (suderinamumui)
os.environ["KERAS_BACKEND"] = "torch"
import keras

# Prijungiame Flask
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.models import db, DesignStyle, TrainingLog

def generate_analytics():
    app = create_app()
    with app.app_context():
        print("📊 Pradedamas analitikos generavimas...")

        # 1. Sukuriame aplanką grafikams
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analytics_charts'))
        os.makedirs(out_dir, exist_ok=True)

        # 2. Užkrauname AI įrankius ir Geriausią Modelį
        model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'saved_models'))
        try:
            nn_model = keras.models.load_model(os.path.join(model_dir, 'best_nn_model.keras'))
            with open(os.path.join(model_dir, 'nn_tools.pkl'), 'rb') as f:
                tools = pickle.load(f)
                vectorizer = tools['vectorizer']
                label_encoder = tools['label_encoder']
        except Exception as e:
            print(f"❌ Klaida kraunant modelius: {e}. Ar tikrai paleidote train_nn_model.py?")
            return

        # 3. Ištraukiame visus duomenis iš DB įvertinimui
        all_data = DesignStyle.query.all()
        texts = [f"{d.mood_keyword} {d.industry}" for d in all_data]
        true_labels_text = [d.header_font for d in all_data]

        X_test = vectorizer.transform(texts).toarray()
        y_true = label_encoder.transform(true_labels_text)

        # AI atlieka spėjimus visiems 1000 įrašų
        print("🤖 AI modelis vertina 1000 duomenų eilučių...")
        predictions = nn_model.predict(X_test, verbose=0)
        y_pred = np.argmax(predictions, axis=1)

        # 4. Skaičiuojame Metrikas (12 užduotis: Precision, Recall, F1-Score)
        # zero_division=0 apsaugo nuo perspėjimų, jei klasė neturi spėjimų
        report_dict = classification_report(y_true, y_pred, target_names=label_encoder.classes_, output_dict=True, zero_division=0)
        
        # --- GRAFIKAS 1: F1-Score pagal klases (Šriftus) ---
        print("📈 Generuojamas 1 grafikas (F1-Scores)...")
        plt.figure(figsize=(12, 6))
        f1_scores = [report_dict[cls]['f1-score'] for cls in label_encoder.classes_]
        sns.barplot(x=f1_scores, y=label_encoder.classes_, palette="viridis", hue=label_encoder.classes_, legend=False)
        plt.title('AI Modelio Tikslumas (F1-Score) pagal Šriftų Klases')
        plt.xlabel('F1-Score (0.0 - blogai, 1.0 - tobula)')
        plt.ylabel('Šriftų klasės')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, '1_f1_scores.png'))
        plt.close()

        # --- GRAFIKAS 2: Confusion Matrix (Klaidų matrica) ---
        print("📈 Generuojamas 2 grafikas (Klaidų Matrica)...")
        plt.figure(figsize=(14, 12))
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=False, cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
        plt.title('Klaidų Matrica (Confusion Matrix)\nTamsesnė spalva diagonaleje = geresnis atpažinimas')
        plt.xlabel('AI Spėjimas (Predicted)')
        plt.ylabel('Tikrasis šriftas (Actual)')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, '2_confusion_matrix.png'))
        plt.close()

        # --- GRAFIKAS 3: Hiperparametrų testavimo rezultatai (Iš duomenų bazės) ---
        print("📈 Generuojamas 3 grafikas (Hiperparametrų testavimas)...")
        logs = TrainingLog.query.all()
        if logs:
            configs = [f"U:{l.hyperparameters.get('units', 0)}|LR:{l.hyperparameters.get('learning_rate', 0)}|B:{l.hyperparameters.get('batch_size', 0)}" for l in logs]
            accuracies = [l.accuracy for l in logs]

            plt.figure(figsize=(12, 6))
            sns.lineplot(x=configs, y=accuracies, marker="o", color="coral", linewidth=2)
            plt.title('Neuroninio Tinklo Hiperparametrų Optimizacija')
            plt.xlabel('Konfigūracija (Neurons | Learning Rate | Batch Size)')
            plt.ylabel('Tikslumas (Accuracy)')
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(out_dir, '3_hyperparameter_optimization.png'))
            plt.close()

        # --- GRAFIKAS 4: Duomenų Pasiskirstymas pagal industrijas ---
        print("📈 Generuojamas 4 grafikas (Duomenų Pasiskirstymas)...")
        industries = [d.industry for d in all_data]
        plt.figure(figsize=(10, 6))
        sns.countplot(y=industries, order=list(set(industries)), palette="Set2", hue=industries, legend=False)
        plt.title('Mokymosi Duomenų Pasiskirstymas pagal Industrijas')
        plt.xlabel('Įrašų kiekis duomenų bazėje')
        plt.ylabel('Industrija')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, '4_data_distribution.png'))
        plt.close()

        print(f"✅ VISKAS BAIGTA! 4 grafikai išsaugoti aplanke: {out_dir}")
        print("--------------------------------------------------")
        print("Pagrindinės ištrauktos metrikos (Diplominio tekstui):")
        print(f"Bendras modelio tikslumas (Accuracy): {report_dict['accuracy']:.4f}")
        print(f"Makro F1-Score vidurkis: {report_dict['macro avg']['f1-score']:.4f}")

if __name__ == "__main__":
    generate_analytics()