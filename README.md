#  YouTube Analytics Dashboard

Aplicație interactivă dezvoltată în **Python (Streamlit)** și **SAS**, care analizează performanța celor mai mari canale YouTube la nivel global.

---

##  Funcționalități principale

-  **Statistici descriptive** asupra dataset-ului
-  **Filtrare interactivă** (categorie, țară, dimensiune canal)
-  **Vizualizări multiple**:
  - Matplotlib
  - Seaborn
  - Plotly (interactiv)
-  **Preprocesare date**:
  - tratarea valorilor lipsă
  - detectarea outlierilor (IQR)
  - encoding variabile categoriale
-  **Machine Learning**:
  - model de regresie
  - analiză corelații
-  **Metrici și evaluare model**
-  **Concluzii asupra datelor**

---

##  Structura aplicației


youtube_app/
│
├── Home.py
├── pages/
│ ├── Date_si_Statistici.py
│ ├── Filtrare_Interactiva.py
│ ├── Vizualizari.py
│ ├── Preprocesare.py
│ ├── Machine_Learning.py
│ ├── Regresie_Metrici.py
│ └── Concluzii.py
│
├── global_youtube_statistics.csv
├── requirements.txt
└── style.py


---

##  Dataset

Dataset-ul conține informații despre **995 de canale YouTube**, incluzând:

- subscribers  
- video views  
- earnings (monthly & yearly)  
- uploads  
- category  
- country  

---

##  Tehnologii utilizate

- Python  
- Streamlit  
- Pandas / NumPy  
- Matplotlib / Seaborn / Plotly  
- Scikit-learn  
- Statsmodels  
- SAS (pentru prelucrare și analiză avansată)  

---

##  Rulare aplicație

Pentru rulare locală:

```bash
streamlit run Home.py


Proiect realizat în cadrul cursului Pachete Software de către Sfetcu Andreea și Scînteie Mălina, având ca obiectiv dezvoltarea unei aplicații interactive pentru analiza datelor unei organizații, utilizând Python și SAS.
