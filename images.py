import os
import cv2
import numpy as np
from PIL import Image
import logging
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import config

class ImageAnalyzer:
    """
    Classe responsável por análise de imagens com IA
    - Gera legendas/descrições de imagens
    - Extrai palavras-chave
    - Classifica conteúdo visual
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pipeline de geração de legendas
        try:
            self.captioner = pipeline(
                "image-to-text",
                model="nlpconnect/vit-gpt2-image-captioning"
            )
            self.logger.info("Pipeline de legendas carregado com sucesso")
        except Exception as e:
            self.logger.warning(f"Erro ao carregar modelo de legendas: {e}")
            self.captioner = None
        
        # Pipeline de classificação de imagens (opcional)
        try:
            self.image_classifier = pipeline(
                "image-classification",
                model="google/vit-base-patch16-224"
            )
        except Exception as e:
            self.logger.warning(f"Erro ao carregar classificador de imagens: {e}")
            self.image_classifier = None
        
        # Vectorizador para extração de keywords
        self.vectorizer = TfidfVectorizer(
            max_features=50,
            stop_words=['de', 'da', 'do', 'para', 'com', 'em', 'no', 'na', 'um', 'uma', 'o', 'a', 'e', 'que']
        )
    
    def describe_image(self, image_path):
        """
        Gera descrição completa de uma imagem
        """
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(image_path):
                self.logger.error(f"Arquivo de imagem não encontrado: {image_path}")
                return None
            
            result = {
                'file_path': image_path,
                'file_name': os.path.basename(image_path),
                'file_size': os.path.getsize(image_path),
                'caption': '',
                'keywords': [],
                'visual_features': {},
                'classification': {}
            }
            
            # Análise visual básica
            result['visual_features'] = self._analyze_image_features(image_path)
            
            # Geração de legenda
            if self.captioner:
                result['caption'] = self._generate_caption(image_path)
                if result['caption']:
                    result['keywords'] = self._extract_keywords_from_text(result['caption'])
            
            # Classificação de conteúdo
            if self.image_classifier:
                result['classification'] = self._classify_image(image_path)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar imagem {image_path}: {str(e)}")
            return None
    
    def _generate_caption(self, image_path):
        """
        Gera legenda para a imagem usando IA
        """
        try:
            captions = self.captioner(image_path, max_new_tokens=50)
            if captions and len(captions) > 0:
                return captions[0]['generated_text']
            return ""
        except Exception as e:
            self.logger.error(f"Erro ao gerar legenda: {str(e)}")
            return ""
    
    def _classify_image(self, image_path):
        """
        Classifica o conteúdo da imagem
        """
        try:
            classifications = self.image_classifier(image_path, top_k=5)
            return {
                'labels': classifications,
                'top_label': classifications[0]['label'] if classifications else 'unknown',
                'confidence': classifications[0]['score'] if classifications else 0.0
            }
        except Exception as e:
            self.logger.error(f"Erro ao classificar imagem: {str(e)}")
            return {}
    
    def _analyze_image_features(self, image_path):
        """
        Análise visual básica da imagem
        """
        try:
            # Carrega imagem
            image = cv2.imread(image_path)
            if image is None:
                return {}
            
            # Dimensões
            height, width, channels = image.shape
            
            # Análise de cores
            colors = image.reshape(-1, 3)
            dominant_color = np.mean(colors, axis=0).tolist()
            
            # Brilho médio
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Detecção de faces
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            has_faces = len(faces) > 0
            
            # Análise de nitidez (usando variância do Laplaciano)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_sharp = laplacian_var > 100  # Threshold empírico
            
            return {
                'width': width,
                'height': height,
                'channels': channels,
                'dominant_color': dominant_color,
                'brightness': brightness,
                'has_faces': has_faces,
                'face_count': len(faces),
                'sharpness': laplacian_var,
                'is_sharp': is_sharp
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de features: {str(e)}")
            return {}
    
    def _extract_keywords_from_text(self, text, max_keywords=15):
        """
        Extrai palavras-chave do texto usando TF-IDF
        """
        if not text or len(text.strip()) < 3:
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
    
    def categorize_image(self, caption, visual_features, classification):
        """
        Categoriza imagem baseada na legenda e features visuais
        """
        try:
            # Palavras-chave por categoria (similar ao video_analysis.py)
            category_keywords = {
                'educacao': ['classroom', 'book', 'study', 'education', 'aula', 'livro', 'estudo'],
                'entretenimento': ['entertainment', 'fun', 'party', 'diversão', 'festa'],
                'arte': ['art', 'painting', 'drawing', 'sculpture', 'arte', 'pintura', 'desenho'],
                'natureza': ['nature', 'landscape', 'tree', 'flower', 'natureza', 'paisagem', 'árvore'],
                'pessoas': ['person', 'people', 'face', 'portrait', 'pessoa', 'pessoas', 'rosto'],
                'tecnologia': ['computer', 'technology', 'device', 'computador', 'tecnologia'],
                'comida': ['food', 'meal', 'cooking', 'comida', 'refeição', 'cozinha'],
                'veiculos': ['car', 'vehicle', 'transportation', 'carro', 'veículo', 'transporte'],
                'arquitetura': ['building', 'house', 'architecture', 'prédio', 'casa', 'arquitetura'],
                'outros': []
            }
            
            text_lower = caption.lower() if caption else ""
            scores = {}
            
            # Calcula score para cada categoria
            for category, keywords in category_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in text_lower:
                        score += text_lower.count(keyword)
                
                # Adiciona bonus baseado em features visuais
                if visual_features:
                    if category == 'pessoas' and visual_features.get('has_faces'):
                        score += 3
                    elif category == 'arte' and visual_features.get('brightness', 0) > 120:
                        score += 1
                
                # Usa classificação do modelo se disponível
                if classification and 'labels' in classification:
                    for label_info in classification['labels']:
                        label = label_info['label'].lower()
                        for keyword in keywords:
                            if keyword in label:
                                score += label_info['score'] * 2
                
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
            self.logger.error(f"Erro na categorização de imagem: {str(e)}")
            return {
                'category': 'outros',
                'confidence': 0.0,
                'scores': {}
            }
