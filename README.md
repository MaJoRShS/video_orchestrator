# Orquestrador de IAs para Análise de Vídeos

Este sistema processa vídeos automaticamente realizando:
- Transcrição de áudio para português brasileiro
- Análise visual do conteúdo
- Classificação automática por categoria
- Criação de base de conhecimento para busca

## Recursos

- **Transcrição de Áudio**: Usa OpenAI Whisper (modelo offline)
- **Análise Visual**: Detecta faces, analisa brilho, mudanças de cena
- **Classificação**: Categoriza em educação, entretenimento, notícias, esportes, tecnologia, etc.
- **Busca Inteligente**: Busca por texto, categoria ou palavras-chave
- **Base de Conhecimento**: SQLite com índice de busca TF-IDF

## Instalação

### Dependências
```bash
pip install torch torchaudio transformers opencv-python librosa sqlalchemy openai-whisper moviepy scikit-learn numpy pandas
```

### Configuração
1. Clone/baixe todos os arquivos para uma pasta
2. Instale as dependências acima
3. Execute o programa

## Uso

### Processar Vídeos em um Diretório
```bash
python orchestrator.py process /caminho/para/videos --recursive
```

### Buscar Vídeos
```bash
# Busca por texto
python orchestrator.py search --query "tecnologia programação"

# Busca por categoria
python orchestrator.py search --category "adulto"

# Busca por palavras-chave
python orchestrator.py search --keywords "sexo,educação,relacionamento"
```

### Ver Resumo do Conteúdo
```bash
python orchestrator.py summary
```

## Exemplo de Uso Prático

Para verificar se você tem vídeos sobre determinado assunto:

```bash
# Exemplo: buscar vídeos sobre sexo
python orchestrator.py search --keywords "sexo,adulto,íntimo"

# Exemplo: buscar vídeos educacionais
python orchestrator.py search --category "educacao"

# Exemplo: buscar por transcrição
python orchestrator.py search --query "como fazer"
```

## Categorias Suportadas

- educacao
- entretenimento
- noticias
- esportes
- tecnologia
- culinaria
- musica
- gaming
- tutorial
- documentario
- adulto
- outros

## Formatos de Vídeo Suportados

- MP4, AVI, MOV, MKV, FLV, WMV
- MP3, WAV, FLAC, AAC, M4A (apenas áudio)

## Estrutura dos Arquivos

- `orchestrator.py` - Programa principal
- `transcription.py` - Motor de transcrição
- `video_analysis.py` - Análise visual e classificação
- `database.py` - Modelo de banco de dados
- `search_engine.py` - Sistema de busca
- `config.py` - Configurações
- `video_database.db` - Banco SQLite (criado automaticamente)

## Logs

Os logs são salvos em `orchestrator.log` e também exibidos no terminal.

---

# Documentação das Classes e Detalhes de Implementação

Abaixo estão todas as classes Python utilizadas no projeto, com o propósito de cada uma e a descrição de seus métodos.

## config.py
Guarda parâmetros de configuração de todo o sistema.
- WHISPER_MODEL, USE_GPU, GPU_DEVICE: controlam o carregamento do Whisper e dispositivo (CPU/GPU).
- VIDEO_EXTENSIONS, AUDIO_EXTENSIONS: definem extensões aceitas.
- DB_PATH: caminho do banco SQLite.
- BATCH_SIZE, MAX_WORKERS, CHUNK_DURATION: parâmetros de processamento (hoje usados principalmente para referência futura).
- CATEGORIES: lista oficial de categorias.
- TEXT_CLASSIFIER_MODEL: modelo HF planejado para classificação textual.

## transcription.py
Classe: TranscriptionEngine
- Por que existe: encapsula toda a lógica de extração de áudio e transcrição com Whisper, isolando dependências (moviepy, torch, whisper) e decisões de hardware.

Métodos:
- __init__(model_size=config.WHISPER_MODEL)
  - Carrega modelo Whisper no dispositivo ideal (GPU se disponível e permitido; caso contrário, CPU).
  - Faz log de informações de GPU quando possível.
- _get_device()
  - Decide entre CPU e GPU com base em config.USE_GPU e torch.cuda.is_available(). Valida GPU específica (config.GPU_DEVICE).
- _log_gpu_info()
  - Faz log de nome e memória da GPU selecionada.
- extract_audio_from_video(video_path, audio_path=None)
  - Extrai o áudio de um vídeo usando MoviePy e salva como WAV temporário. Retorna o caminho do arquivo.
