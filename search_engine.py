import logging
import json
from database import DatabaseManager, VideoRecord
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ContentSearchEngine:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.vectorizer = TfidfVectorizer(
            stop_words=['de', 'da', 'do', 'para', 'com', 'em', 'no', 'na', 'um', 'uma', 'o', 'a', 'e', 'que']
        )
        self.corpus = []
        self.video_ids = []
        self._update_search_index()
    
    def _update_search_index(self):
        """
        Atualiza o índice de busca com todos os vídeos do banco
        """
        try:
            videos = self.db_manager.get_all_videos()
            self.corpus = []
            self.video_ids = []
            
            for video in videos:
                # Combina transcrição, contexto e keywords para busca
                search_text = ""
                if video.transcript_pt:
                    search_text += video.transcript_pt + " "
                if video.video_context:
                    search_text += video.video_context + " "
                if video.keywords:
                    try:
                        keywords = json.loads(video.keywords)
                        search_text += " ".join(keywords) + " "
                    except:
                        pass
                
                if search_text.strip():
                    self.corpus.append(search_text.strip())
                    self.video_ids.append(video.id)
            
            # Cria a matriz TF-IDF
            if self.corpus:
                self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
            else:
                self.tfidf_matrix = None
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar índice de busca: {str(e)}")
    
    def search_by_text(self, query, limit=10):
        """
        Busca por similaridade textual usando TF-IDF
        """
        try:
            if not self.corpus or self.tfidf_matrix is None:
                return []
            
            # Transforma a query usando o mesmo vectorizer
            query_vec = self.vectorizer.transform([query.lower()])
            
            # Calcula similaridade coseno
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Ordena por similaridade
            similar_indices = similarities.argsort()[::-1]
            
            results = []
            for idx in similar_indices[:limit]:
                if similarities[idx] > 0:  # Só retorna resultados com similaridade > 0
                    video_id = self.video_ids[idx]
                    video = self.db_manager.session.query(VideoRecord).filter_by(id=video_id).first()
                    if video:
                        results.append({
                            'video': video,
                            'similarity_score': float(similarities[idx])
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca textual: {str(e)}")
            return []
    
    def search_by_keywords(self, keywords, exact_match=False):
        """
        Busca por palavras-chave específicas
        """
        try:
            if isinstance(keywords, str):
                keywords = [keywords]
            
            results = []
            videos = self.db_manager.get_all_videos()
            
            for video in videos:
                score = 0
                matched_keywords = []
                
                # Busca na transcrição
                if video.transcript_pt:
                    text_lower = video.transcript_pt.lower()
                    for keyword in keywords:
                        keyword_lower = keyword.lower()
                        if exact_match:
                            if f" {keyword_lower} " in f" {text_lower} ":
                                score += 2
                                matched_keywords.append(keyword)
                        else:
                            if keyword_lower in text_lower:
                                score += text_lower.count(keyword_lower)
                                matched_keywords.append(keyword)
                
                # Busca no contexto
                if video.video_context:
                    context_lower = video.video_context.lower()
                    for keyword in keywords:
                        keyword_lower = keyword.lower()
                        if keyword_lower in context_lower:
                            score += 1
                            if keyword not in matched_keywords:
                                matched_keywords.append(keyword)
                
                # Busca nas keywords extraídas
                if video.keywords:
                    try:
                        video_keywords = json.loads(video.keywords)
                        for keyword in keywords:
                            keyword_lower = keyword.lower()
                            for vk in video_keywords:
                                if keyword_lower in vk.lower():
                                    score += 1
                                    if keyword not in matched_keywords:
                                        matched_keywords.append(keyword)
                    except:
                        pass
                
                if score > 0:
                    results.append({
                        'video': video,
                        'score': score,
                        'matched_keywords': matched_keywords
                    })
            
            # Ordena por score decrescente
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca por keywords: {str(e)}")
            return []
    
    def search_by_category(self, category):
        """
        Busca vídeos por categoria
        """
        try:
            videos = self.db_manager.get_videos_by_category(category)
            results = []
            
            for video in videos:
                results.append({
                    'video': video,
                    'confidence': video.confidence_score or 0.0
                })
            
            # Ordena por confiança decrescente
            results.sort(key=lambda x: x['confidence'], reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca por categoria: {str(e)}")
            return []
    
    def advanced_search(self, query, category=None, min_duration=None, max_duration=None):
        """
        Busca avançada combinando múltiplos critérios
        """
        try:
            results = []
            
            # Busca textual inicial
            if query:
                text_results = self.search_by_text(query)
                results = text_results
            else:
                # Se não há query, pega todos os vídeos
                videos = self.db_manager.get_all_videos()
                results = [{'video': video, 'similarity_score': 1.0} for video in videos]
            
            # Filtra por categoria
            if category and category != 'todos':
                results = [r for r in results if r['video'].category == category]
            
            # Filtra por duração
            if min_duration is not None:
                results = [r for r in results if r['video'].duration and r['video'].duration >= min_duration]
            
            if max_duration is not None:
                results = [r for r in results if r['video'].duration and r['video'].duration <= max_duration]
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca avançada: {str(e)}")
            return []
    
    def get_content_summary(self):
        """
        Retorna resumo do conteúdo na base de conhecimento
        """
        try:
            videos = self.db_manager.get_all_videos()
            
            summary = {
                'total_videos': len(videos),
                'categories': {},
                'total_duration': 0,
                'languages': {'pt': 0, 'en': 0}
            }
            
            for video in videos:
                # Conta por categoria
                category = video.category or 'outros'
                summary['categories'][category] = summary['categories'].get(category, 0) + 1
                
                # Soma duração total
                if video.duration:
                    summary['total_duration'] += video.duration
                
                # Conta idiomas
                if video.transcript_pt:
                    summary['languages']['pt'] += 1
                if video.transcript_en:
                    summary['languages']['en'] += 1
            
            # Converte duração para formato legível
            total_hours = summary['total_duration'] / 3600
            summary['total_duration_hours'] = round(total_hours, 2)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo: {str(e)}")
            return {}
    
    def find_similar_videos(self, video_id, limit=5):
        """
        Encontra vídeos similares a um vídeo específico
        """
        try:
            target_video = self.db_manager.session.query(VideoRecord).filter_by(id=video_id).first()
            if not target_video or not target_video.transcript_pt:
                return []
            
            # Usa a transcrição do vídeo como query
            query = target_video.transcript_pt
            results = self.search_by_text(query, limit=limit+1)  # +1 porque vai incluir o próprio vídeo
            
            # Remove o próprio vídeo dos resultados
            similar_videos = [r for r in results if r['video'].id != video_id]
            
            return similar_videos[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar vídeos similares: {str(e)}")
            return []
