# Déployer le bot KN SHOP 24/7 (sans allumer ton PC)

Le bot peut tourner en continu sur un hébergeur cloud. Voici plusieurs options.

---

## ⚠️ Important

- **Une seule instance** du bot doit tourner (polling Telegram). Si tu le déploies en ligne, **ne le lance plus sur ton PC**.
- Configure la variable d'environnement **`BOT_TOKEN`** avec ton token Telegram (@BotFather) sur chaque plateforme.

---

## 1. Railway (simple, gratuit au début)

1. Pousse ton projet sur **GitHub** (crée un repo, puis `git add .` / `git commit` / `git push` depuis le dossier du bot).
2. Va sur [railway.app](https://railway.app) et connecte-toi avec GitHub.
3. **New Project** → **Deploy from GitHub repo** → choisis le dépôt du bot.
3. Railway détecte le `Procfile` : le service sera un **worker** qui exécute `python -u bot.py`.
4. **Variables** : ajoute `BOT_TOKEN` = ton token (ex. `8511148818:AAH...`).
5. Déploie. Le bot tourne tant que le projet est actif.

**Build** : si besoin, définis **Build Command** = `pip install -r requirements.txt` et **Root Directory** = dossier du bot.

---

## 2. Render (Background Worker)

1. Pousse le bot sur **GitHub** si ce n’est pas déjà fait.
2. Va sur [render.com](https://render.com) → **Dashboard** → **New** → **Background Worker**.
3. Connecte le dépôt GitHub qui contient le bot.
3. **Build Command** : `pip install -r requirements.txt`  
   **Start Command** : `python -u bot.py`
4. **Environment** : ajoute `BOT_TOKEN` = ton token.
5. Crée le worker. Une fois déployé, le bot tourne 24/7.

Les Background Workers Render peuvent être payants selon le plan. Vérifie la grille tarifaire.

---

## 3. Docker sur un VPS (ionos, OVH, Hetzner, etc.)

Sur un VPS Linux avec Docker installé :

```bash
# Cloner ou copier le projet, puis :
cd "BOT TELEGRAM"

# Construire l'image
docker build -t knshop-bot .

# Lancer le conteneur (remplace TOKEN par ton vrai token)
docker run -d --restart unless-stopped -e BOT_TOKEN="TON_TOKEN" --name knshop-bot knshop-bot
```

Le bot redémarre tout seul si le serveur reboot (`--restart unless-stopped`).

---

## 4. Oracle Cloud (VPS gratuit)

Oracle propose des VPS **toujours gratuits** (Always Free).

1. Crée un compte sur [cloud.oracle.com](https://cloud.oracle.com) et provisionne une instance **Always Free** (ex. VM.Standard.E2.1.Micro).
2. SSH dans la VM, installe Python 3.10+ et les deps :
   ```bash
   sudo apt update && sudo apt install -y python3 python3-pip
   pip3 install -r requirements.txt
   ```
3. Copie `bot.py` et `requirements.txt` sur la VM (scp, git, etc.).
4. Lance le bot en arrière-plan :
   ```bash
   nohup python3 -u bot.py > bot.log 2>&1 &
   ```
   Ou utilise **systemd** pour un service propre qui redémarre au boot (tu peux créer un fichier `knshop-bot.service`).

Pense à définir `BOT_TOKEN` :
```bash
export BOT_TOKEN="ton_token"
python3 -u bot.py
```

---

## 5. Fly.io

1. Installe [flyctl](https://fly.io/docs/hands-on/install-flyctl/) et connecte-toi.
2. Dans le dossier du bot : `fly launch` (choisis une région, ne pas attacher de BDD).
3. Ajoute le secret : `fly secrets set BOT_TOKEN=ton_token`
4. `fly deploy` pour construire et déployer le Dockerfile.

Le bot tourne sur Fly tant que l’app est active (offre gratuite limitée).

---

## Récap

| Option        | Coût               | Difficulté |
|---------------|--------------------|------------|
| Railway       | Gratuit (limites)  | Facile     |
| Render        | Variable           | Facile     |
| Docker (VPS)  | Coût du VPS       | Moyen      |
| Oracle Free   | Gratuit            | Moyen      |
| Fly.io        | Gratuit (limites)  | Moyen      |

Une fois déployé, le bot KN SHOP tourne sans que ton PC soit allumé.