- transcribe_audio_with_timeout(audio_path, language=None, timeout=300, progress_callback=None)
  - Executa a transcrição em thread separada com timeout para evitar travas em mídia grande/corrompida. Retorna dict: {text, language, segments}.
- transcribe_audio(audio_path, language=None, progress_callback=None)
  - Wrapper com checagens (existência/tamanho do arquivo) e escolha de timeout (10 min para >100MB). Faz log e retorna o resultado da transcrição.
- transcribe_video(video_path, languages=['pt','en'], progress_callback=None)
  - Pipeline completo: extrai áudio, transcreve nos idiomas pedidos (pt e/ou en), remove o temporário e retorna {'pt': {...}, 'en': {...}} quando disponíveis.
- get_video_duration(video_path)
  - Lê a duração do vídeo via MoviePy e retorna em segundos.

## video_analysis.py
Classe: VideoAnalyzer
- Por que existe: concentra a análise de frames (visão computacional) e a inteligência de PNL para classificar e gerar contexto e keywords, de forma desacoplada do orquestrador.

Métodos:
- __init__()
  - Inicializa pipeline de classificação textual (fallback caso não carregue) e um TfidfVectorizer para extração de keywords.
- extract_video_frames(video_path, num_frames=10)
  - Amostra frames ao longo do vídeo com OpenCV para representarem o conteúdo visual. Retorna lista de frames (ndarrays BGR).
- analyze_visual_content(frames)
  - Extrai métricas simples: brilho médio por frame, cores dominantes, presença de faces (Haar cascades), mudanças de cena (correlação de histograma). Agrega médias/variâncias e retorna dict com estatísticas.
- extract_keywords(text, max_keywords=20)
  - Usa TF‑IDF local para obter termos mais relevantes do texto. Retorna uma lista ordenada de palavras‑chave.
- classify_content(transcript, visual_analysis)
  - Classificador baseado em regras por palavras‑chave por categoria, somando contagens no texto e aplicando bônus para alguns sinais visuais. Retorna {category, confidence, scores}.
- generate_video_context(transcript, visual_analysis, classification)
  - Gera um texto de contexto compacto: mini-resumo da transcrição + observações visuais + categoria e confiança.

## database.py
Classes: VideoRecord (ORM), DatabaseManager
- Por que existem: prover persistência relacional simples (SQLite/SQLAlchemy) dos metadados e resultados de processamento.

VideoRecord (tabela 'videos'):
- Campos: id, file_path, file_name, file_size, duration, transcript_pt, transcript_en, video_context, category, confidence_score, keywords (JSON string), processed_at, created_at.
- __repr__: exibe file_name e category para debug.

DatabaseManager
- __init__(db_path=config.DB_PATH): cria engine SQLite, materializa schema e abre sessão.
- add_video(video_record): adiciona e commita, retornando o id.
- get_video_by_path(file_path): busca deunicador por caminho absoluto.
- search_videos_by_keywords(keywords): procura palavras na transcrição, contexto e campo keywords; remove duplicados.
- get_videos_by_category(category): retorno filtrado por categoria.
- get_all_videos(): lista completa.
- close(): fecha a sessão.

## search_engine.py
Classe: ContentSearchEngine
- Por que existe: provê busca textual eficiente em cima do corpus com TF‑IDF e utilitários de busca por categoria/keywords e resumo.

Métodos:
- __init__(db_manager)
  - Inicializa um TfidfVectorizer com stopwords simples de PT, monta corpus e ids, chama _update_search_index().
- _update_search_index()
  - Reconstroi corpus a partir de transcript_pt, video_context e keywords (parseadas de JSON). Treina a matriz TF‑IDF.
- search_by_text(query, limit=10)
  - Vetoriza a query, calcula similaridade coseno, retorna top resultados com score.
- search_by_keywords(keywords, exact_match=False)
  - Heurística por contagem de ocorrências (transcrição/contexto/keywords) e retorna ordenado por score.
- search_by_category(category)
  - Retorna vídeos da categoria informada ordenados por confidence_score (desc).
- advanced_search(query, category=None, min_duration=None, max_duration=None)
  - Combina filtros de texto, categoria e duração.
- get_content_summary()
  - Agrega estatísticas globais: total, por categoria, duração total (em horas), contagem por idioma.
- find_similar_videos(video_id, limit=5)
  - Busca semelhantes usando a própria transcrição como query e remove o item alvo do ranking.

## orchestrator.py
Classe: VideoOrchestrator
- Por que existe: orquestra o pipeline end-to-end por arquivo/diretório, integrando transcrição, análise visual, classificação, persistência e indexação de busca.

