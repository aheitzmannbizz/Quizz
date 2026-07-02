# Quiz Memento Militaire (FR)

Application locale de quiz en francais basee sur le livret photo fourni.

## Lancer l'application

1. Ouvrir un terminal dans le dossier du projet.
2. Installer les dependances:

```powershell
pip install -r requirements.txt
```

3. Demarrer l'application:

```powershell
streamlit run app.py
```

4. Ouvrir l'URL locale affichee dans le terminal (en general http://localhost:8501).

## Fonctionnalites

- Questions en francais organisees par chapitres.
- Filtre par chapitre et difficulte.
- Nombre de questions configurable.
- Ordre des questions et des reponses melange a chaque nouveau quiz.
- Correction immediate avec explication.
- Resume final avec revision des erreurs.

## Fichiers principaux

- `app.py` : interface et logique du quiz.
- `data/questions_fr.json` : banque de questions.
- `requirements.txt` : dependances Python.
