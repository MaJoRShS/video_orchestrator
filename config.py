import os

# Configurações de modelos
WHISPER_MODEL = "tiny"  # Pode ser: tiny, base, small, medium, large (tiny é mais rápido)
USE_GPU = True  # True para usar GPU (CUDA), False para usar CPU
GPU_DEVICE = "cuda:0"  # Dispositivo GPU a ser usado (cuda:0, cuda:1, etc.)
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.m4a']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif']

# Configurações de banco de dados
DB_PATH = "video_database.db"

# Configurações MongoDB (para versão estendida)
USE_MONGO = True  # True para usar MongoDB, False para SQLite
MONGODB_URI = "mongodb://localhost:27017"  # URI de conexão do MongoDB
MONGODB_DATABASE = "video_orchestrator"  # Nome da base de dados

# Configurações de processamento
BATCH_SIZE = 16
MAX_WORKERS = 4
CHUNK_DURATION = 30  # segundos para dividir vídeos muito longos

# Configurações de categorização
CATEGORIES = [
    "educacao",
    "entretenimento", 
    "noticias",
    "esportes",
    "tecnologia",
    "culinaria",
    "musica",
    "gaming",
    "tutorial",
    "documentario",
    "adulto",
    "outros"
]

# Categorias específicas para imagens
IMAGE_CATEGORIES = [
    "educacao",
    "entretenimento",
    "arte",
    "natureza",
    "pessoas",
    "tecnologia",
    "comida",
    "veiculos",
    "arquitetura",
    "adulto",
    "outros"
]

# Modelo de classificação de texto (HuggingFace)
TEXT_CLASSIFIER_MODEL = "neuralmind/bert-base-portuguese-cased"