Métodos principais:
- __init__(): instancia TranscriptionEngine, VideoAnalyzer, DatabaseManager, ContentSearchEngine; configura logging.
- process_video(video_path, progress_bar=None):
  - Pipeline de 7 etapas com barra de progresso: verificação/skip se já processado; criação do registro; leitura de duração; transcrição; análise visual; classificação e keywords; salvar no banco; atualizar índice de busca. Retorna o id do vídeo.
- process_directory(directory_path, recursive=True):
  - Varre o diretório por extensões configuradas, processa sequência de vídeos com uma barra geral e acumula ids.
- search_videos(query), search_by_category(category), search_by_keywords(keywords):
  - Facades que delegam para ContentSearchEngine e formatam a saída (id, nome, categoria, contexto, score).
- get_content_summary(): retorna o resumo produzido pelo search engine.

CLI (função main):
- Subcomandos: process, search, summary. Opções para --recursive, --query, --category, --keywords. Imprime resultados amigáveis no terminal.

---

# Extensão: Suporte a Imagens (contexto/explicação) e Cadastro por Diretório

A seguir, um guia para incorporar imagens ao pipeline, gerar contexto/explicação e persistir por diretório. Inclui também um plano de migração para usar MongoDB como base NoSQL documental (preferência solicitada).

## Como extrair contexto/explicação de imagens

Abordagem recomendada:
- Leitura com OpenCV/Pillow.
- Geração de legendas (image captioning) com Transformers (ex.: "nlpconnect/vit-gpt2-image-captioning") ou "Salesforce/blip-image-captioning-base".
- Extração de tags/keywords usando TF‑IDF sobre a legenda e/ou modelos de classificação de imagens (ex.: "google/vit-base-patch16-224").
- Armazenar: caminho do arquivo, diretório (parent), legenda gerada, keywords, features auxiliares (opcional).

Exemplo de código (novo módulo images.py):
```python
# images.py
import os
import cv2
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

class ImageAnalyzer:
    def __init__(self):
        # Pipeline de legenda de imagem
        self.captioner = pipeline(
            "image-to-text",
            model="nlpconnect/vit-gpt2-image-captioning"
        )
        self.vectorizer = TfidfVectorizer(max_features=50, stop_words=['de','da','do','para','com','em','no','na','o','a','e','que'])

    def describe_image(self, image_path):
        # Lê a imagem (BGR)
        image = cv2.imread(image_path)
        if image is None:
            return None
        # A pipeline do HF aceita caminhos de arquivo diretamente
        captions = self.captioner(image_path, max_new_tokens=30)
        caption = captions[0]['generated_text'] if captions else ""
        # Keywords simples a partir da legenda
        if caption:
            X = self.vectorizer.fit_transform([caption.lower()])
            features = self.vectorizer.get_feature_names_out()
            scores = X.toarray()[0]
            keywords = [w for w, s in sorted(zip(features, scores), key=lambda x: x[1], reverse=True) if s > 0][:15]
        else:
            keywords = []
        return {
            'caption': caption,
            'keywords': keywords
        }
```

Para processar um diretório com imagens, você pode adicionar um subcomando ao orchestrator (por exemplo, `orchestrator.py images ...`) ou criar um script dedicado que:
- Varre extensões de imagem (jpg, jpeg, png, bmp, webp).
- Chama `ImageAnalyzer.describe_image` para cada arquivo.
- Persiste no banco (ver seção MongoDB abaixo) incluindo o campo `directory` = pasta pai do arquivo.

## Persistência por Diretório em MongoDB (Migração de SQLite para NoSQL)

Motivação: documentos com campos flexíveis (legendas de imagens, análises visuais, múltiplos idiomas) e indexações de texto são naturais em bases documentais como MongoDB.

### Esquema sugerido (coleções)
- videos
  - _id
  - file_path (string, único)
  - directory (string) -> ex.: caminho da pasta pai
  - file_name, file_size, duration
  - transcript: { pt: {text, segments}, en: {text, segments} }
  - visual_analysis: { avg_brightness, has_faces, scene_changes, dominant_colors, ... }
  - classification: { category, confidence, scores }
  - keywords: ["..."]
  - video_context (string)
  - created_at, processed_at
- images
  - _id
  - file_path (string, único)
  - directory (string)
  - file_name, file_size
  - caption (string)
  - keywords: ["..."]
  - extra_features (opcional: cores dominantes, presença de rostos)
  - created_at, processed_at

