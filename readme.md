Projekto struktūra:

C:\FINAL\
├── .git/                 # (Paslėptas) GitHub ryšys ir istorija
├── .gitignore            # Katalogų ir failų ignoravimo taisyklės
├── readme.md             # Projekto dokumentacija
├── requirements.txt      # Bibliotekų sąrašas (torch, flask ir kt.)
├── run.py                # Pagrindinis aplikacijos paleidimo failas
│
├── app/                  # Programinis kodas
│   ├── __init__.py       # Paketo inicializacija
│   ├── models.py         # Duomenų bazės modeliai (SQLAlchemy)
│   └── routes.py         # Maršrutų ir užklausų logika
│
├── ml/                   # Mašininio mokymosi moduliai
│   ├── train.py          # Modelio apmokymo procesas (CUDA palaikymas)
│   └── predict.py        # Prognozavimo logika
│
├── instance/             # Konfigūracijos katalogas
│   └── site.db           # SQLite duomenų bazė
│
└── venv/                 # Virtuali aplinka