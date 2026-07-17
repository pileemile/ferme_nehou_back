# Ferme de Néhou - Backend API

API REST développée avec Django REST Framework pour la gestion des réservations de la Ferme de Néhou, une chambre d'hôtes en Normandie.

## Stack technique

- **Python 3** / **Django 6.0**
- **Django REST Framework** 3.16
- **PostgreSQL** 15 (via Docker)
- **Redis** 7 (cache + broker Celery)
- **Celery** 5.6 + **django-celery-beat** (tâches asynchrones planifiées)
- **JWT** (djangorestframework_simplejwt) pour l'authentification
- **drf-spectacular** pour la documentation OpenAPI/Swagger
- **Pillow** pour le traitement d'images (photos de chambres, thumbnails)
- **qrcode / django-qrcode** pour la génération de QR codes (emails de réservation)
- **django-ratelimit**, **django-cors-headers**, **django-filter**
- **Docker / Docker Compose**

## Prérequis

- Docker et Docker Compose
- Python 3.12+ (si exécution hors Docker)

## Installation

```bash
git clone https://github.com/pileemile/ferme_nehou_back.git
cd ferme_nehou_back
docker compose up --build
```

L'API est alors disponible sur `http://localhost:8080/api/`.

### Variables d'environnement

Le `docker-compose.yml` définit déjà des valeurs par défaut pour le développement. Pour un déploiement, créez un fichier `.env` (ou surchargez les variables) avec au minimum :

```
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=...
POSTGRES_DB=ferme_nehou
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Une clé secrète peut être générée avec le script fourni :

```bash
python generate_secret_key.py
```

### Migrations

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Documentation API

Une fois le serveur lancé :

- Swagger UI : `http://localhost:8080/api/schema/swagger-ui/`
- Schéma OpenAPI brut : `http://localhost:8080/api/schema/`
- Admin Django : `http://localhost:8080/admin/`

## Structure du projet

```
app/
├── activity/            # Activités proposées (équitation, visites, etc.)
├── authentification/    # Utilisateur custom + JWT
├── customers/           # Profils clients
├── emails/              # Templates HTML + envoi d'emails (confirmation, etc.)
├── notifications/       # Notifications in-app
├── photo/                # Photos de chambres (upload, thumbnails)
├── reservation/          # Réservations de chambres
├── reservationActivity/  # Activités liées à une réservation
├── reviews/              # Avis clients
├── rooms/                # Chambres + équipements (amenities)
├── stats/                # Statistiques admin
└── utils/                # Fonctions utilitaires (sanitizers, etc.)
```

Chaque app expose ses routes sous `/api/<nom_app>/`, par exemple `/api/rooms/`, `/api/reservation/`, `/api/customers/`, etc. (voir `app/urls.py`).

## Modèles de données (utiles pour le front)

### `User` (authentification)
Utilisateur custom basé sur `AbstractUser`, authentification par **email**.

| Champ | Type |
|---|---|
| `email` | string (unique, `USERNAME_FIELD`) |
| `username` | string |
| `created_at` | datetime |
| `updated_at` | datetime |

### `CustomerModel` (customers)
Profil client, lié en `OneToOne` à un `User`.

| Champ | Type |
|---|---|
| `user` | FK → User (nullable) |
| `first_name` | string |
| `last_name` | string |
| `email` | string (unique) |
| `phone` | string |
| `address` | text |
| `created_at` | datetime |

### `RoomModel` (rooms)
Chambre de la maison d'hôtes.

| Champ | Type |
|---|---|
| `name` | string |
| `description` | text |
| `capacity` | int |
| `price_per_night` | decimal |
| `available` | bool |
| `main_photo` | image |
| `amenities` | M2M → AmenityModel |

### `AmenityModel` (rooms)
Équipement d'une chambre (Wi-Fi, jacuzzi, TV...).

| Champ | Type |
|---|---|
| `name` | string |
| `icon` | string (classe FontAwesome) |

### `Photo` (photo)
Photo secondaire liée à une chambre, avec génération automatique de thumbnail.

| Champ | Type |
|---|---|
| `room` | FK → RoomModel |
| `file` | image |
| `thumbnail` | image (généré automatiquement) |
| `description` | text |
| `order` | int |
| `created_at` | datetime |

### `Activity` (activity)
Activité proposée en supplément (équitation, dégustation, etc.).

| Champ | Type |
|---|---|
| `name` | string |
| `description` | text |
| `price` | decimal |
| `available` | bool |
| `photo` | image |
| `icon` | string |

### `Reservation` (reservation)
Réservation d'une chambre par un client, avec calcul automatique du prix total et vérification de chevauchement de dates.

| Champ | Type |
|---|---|
| `client` | FK → CustomerModel |
| `room` | FK → RoomModel |
| `check_in_date` | date |
| `check_out_date` | date |
| `guest_count` | int |
| `status` | choix : `pending`, `confirmed`, `canceled`, `completed` |
| `total_price` | decimal (calculé automatiquement) |
| `created_at` | datetime |
| `updated_at` | datetime |

### `ReservationActivity` (reservationActivity)
Table de liaison réservation ↔ activité.

| Champ | Type |
|---|---|
| `reservation` | FK → Reservation |
| `activity` | FK → Activity |
| `quantity` | int |

### `Review` (reviews)
Avis client sur une chambre, uniquement possible après une réservation confirmée/terminée.

| Champ | Type |
|---|---|
| `client` | FK → CustomerModel |
| `room` | FK → RoomModel |
| `reservation` | OneToOne → Reservation (nullable) |
| `rating` | int (1 à 5) |
| `comment` | text |
| `created_at` | datetime |

### `Notification` (notifications)
Notification interne pour un client.

| Champ | Type |
|---|---|
| `user` | FK → CustomerModel |
| `type` | choix : `info`, `success`, `warning`, `error`, `reservation`, `review`, `payment` |
| `title` | string |
| `message` | text |
| `link` | url (nullable) |
| `is_read` | bool |
| `created_at` | datetime |
| `read_at` | datetime (nullable) |
| `metadata` | JSON |

## Fonctionnalités clés

- Authentification JWT
- Recherche et disponibilité des chambres
- Réservations avec validation des dates/capacité et calcul automatique du prix
- Avis clients rattachés à une réservation validée
- Notifications in-app
- Envoi d'emails transactionnels (HTML) avec QR code, via Celery
- Statistiques admin
- Cache Redis, rate limiting, sanitization XSS

## Tests

```bash
docker compose exec web python manage.py test
```
