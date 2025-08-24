import os
import logging
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient, ASCENDING, TEXT, errors
from pymongo.collection import Collection
from typing import Dict, List, Optional, Any

class MongoManager:
    """
    Manager para MongoDB com suporte a vídeos e imagens organizados por diretório
    
    Coleções:
    - videos: metadados, transcrições e análises de vídeos
    - images: metadados, legendas e análises de imagens
    
    Cada documento inclui o campo 'directory' para organização por pasta
    """
    
    def __init__(self, uri: Optional[str] = None, db_name: str = "video_orchestrator"):
        self.logger = logging.getLogger(__name__)
        
        # Conecta ao MongoDB
        try:
            mongodb_uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[db_name]
            
            # Testa a conexão
            self.client.admin.command('ismaster')
            self.logger.info(f"Conectado ao MongoDB: {db_name}")
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar ao MongoDB: {e}")
            raise
        
        # Referências das coleções
        self.videos: Collection = self.db["videos"]
        self.images: Collection = self.db["images"]
        
        # Cria índices necessários
        self._create_indexes()
    
    def _create_indexes(self):
        """
        Cria índices otimizados para busca e performance
        """
        try:
            # Índices para vídeos
            self.videos.create_index([("file_path", ASCENDING)], unique=True)
            self.videos.create_index([("directory", ASCENDING)])
            self.videos.create_index([("classification.category", ASCENDING)])
            self.videos.create_index([("created_at", ASCENDING)])
            
            # Índice de texto para busca full-text em vídeos
            try:
                self.videos.create_index([
                    ("transcript.pt.text", TEXT),
                    ("transcript.en.text", TEXT),
                    ("video_context", TEXT),
                    ("keywords", TEXT)
                ])
            except errors.OperationFailure:
                # Índice de texto já existe ou conflito
                pass
            
            # Índices para imagens
            self.images.create_index([("file_path", ASCENDING)], unique=True)
            self.images.create_index([("directory", ASCENDING)])
            self.images.create_index([("classification.category", ASCENDING)])
            self.images.create_index([("created_at", ASCENDING)])
            
            # Índice de texto para busca full-text em imagens
            try:
                self.images.create_index([
                    ("caption", TEXT),
                    ("keywords", TEXT)
                ])
            except errors.OperationFailure:
                # Índice de texto já existe ou conflito
                pass
            
            self.logger.info("Índices criados com sucesso")
            
        except Exception as e:
            self.logger.warning(f"Erro ao criar índices: {e}")
    
    def upsert_video(self, doc: Dict[str, Any]) -> str:
        """
        Insere ou atualiza um documento de vídeo
        """
        try:
            # Adiciona timestamps
            doc.setdefault("created_at", datetime.utcnow())
            doc["processed_at"] = datetime.utcnow()
            
            # Adiciona diretório se não presente
            if "directory" not in doc and "file_path" in doc:
                doc["directory"] = str(Path(doc["file_path"]).parent)
            
            # Upsert
            result = self.videos.update_one(
                {"file_path": doc["file_path"]}, 
                {"$set": doc}, 
                upsert=True
            )
            
            # Retorna o ID do documento
            video_doc = self.videos.find_one({"file_path": doc["file_path"]}, {"_id": 1})
            return str(video_doc["_id"]) if video_doc else None
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar vídeo: {e}")
            return None
    
    def upsert_image(self, doc: Dict[str, Any]) -> str:
        """
        Insere ou atualiza um documento de imagem
        """
        try:
            # Adiciona timestamps
            doc.setdefault("created_at", datetime.utcnow())
            doc["processed_at"] = datetime.utcnow()
            
            # Adiciona diretório se não presente
            if "directory" not in doc and "file_path" in doc:
                doc["directory"] = str(Path(doc["file_path"]).parent)
            
            # Upsert
            result = self.images.update_one(
                {"file_path": doc["file_path"]}, 
                {"$set": doc}, 
                upsert=True
            )
            
            # Retorna o ID do documento
            image_doc = self.images.find_one({"file_path": doc["file_path"]}, {"_id": 1})
            return str(image_doc["_id"]) if image_doc else None
            
        except Exception as e:\n            self.logger.error(f"Erro ao salvar imagem: {e}")
            return None
    
    def get_video_by_path(self, file_path: str) -> Optional[Dict]:
        """
        Busca vídeo por caminho do arquivo
        """
        try:
            return self.videos.find_one({"file_path": file_path})
        except Exception as e:
            self.logger.error(f"Erro ao buscar vídeo por path: {e}")
            return None
    
    def get_image_by_path(self, file_path: str) -> Optional[Dict]:
        """
        Busca imagem por caminho do arquivo
        """
        try:
            return self.images.find_one({"file_path": file_path})
        except Exception as e:
            self.logger.error(f"Erro ao buscar imagem por path: {e}")
            return None
    
    def search_videos_text(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca textual em vídeos usando índice MongoDB
        """
        try:
            return list(self.videos.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))
        except Exception as e:
            self.logger.error(f"Erro na busca textual de vídeos: {e}")
            return []
    
    def search_images_text(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca textual em imagens usando índice MongoDB
        """
        try:
            return list(self.images.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))
        except Exception as e:
            self.logger.error(f"Erro na busca textual de imagens: {e}")
            return []
    
    def get_videos_by_directory(self, directory: str) -> List[Dict]:
        """
        Retorna todos os vídeos de um diretório específico
        """
        try:
            return list(self.videos.find({"directory": directory}))
        except Exception as e:
            self.logger.error(f"Erro ao buscar vídeos por diretório: {e}")
            return []
    
    def get_images_by_directory(self, directory: str) -> List[Dict]:
        """
        Retorna todas as imagens de um diretório específico
        """
        try:
            return list(self.images.find({"directory": directory}))
        except Exception as e:
            self.logger.error(f"Erro ao buscar imagens por diretório: {e}")
            return []
    
    def get_videos_by_category(self, category: str) -> List[Dict]:
        """
        Retorna vídeos de uma categoria específica
        """
        try:
            return list(self.videos.find({"classification.category": category}))
        except Exception as e:
            self.logger.error(f"Erro ao buscar vídeos por categoria: {e}")
            return []
    
    def get_images_by_category(self, category: str) -> List[Dict]:
        """
        Retorna imagens de uma categoria específica
        """
        try:
            return list(self.images.find({"classification.category": category}))
        except Exception as e:
            self.logger.error(f"Erro ao buscar imagens por categoria: {e}")
            return []
    
    def get_all_videos(self) -> List[Dict]:
        """
        Retorna todos os vídeos
        """
        try:
            return list(self.videos.find({}))
        except Exception as e:
            self.logger.error(f"Erro ao buscar todos os vídeos: {e}")
            return []
    
    def get_all_images(self) -> List[Dict]:
        """
        Retorna todas as imagens
        """
        try:
            return list(self.images.find({}))
        except Exception as e:
            self.logger.error(f"Erro ao buscar todas as imagens: {e}")
            return []
    
    def get_directory_summary(self, directory: str) -> Dict[str, Any]:
        """
        Retorna resumo estatístico de um diretório específico
        """
        try:
            summary = {
                'directory': directory,
                'videos': {
                    'count': 0,
                    'total_duration': 0,
                    'categories': {}
                },
                'images': {
                    'count': 0,
                    'categories': {}
                }
            }
            
            # Estatísticas de vídeos
            videos = self.get_videos_by_directory(directory)
            summary['videos']['count'] = len(videos)
            
            for video in videos:
                # Duração total
                if video.get('duration'):
                    summary['videos']['total_duration'] += video['duration']
                
                # Categorias
                category = video.get('classification', {}).get('category', 'outros')
                summary['videos']['categories'][category] = summary['videos']['categories'].get(category, 0) + 1
            
            # Estatísticas de imagens
            images = self.get_images_by_directory(directory)
            summary['images']['count'] = len(images)
            
            for image in images:
                category = image.get('classification', {}).get('category', 'outros')
                summary['images']['categories'][category] = summary['images']['categories'].get(category, 0) + 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo do diretório: {e}")
            return {}
    
    def get_global_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo estatístico global
        """
        try:
            summary = {
                'videos': {
                    'total_count': 0,
                    'total_duration_hours': 0,
                    'categories': {},
                    'directories': set()
                },
                'images': {
                    'total_count': 0,
                    'categories': {},
                    'directories': set()
                }
            }
            
            # Estatísticas de vídeos
            videos = self.get_all_videos()
            summary['videos']['total_count'] = len(videos)
            
            for video in videos:
                # Duração total
                if video.get('duration'):
                    summary['videos']['total_duration_hours'] += video['duration'] / 3600
                
                # Categorias
                category = video.get('classification', {}).get('category', 'outros')
                summary['videos']['categories'][category] = summary['videos']['categories'].get(category, 0) + 1
                
                # Diretórios
                if video.get('directory'):
                    summary['videos']['directories'].add(video['directory'])
            
            # Estatísticas de imagens
            images = self.get_all_images()
            summary['images']['total_count'] = len(images)
            
            for image in images:
                # Categorias
                category = image.get('classification', {}).get('category', 'outros')
                summary['images']['categories'][category] = summary['images']['categories'].get(category, 0) + 1
                
                # Diretórios
                if image.get('directory'):
                    summary['images']['directories'].add(image['directory'])
            
            # Converte sets para listas
            summary['videos']['directories'] = list(summary['videos']['directories'])
            summary['images']['directories'] = list(summary['images']['directories'])
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo global: {e}")
            return {}
    
    def search_by_keywords(self, keywords: List[str], collection: str = "videos", limit: int = 10) -> List[Dict]:
        """
        Busca por palavras-chave específicas
        """
        try:
            coll = self.db[collection]
            
            # Constrói query regex para as keywords
            keyword_queries = []
            for keyword in keywords:
                keyword_queries.append({"keywords": {"$regex": keyword, "$options": "i"}})
            
            # Busca documentos que contenham pelo menos uma keyword
            results = list(coll.find(
                {"$or": keyword_queries}
            ).limit(limit))
            
            # Calcula score simples baseado no número de keywords encontradas
            for result in results:
                score = 0
                result_keywords = result.get('keywords', [])
                for keyword in keywords:
                    for rk in result_keywords:
                        if keyword.lower() in rk.lower():
                            score += 1
                result['match_score'] = score
            
            # Ordena por score
            results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca por keywords: {e}")
            return []
    
    def aggregate_by_directory(self, collection: str = "videos") -> List[Dict]:
        """
        Agrega estatísticas por diretório
        """
        try:
            coll = self.db[collection]
            
            pipeline = [
                {
                    "$group": {
                        "_id": "$directory",
                        "count": {"$sum": 1},
                        "categories": {"$push": "$classification.category"},
                        "avg_duration": {"$avg": "$duration"} if collection == "videos" else {"$avg": 0}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            return list(coll.aggregate(pipeline))
            
        except Exception as e:
            self.logger.error(f"Erro na agregação por diretório: {e}")
            return []
    
    def find_similar_content(self, file_path: str, collection: str = "videos", limit: int = 5) -> List[Dict]:
        """
        Encontra conteúdo similar baseado nas keywords
        """
        try:
            coll = self.db[collection]
            
            # Busca o documento alvo
            target_doc = coll.find_one({"file_path": file_path})
            if not target_doc:
                return []
            
            target_keywords = target_doc.get('keywords', [])
            if not target_keywords:
                return []
            
            # Busca documentos com keywords similares
            similar_docs = []
            
            # Query por keywords similares
            keyword_queries = []
            for keyword in target_keywords:
                keyword_queries.append({"keywords": {"$regex": keyword, "$options": "i"}})
            
            candidates = list(coll.find({
                "$or": keyword_queries,
                "file_path": {"$ne": file_path}  # Exclui o próprio arquivo
            }))
            
            # Calcula similaridade simples
            for candidate in candidates:
                candidate_keywords = candidate.get('keywords', [])
                
                # Intersecção de keywords
                common_keywords = set(target_keywords) & set(candidate_keywords)
                similarity_score = len(common_keywords) / max(len(target_keywords), 1)
                
                candidate['similarity_score'] = similarity_score
                similar_docs.append(candidate)
            
            # Ordena por similaridade e retorna top resultados
            similar_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_docs[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar conteúdo similar: {e}")
            return []
    
    def delete_by_directory(self, directory: str, collection: str = None):
        """
        Remove todos os documentos de um diretório específico
        """
        try:
            if collection:
                coll = self.db[collection]
                result = coll.delete_many({"directory": directory})
                self.logger.info(f"Removidos {result.deleted_count} documentos de {directory} na coleção {collection}")
            else:
                # Remove de ambas as coleções
                video_result = self.videos.delete_many({"directory": directory})
                image_result = self.images.delete_many({"directory": directory})
                self.logger.info(f"Removidos {video_result.deleted_count} vídeos e {image_result.deleted_count} imagens de {directory}")
            
        except Exception as e:
            self.logger.error(f"Erro ao remover documentos do diretório: {e}")
    
    def update_directory_path(self, old_directory: str, new_directory: str):
        """
        Atualiza o caminho de diretório em massa (útil para reorganização)
        """
        try:
            # Atualiza vídeos
            video_result = self.videos.update_many(
                {"directory": old_directory},
                {"$set": {"directory": new_directory}}
            )
            
            # Atualiza imagens
            image_result = self.images.update_many(
                {"directory": old_directory},
                {"$set": {"directory": new_directory}}
            )
            
            self.logger.info(f"Atualizados {video_result.modified_count} vídeos e {image_result.modified_count} imagens")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar caminhos de diretório: {e}")
    
    def close(self):
        """
        Fecha conexão com MongoDB
        """
        try:
            self.client.close()
            self.logger.info("Conexão MongoDB fechada")
        except Exception as e:
            self.logger.error(f"Erro ao fechar conexão: {e}")

# Classe de compatibilidade para migração gradual do SQLite
class MongoVideoRecord:
    """
    Wrapper que simula a interface do VideoRecord do SQLAlchemy
    para facilitar migração gradual
    """
    
    def __init__(self, mongo_doc: Dict[str, Any]):
        self._doc = mongo_doc
    
    @property
    def id(self):
        return str(self._doc.get('_id', ''))
    
    @property
    def file_path(self):
        return self._doc.get('file_path', '')
    
    @property
    def file_name(self):
        return self._doc.get('file_name', '')
    
    @property
    def file_size(self):
        return self._doc.get('file_size', 0)
    
    @property
    def duration(self):
        return self._doc.get('duration', 0)
    
    @property
    def transcript_pt(self):
        transcript = self._doc.get('transcript', {})
        return transcript.get('pt', {}).get('text', '') if transcript.get('pt') else ''
    
    @property
    def transcript_en(self):
        transcript = self._doc.get('transcript', {})
        return transcript.get('en', {}).get('text', '') if transcript.get('en') else ''
    
    @property
    def video_context(self):
        return self._doc.get('video_context', '')
    
    @property
    def category(self):
        classification = self._doc.get('classification', {})
        return classification.get('category', 'outros')
    
    @property
    def confidence_score(self):
        classification = self._doc.get('classification', {})
        return classification.get('confidence', 0.0)
    
    @property
    def keywords(self):
        keywords_list = self._doc.get('keywords', [])
        # Converte para formato JSON string como no SQLite
        import json
        return json.dumps(keywords_list) if keywords_list else ''
    
    @property
    def directory(self):
        return self._doc.get('directory', '')
    
    def __repr__(self):
        return f"<MongoVideoRecord(file_name='{self.file_name}', category='{self.category}')>"
