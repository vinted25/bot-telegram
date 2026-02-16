# KN SHOP — Résumé complet du bot Telegram

Document de référence pour tout savoir sur le bot et préparer une mise à jour.

---

## 1. Rôle du bot

**KN SHOP** est un **bot Telegram e‑commerce** pour un shop de **produits digitaux** (revente) :
- **Gaming** : comptes Fortnite, Valorant, CS2, R6, Minecraft, Steam, etc.
- **Streaming** : Netflix, Disney+, Prime, HBO, Spotify, Crunchyroll, etc.
- **Services** : VPN, logiciels, spoofers, générateurs, etc.

Le bot **ne gère pas les paiements** : il affiche le catalogue, les fiches produits, et redirige vers le **support Telegram** (`SUPPORT_CONTACT`) pour commander. C’est un **vitrine + support** uniquement.

---

## 2. Ce que le bot propose (côté utilisateur)

### 2.1 Commandes

| Commande | Qui | Description |
|----------|-----|-------------|
| **`/start`** | Tout le monde | Message d’accueil + menu principal (boutons) |
| **`/marges`** | **Admins uniquement** | Liste tous les produits avec **Prix · Coût · Marge bénéfice** + marge totale |

### 2.2 Menu principal (après /start)

- **🛍️ Ouvrir le shop** → Liste de **toutes les catégories** du catalogue
- **🎬 Streaming** / **🎮 Gaming** → Catégories Streaming premium et Gaming accounts
- **💬 Discord** / **🟣 Fortnite** → Catégories Discord & Boosts, Fortnite accounts
- **💳 Paiement** → Moyens de paiement (Crypto, PayPal, RIB)
- **📸 Preuves** → Lien vers le canal vouch (`VOUCH_CHANNEL_URL`)
- **📢 Canal** → Lien vers le canal Telegram (`CANAL_SHOP_URL`)
- **📞 Contact** → Lien vers le support (`SUPPORT_CONTACT`)

### 2.3 Parcours utilisateur

1. **/start** → Menu avec boutons.
2. **Meilleures offres / Gaming / Streaming / Services** → Liste des produits de la catégorie (nom + prix), avec image de la catégorie.
3. **Tout le shop** → Image (logo ou défaut) + grille de **toutes les catégories** → même logique par catégorie.
4. Clic sur un **produit** → **Fiche produit** : image, badges, nom, **prix**, avantages (benefits), bouton **« 🛒 Commander maintenant »** (lien support).
5. **Commander** → Ouverture du chat support (Telegram). Aucun paiement dans le bot.

### 2.4 Spécificités admins

- **`/marges`** : liste des produits avec prix, coût, marge. Marge totale affichée. Si liste > 4096 caractères, envoi en plusieurs messages.
- **Fiche produit** : si l’utilisateur est **admin** (ID dans `ADMIN_IDS`), la fiche affiche en plus **Coût** et **Marge bénéfice**. Les clients ne voient pas ces infos.

---

## 3. Catalogue (CATALOG)

### 3.1 Structure

```text
CATALOG = {
    "clé_catégorie": {
        "title": "🆕 NOM AFFICHÉ",
        "image": URL ou IMAGE_URLS["..."],
        "products": [
            {
                "id": "identifiant_unique",
                "name": "Nom produit",
                "price": "X,XX€",
                "cost": "X,XX€",     // optionnel, pour marge (admin)
                "benefits": ["Avantage 1", "Avantage 2", ...],
                "badges": ["🔥 Le plus vendu", "⭐ Recommandé", ...],
                "image": URL ou IMAGE_URLS["..."]
            },
            ...
        ]
    },
    ...
}
```

- **`id`** : identifiant unique du produit (réutilisable dans plusieurs catégories).
- **`price`** : prix affiché (format `"X,XX€"`).
- **`cost`** : coût d’achat (optionnel). Utilisé pour la **marge** (prix − coût). Par défaut `0€` si absent.
- **`benefits`** : liste d’avantages affichés sous forme de puces.
- **`badges`** : petits labels au-dessus du nom (ex. « Le plus vendu », « Stock limité »).
- **`image`** : image du produit. Si absent, usage de `DEFAULT_IMAGE`.

### 3.2 Catégories existantes

| Clé | Titre affiché |
|-----|----------------|
| `streaming_premium` | 🎬 STREAMING PREMIUM |
| `abonnements_premium` | 🎧 ABONNEMENTS PREMIUM |
| `vpn_securite` | 🔐 VPN & SÉCURITÉ |
| `discord_boosts` | 💬 DISCORD & BOOSTS |
| `gaming_accounts` | 🎮 GAMING ACCOUNTS |
| `fortnite_accounts` | 🟣 FORTNITE ACCOUNTS |
| `valorant_eu` | 🔫 VALORANT (EU) |
| `reseaux_sociaux` | 📱 RÉSEAUX SOCIAUX |
| `ia_tools` | 🤖 IA & TOOLS |
| `packs` | 🎁 PACKS EXCLUSIFS |

