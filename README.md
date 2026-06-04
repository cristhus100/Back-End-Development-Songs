# Back-End-Development-Songs

Microservicio de Songs - API REST con Flask y MongoDB

## Descripción del Proyecto

API REST para gestionar canciones (CRUD completo) desarrollada con Flask y MongoDB. Incluye pruebas con comandos curl.

## Environment Setup

- **Python version**: 3.9.x
- **Virtual environment**: `backend-songs-venv`
- **Framework**: Flask 3.1.1
- **Database**: MongoDB (with PyMongo 4.12.1)

### Setup Instructions

```bash
# Clone the repository
git clone https://github.com/cristhus100/Back-End-Development-Songs.git
cd Back-End-Development-Songs

# Create virtual environment
python3 -m venv backend-songs-venv
source backend-songs-venv/bin/activate

# Create from template
bin/setup.sh

# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

### Endpoints

- `GET /health` - Health check
- `GET /song` - Get all songs
- `POST /song` - Create song
- `GET /song/<id>` - Get song by ID
- `PUT /song/<id>` - Update song
- `DELETE /song/<id>` - Delete song
- `GET /count` - Song count