### Índices recomendados
- Único: file_path em cada coleção.
- Texto: transcrições/contexts em videos (transcript.pt.text, video_context, keywords) e caption/keywords em images.
- campo directory indexado para filtros rápidos por pasta.

### Exemplo de Manager para MongoDB
```python
# db_mongo.py
import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, TEXT

class MongoManager:
    def __init__(self, uri=None, db_name="video_orchestrator"):
        self.client = MongoClient(uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
        self.db = self.client[db_name]
        self.videos = self.db["videos"]
        self.images = self.db["images"]
        # Índices
        self.videos.create_index([("file_path", ASCENDING)], unique=True)
        self.videos.create_index([("directory", ASCENDING)])
        self.videos.create_index([("transcript.pt.text", TEXT), ("video_context", TEXT), ("keywords", TEXT)])
        self.images.create_index([("file_path", ASCENDING)], unique=True)
        self.images.create_index([("directory", ASCENDING)])
        self.images.create_index([("caption", TEXT), ("keywords", TEXT)])

    def upsert_video(self, doc):
        doc.setdefault("created_at", datetime.utcnow())
        doc["processed_at"] = datetime.utcnow()
        self.videos.update_one({"file_path": doc["file_path"]}, {"$set": doc}, upsert=True)
        return self.videos.find_one({"file_path": doc["file_path"]}, {"_id": 1})["_id"]

    def upsert_image(self, doc):
        doc.setdefault("created_at", datetime.utcnow())
        doc["processed_at"] = datetime.utcnow()
        self.images.update_one({"file_path": doc["file_path"]}, {"$set": doc}, upsert=True)
        return self.images.find_one({"file_path": doc["file_path"]}, {"_id": 1})["_id"]

    def search_videos_text(self, query, limit=10):
        return list(self.videos.find({"$text": {"$search": query}}).limit(limit))

    def search_images_text(self, query, limit=10):
        return list(self.images.find({"$text": {"$search": query}}).limit(limit))

    def by_directory(self, collection, directory):
        coll = self.db[collection]
        return list(coll.find({"directory": directory}))
```

### Como usar o campo "directory"
- Ao processar, sempre derive `directory = os.path.dirname(file_path)`.
- Salve esse campo no documento. Isso permite:
  - Listar tudo de uma pasta específica.
  - Agregar estatísticas por diretório (ex.: quantos vídeos/imagens, categorias mais comuns, etc.).

### Adaptação do Orchestrator para MongoDB (conceito)
- Substituir DatabaseManager por MongoManager quando desejado:
```python
# orchestrator.py (conceito)
from db_mongo import MongoManager

class VideoOrchestrator:
    def __init__(self, use_mongo=True):
        if use_mongo:
            self.db = MongoManager()
        else:
            from database import DatabaseManager
            self.db = DatabaseManager()
        # demais componentes...
```
- Ao salvar vídeo:
```python
# montar doc para Mongo
doc = {
  "file_path": video_path,
  "directory": str(Path(video_path).parent),
  "file_name": os.path.basename(video_path),
  "file_size": os.path.getsize(video_path),
  "duration": duration,
  "transcript": {
      "pt": transcription_results.get("pt"),
      "en": transcription_results.get("en"),
  },
  "visual_analysis": visual_analysis,
  "classification": classification,
  "keywords": keywords,
  "video_context": video_context,
}
vid = self.db.upsert_video(doc)
```

### Busca com TF‑IDF vs. Índice de Texto do Mongo
- Você pode manter o ContentSearchEngine (TF‑IDF) como hoje, lendo do Mongo em vez do SQLite.
- Alternativamente, usar o índice textual do Mongo (`$text`) para queries simples, e TF‑IDF/embedding apenas para ranking avançado.

## Passo a passo sugerido para migração
1. Instalar dependência:
```bash
pip install pymongo
```
2. Criar o módulo `db_mongo.py` conforme exemplo e parametrizar via variável de ambiente `MONGODB_URI`.
3. Introduzir flag/config em `config.py` (ex.: USE_MONGO=True) e ramificar a escolha do manager no `VideoOrchestrator`.
4. Ajustar `search_engine.py` para ler do novo manager (implemente métodos `get_all_videos()` equivalentes no MongoManager ou use consultas diretas).
5. Testar: processar um pequeno diretório, verificar coleções `videos` e `images`, índices e buscas.

---