### 3.3 Images (IMAGE_URLS)

Clés utilisées dans le catalogue :  
`fortnite`, `valorant`, `cs2`, `minecraft`, `netflix`, `disney`, `prime`, `vpn`, `premium`, `pack`, `r6`, `hbo`, `discord`, `twitch`, `roblox`, `paramount`, `clash_royale`, `cod`, `chatgpt`, `instagram`.  
`DEFAULT_IMAGE` = `premium` si pas d’image produit.

---

## 4. Configuration (en tête de `bot.py`)

| Variable | Rôle |
|----------|------|
| **`BOT_TOKEN`** | Token du bot Telegram (@BotFather). **Obligatoire** : à définir en variable d'environnement (le bot refuse de démarrer sans). |
| **`CANAL_SHOP_URL`** | Lien du canal (bouton « Rejoindre le canal ») |
| **`SUPPORT_CONTACT`** | Lien support (bouton « Commander » / « Contacter le support ») |
| **`SHOP_LOGO_PATH`** | Chemin local vers `shop_logo.png` (écran « Tout le shop ») |
| **`ADMIN_IDS`** | Liste des IDs Telegram admins (ex. `[123456789]`) pour `/marges` et marge sur fiche produit |

---

## 5. Fichiers du projet

| Fichier | Rôle |
|---------|------|
| **`bot.py`** | Tout le code du bot (config, catalogue, handlers, clavier) |
| **`requirements.txt`** | `python-telegram-bot>=22.0` |
| **`shop_logo.png`** | Logo du shop (Tout le shop, fallback images) |
| **`LANCEMENT.txt`** | Instructions pour lancer le bot (Python 3.11/3.12) |
| **`PP_BOT.txt`** | Comment changer la photo de profil du bot via @BotFather |
| **`RESUME_BOT_KN_SHOP.md`** | Ce résumé |

---

## 6. Logique technique utile pour les mises à jour

### 6.1 Callbacks (boutons)

- `main` → Menu principal  
- `shop` → Tout le shop (catégories)  
- `canal` → Canal du shop  
- `support` → Commander / Support  
- `cat:<category_key>` → Liste produits de la catégorie  
- `prod:<category_key>:<product_id>` → Fiche produit  

### 6.2 Marge bénéfice

- **`_parse_price(s)`** : `"0,15€"` → `0.15`  
- **`_format_price(x)`** : `0.15` → `"0,15€"`  
- **`_marge_produit(p)`** : `(prix, coût, marge)` avec `marge = prix - coût` (coût par défaut 0 si absent).  
- **`_collect_unique_products()`** : tous les produits uniques par `id` (une fois par produit, même s’il est dans plusieurs catégories).

### 6.3 Envoi d’images

- **`send_photo_file`** : envoi depuis un fichier local (ex. `shop_logo.png`).  
- **`send_photo_chat`** : envoi par URL.  
- Si envoi par URL échoue, fallback sur `SHOP_LOGO_PATH` ou `IMAGE_URLS["premium"]` selon le cas.

### 6.4 Handlers enregistrés

- **`/start`** → `cmd_start`  
- **`/marges`** → `cmd_marges`  
- **Tous les callbacks des boutons** → `callback_handler`  

---

## 7. Idées de mises à jour

- **Catalogue** : ajouter / modifier / supprimer des catégories ou des produits (avec `id`, `price`, `cost`, `benefits`, `badges`, `image`).  
- **Config** : changer `BOT_TOKEN`, `CANAL_SHOP_URL`, `SUPPORT_CONTACT`, `ADMIN_IDS`.  
- **Images** : modifier `IMAGE_URLS`, `DEFAULT_IMAGE`, ou utiliser `shop_logo.png` pour le « Tout le shop ».  
- **Marges** : compléter `cost` sur les produits pour des marges correctes dans `/marges` et sur les fiches admin.  
- **Textes** : adapter les messages (accueil, canal, support, fiches produits) directement dans `bot.py`.  
- **Nouvelles commandes** : ajouter un `CommandHandler` et une fonction async dédiée, puis l’enregistrer dans `main()`.  
- **Nouveaux boutons** : ajouter des `InlineKeyboardButton` dans les clavers existants ou en créer de nouveaux, et gérer les nouveaux `callback_data` dans `callback_handler`.

---

## 8. Rappel lancement

Définir le token avant de lancer (obligatoire) :

```bash
# Windows (PowerShell)
$env:BOT_TOKEN = "TON_TOKEN_ICI"

# Ou créer un fichier .env et utiliser python-dotenv si tu l'ajoutes au projet
```

Puis :

```bash
cd "c:\Users\frack\Desktop\BOT TELEGRAM"
py -3.12 -m pip install -r requirements.txt
py -3.12 bot.py
```

Arrêt : **Ctrl+C**.  
Voir `LANCEMENT.txt` pour le détail (Python 3.11/3.12, PATH, etc.).

---

*Dernière mise à jour : généré à partir de `bot.py` actuel.*
