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
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
```

4. Ouvrir l'URL locale affichee dans le terminal (en general http://localhost:8501).

## Utiliser le quiz sur iPhone (iOS)

Option recommandee sans Cloudflare (1 commande):

```powershell
.\start_ios_local.ps1
```

Puis ouvrir sur iPhone (Safari), en etant sur le meme Wi-Fi:

http://IP_DU_PC:8501

Exemple chez vous actuellement:

http://192.168.1.14:8501

Etapes simples:

1. Mettre le PC et l'iPhone sur le meme reseau Wi-Fi.
2. Lancer le quiz sur le PC (commande ci-dessus).
3. Sur le PC, recuperer l'adresse IP locale:

```powershell
ipconfig
```

4. Prendre la ligne IPv4 (exemple: 192.168.1.42).
5. Sur iPhone (Safari), ouvrir le lien:

http://192.168.1.42:8501

Astuce: Streamlit affiche aussi une ligne Network URL dans le terminal. C'est le lien a cliquer/coller depuis le telephone.

Si ca ne marche pas:

- Autoriser Python/Streamlit dans le pare-feu Windows (reseau prive).
- Verifier que le terminal Streamlit est toujours en cours d'execution.
- Desactiver temporairement un VPN sur PC/iPhone si besoin.

## Lien securise (hors de la maison)

Si vous voulez un lien public securise (HTTPS) pour ouvrir le quiz de n'importe ou, utilisez Cloudflare Tunnel.

Etapes simples:

1. Installer Cloudflared (une seule fois):

```powershell
winget install --id Cloudflare.cloudflared -e
```

2. Lancer le quiz:

```powershell
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
```

3. Dans un 2e terminal, lancer le tunnel securise:

```powershell
cloudflared tunnel --url http://localhost:8501
```

4. Copier le lien HTTPS affiche (exemple: https://xxxx.trycloudflare.com) et l'ouvrir sur iPhone.

Option ultra simple (1 commande):

```powershell
.\start_secure.ps1
```

Ce script ouvre automatiquement:

- une fenetre pour Streamlit
- une fenetre pour Cloudflared (avec le lien HTTPS a copier)

Remarques:

- Le lien est temporaire (il change a chaque lancement du tunnel).
- Garder les 2 terminaux ouverts (Streamlit + Cloudflared).
- C'est la methode la plus simple pour partager le quiz en HTTPS sans config reseau complexe.

## Depannage iOS rapide

Si Safari iPhone n'affiche pas le quiz:

- Fermer/reouvrir Safari puis recharger la page.
- Verifier que l'iPhone est sur le meme Wi-Fi que le PC (pas 4G/5G).
- Sur iPhone: Reglages > Wi-Fi > votre reseau > desactiver temporairement "Limiter le suivi de l'adresse IP".
- Verifier que VPN/proxy est desactive sur PC et iPhone.
- Verifier dans la fenetre Streamlit qu'il n'y a pas d'erreur au chargement.

## Fonctionnalites

- Questions en francais organisees par chapitres.
- Filtre par chapitre et difficulte.
- Nombre de questions configurable.
- Ordre des questions et des reponses melange a chaque nouveau quiz.
- Correction immediate avec explication.
- Resume final avec revision des erreurs.

## Fichiers principaux

- app.py : interface et logique du quiz.
- data/questions_fr.json : banque de questions.
- requirements.txt : dependances Python.
- start_secure.ps1 : lancement en 1 commande (quiz + lien HTTPS Cloudflare).
- start_ios_local.ps1 : lancement en 1 commande pour iPhone sur le meme Wi-Fi (sans Cloudflare).
