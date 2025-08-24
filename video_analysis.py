import cv2
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import logging
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import config

class VideoAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Inicializa pipeline de classificação de texto para português
        try:
            self.text_classifier = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
        except Exception as e:
            self.logger.warning(f"Erro ao carregar modelo de classificação: {e}")
            self.text_classifier = None
        
        # Vectorizador para extração de keywords
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words=['de', 'da', 'do', 'para', 'com', 'em', 'no', 'na', 'um', 'uma', 'o', 'a', 'e', 'que']
        )
    
    def extract_video_frames(self, video_path, num_frames=10):
        """
        Extrai frames representativos do vídeo para análise visual
        """
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                return []
            
            frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
            frames = []
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            return frames
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair frames de {video_path}: {str(e)}")
            return []
    
    def analyze_visual_content(self, frames):
        """
        Análise básica do conteúdo visual (cores, movimento, etc.)
        """
        if not frames:
            return {}
        
        analysis = {
            'brightness': [],
            'dominant_colors': [],
            'has_faces': False,
            'scene_changes': 0
        }
        
        try:
            prev_hist = None
            
            for frame in frames:
                # Análise de brilho
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                analysis['brightness'].append(brightness)
                
                # Análise de cores dominantes (simplificada)
                colors = frame.reshape(-1, 3)
                dominant_color = np.mean(colors, axis=0)
                analysis['dominant_colors'].append(dominant_color.tolist())
                
                # Detecção básica de faces
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) > 0:
                    analysis['has_faces'] = True
                
                # Análise de mudanças de cena
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                if prev_hist is not None:
                    correlation = cv2.compareHist(hist, prev_hist, cv2.HISTCMP_CORREL)
                    if correlation < 0.7:  # Threshold para mudança de cena
                        analysis['scene_changes'] += 1
                prev_hist = hist
            
            # Calcular médias
            analysis['avg_brightness'] = np.mean(analysis['brightness'])
            analysis['brightness_variance'] = np.var(analysis['brightness'])
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise visual: {str(e)}")
            return {}
    
    def extract_keywords(self, text, max_keywords=20):
        """
        Extrai palavras-chave do texto usando TF-IDF
        """
        if not text or len(text.strip()) < 10:
            return []
        
        try:
            # Preprocessa o texto
            text_clean = text.lower().strip()
            
            # Extrai keywords usando TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform([text_clean])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Cria lista de (palavra, score) e ordena por score
            word_scores = list(zip(feature_names, tfidf_scores))
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Retorna as top palavras-chave
            keywords = [word for word, score in word_scores[:max_keywords] if score > 0]
            return keywords
            
        except Exception as e:
            self.logger.error(f"Erro na extração de keywords: {str(e)}")
            return []
    
    def classify_content(self, transcript, visual_analysis):
        """
        Classifica o conteúdo baseado na transcrição e análise visual
        """
        try:
            # Palavras-chave por categoria
            category_keywords = {
                'educacao': ['aula', 'ensino', 'aprender', 'estudar', 'explicar', 'conhecimento', 'educação'],
                'entretenimento': ['diversão', 'entretenimento', 'filme', 'série', 'comédia', 'drama'],
                'noticias': ['notícia', 'jornal', 'informação', 'reportagem', 'atualidade'],
                'esportes': ['futebol', 'basquete', 'esporte', 'jogo', 'competição', 'atleta'],
                'tecnologia': ['tecnologia', 'computador', 'software', 'programação', 'digital'],
                'culinaria': ['receita', 'cozinhar', 'comida', 'ingrediente', 'culinária'],
                'musica': ['música', 'cantar', 'instrumento', 'banda', 'som', 'melodia'],
                'gaming': ['game', 'jogo', 'jogar', 'gamer', 'gameplay', 'videogame'],
                'tutorial': ['como fazer', 'tutorial', 'passo a passo', 'ensinar', 'guia'],
                'documentario': ['documentário', 'história', 'realidade', 'investigação'],
                'adulto': ['sexo', 'adulto', 'íntimo', 'sensual', 'erótico', 'pornô'],
                'outros': []
            }
            
            text_lower = transcript.lower()
            scores = {}
            
            # Calcula score para cada categoria
            for category, keywords in category_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in text_lower:
                        score += text_lower.count(keyword)
                
                # Adiciona bonus baseado em análise visual se disponível
                if visual_analysis and category == 'adulto':
                    # Critérios visuais para conteúdo adulto (básico)
                    if visual_analysis.get('has_faces') and visual_analysis.get('avg_brightness', 0) > 100:
                        score += 2
                
                scores[category] = score
            
            # Encontra a categoria com maior score
            if max(scores.values()) == 0:
                predicted_category = 'outros'
                confidence = 0.5
            else:
                predicted_category = max(scores, key=scores.get)
                total_score = sum(scores.values())
                confidence = scores[predicted_category] / total_score if total_score > 0 else 0.5
            
            return {
                'category': predicted_category,
                'confidence': confidence,
                'scores': scores
            }
            
        except Exception as e:
            self.logger.error(f"Erro na classificação de conteúdo: {str(e)}")
            return {
                'category': 'outros',
                'confidence': 0.0,
                'scores': {}
            }
    
    def generate_video_context(self, transcript, visual_analysis, classification):
        """
        Gera contexto do vídeo baseado em todas as análises
        """
        try:
            context_parts = []
            
            # Resumo da transcrição
            if transcript:
                words = transcript.split()
                if len(words) > 100:
                    summary = ' '.join(words[:100]) + '...'
                else:
                    summary = transcript
                context_parts.append(f"Transcrição: {summary}")
            
            # Informações visuais
            if visual_analysis:
                if visual_analysis.get('has_faces'):
                    context_parts.append("Vídeo contém pessoas/faces")
                
                brightness = visual_analysis.get('avg_brightness', 0)
                if brightness > 150:
                    context_parts.append("Vídeo com boa iluminação")
                elif brightness < 50:
                    context_parts.append("Vídeo com pouca iluminação")
                
                scene_changes = visual_analysis.get('scene_changes', 0)
                if scene_changes > 5:
                    context_parts.append("Vídeo dinâmico com várias cenas")
                elif scene_changes < 2:
                    context_parts.append("Vídeo estático ou poucas cenas")
            
            # Classificação
            if classification:
                category = classification.get('category', 'outros')
                confidence = classification.get('confidence', 0)
                context_parts.append(f"Classificado como: {category} (confiança: {confidence:.2f})")
            
            return ' | '.join(context_parts)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar contexto: {str(e)}")
            return "Contexto não disponível"