# FAQ e Boas Práticas
- Tratamento de arquivos grandes: a transcrição usa timeout progressivo para evitar travas. Ajuste em `transcription.py` se necessário.
- GPU opcional: se `config.USE_GPU=True` e CUDA não estiver disponível, o sistema cai para CPU automaticamente.
- Categorias: o classificador é heurístico; para melhor qualidade, troque por um modelo supervisionado treinado no seu domínio, mantendo a mesma interface de `VideoAnalyzer.classify_content`.
- Privacidade: os modelos utilizados localmente (Whisper offline, OpenCV) evitam envio de dados a terceiros por padrão.

---

# Como usar as extensões

## Configuração do MongoDB

1. Instale o MongoDB localmente ou use um serviço na nuvem
2. Configure a variável de ambiente `MONGODB_URI` ou edite `config.py`
3. Instale as dependências estendidas:
```bash
pip install -r requirements_extended.txt
```

## Uso do orquestrador estendido

### Processar vídeos e imagens
```bash
# Processar tudo (vídeos + imagens) com MongoDB
python orchestrator_extended.py process /caminho/para/arquivos --recursive

# Processar apenas vídeos
python orchestrator_extended.py process /caminho/para/videos --videos-only

# Forçar uso do SQLite (apenas vídeos)
python orchestrator_extended.py --use-sqlite process /caminho/para/videos
```

### Busca avançada
```bash
# Busca textual em tudo
python orchestrator_extended.py search --query "natureza paisagem"

# Busca apenas em imagens
python orchestrator_extended.py search --query "casa arquitetura" --type images

# Busca todo conteúdo de um diretório
python orchestrator_extended.py search --directory "/caminho/para/pasta"

# Resumo de diretório específico
python orchestrator_extended.py summary --directory "/caminho/para/pasta"
```

### Exemplo prático com imagens
```bash
# Processar pasta de fotos
python orchestrator_extended.py process ~/Pictures/Vacation2023 --recursive

# Buscar fotos de comida
python orchestrator_extended.py search --query "food meal" --type images

# Ver resumo das fotos por pasta
python orchestrator_extended.py summary --directory "~/Pictures/Vacation2023"
```

## Estrutura de dados no MongoDB

### Coleção 'videos'
```json
{
  "_id": ObjectId("..."),
  "file_path": "/caminho/completo/video.mp4",
  "directory": "/caminho/completo",
  "file_name": "video.mp4",
  "file_size": 104857600,
  "duration": 1800.5,
  "transcript": {
    "pt": {
      "text": "Transcrição em português...",
      "segments": [...]
    }
  },
  "visual_analysis": {
    "avg_brightness": 128.5,
    "has_faces": true,
    "scene_changes": 15
  },
  "classification": {
    "category": "educacao",
    "confidence": 0.85
  },
  "keywords": ["aula", "ensino", "explicar"],
  "video_context": "Vídeo educacional sobre...",
  "created_at": ISODate("2023-12-01T10:30:00Z"),
  "processed_at": ISODate("2023-12-01T10:35:00Z")
}
```

### Coleção 'images'
```json
{
  "_id": ObjectId("..."),
  "file_path": "/caminho/completo/foto.jpg",
  "directory": "/caminho/completo",
  "file_name": "foto.jpg",
  "file_size": 2048576,
  "caption": "A beautiful landscape with mountains and trees",
  "keywords": ["landscape", "mountains", "trees", "nature"],
  "visual_features": {
    "width": 1920,
    "height": 1080,
    "brightness": 145.2,
    "has_faces": false,
    "dominant_color": [34, 89, 156]
  },
  "classification": {
    "category": "natureza",
    "confidence": 0.92,
    "labels": [{"label": "landscape", "score": 0.95}]
  },
  "created_at": ISODate("2023-12-01T10:30:00Z"),
  "processed_at": ISODate("2023-12-01T10:32:00Z")
}
```

## Vantagens do MongoDB

1. **Flexibilidade de esquema**: Fácil adicionar novos campos sem migrações
2. **Busca textual nativa**: Índices de texto full-text integrados
3. **Agregações poderosas**: Estatísticas por diretório, categoria, etc.
4. **Escalabilidade**: Suporta grandes volumes de dados
5. **Organização por diretório**: Campo `directory` permite filtros rápidos

## Modelos de IA utilizados

### Para vídeos
- **OpenAI Whisper**: Transcrição de áudio (offline)
- **OpenCV**: Análise visual básica
- **TF-IDF**: Extração de palavras-chave

### Para imagens
- **nlpconnect/vit-gpt2-image-captioning**: Geração de legendas
- **google/vit-base-patch16-224**: Classificação de imagens
- **OpenCV**: Análise de features visuais (faces, brilho, nitidez)
- **TF-IDF**: Extração de palavras-chave das legendas
