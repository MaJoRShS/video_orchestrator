import os
import sys
import logging
import json
import argparse
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Importa módulos do sistema
from transcription import TranscriptionEngine
from video_analysis import VideoAnalyzer
# from images import ImageAnalyzer
from database import DatabaseManager, VideoRecord
from search_engine import ContentSearchEngine
import config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("orchestrator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class VideoOrchestrator:
    def __init__(self):
        self.transcription_engine = TranscriptionEngine()
        self.video_analyzer = VideoAnalyzer()
        # # Aqui eu acabei de colocar o esquema da imagem , preciso agora adicionar no meio do processamento do diretório a analise das imagens
        # self.image_analyzer = ImageAnalyzer()
        self.db_manager = DatabaseManager()
        self.search_engine = ContentSearchEngine(self.db_manager)
        
        logger.info("Inicializando orquestrador de vídeos")
    
    def process_video(self, video_path, progress_bar=None):
        """
        Processa um único vídeo: transcrição, análise, categorização e armazenamento
        """
        try:
            video_name = os.path.basename(video_path)
            
            # Cria barra de progresso específica para este vídeo se não foi fornecida
            if progress_bar is None:
                progress_bar = tqdm(total=7, desc=f"Processando {video_name[:30]}...", 
                                  unit="etapa", leave=True)
            
            progress_bar.set_description(f"📁 Verificando: {video_name[:30]}...")
            
            # Verifica se o vídeo já foi processado
            existing_record = self.db_manager.get_video_by_path(video_path)
            if existing_record:
                progress_bar.set_description(f"✅ Já processado: {video_name[:30]}")
                progress_bar.update(7)  # Completa a barra
                progress_bar.close()
                return existing_record.id
            
            progress_bar.update(1)
            progress_bar.set_description(f"📊 Criando registro: {video_name[:30]}...")
            
            # Cria registro para o vídeo
            video_record = VideoRecord(
                file_path=video_path,
                file_name=os.path.basename(video_path),
                file_size=os.path.getsize(video_path)
            )
            
            # Obtém duração do vídeo
            duration = self.transcription_engine.get_video_duration(video_path)
            if duration:
                video_record.duration = duration
            
            progress_bar.update(1)
            progress_bar.set_description(f"🎤 Transcrevendo: {video_name[:30]}...")
            
            # Transcrição
            transcription_results = self.transcription_engine.transcribe_video(
                video_path, languages=['pt'], progress_callback=progress_bar
            )
            
            if not transcription_results:
                progress_bar.set_description(f"❌ Falha na transcrição: {video_name[:30]}")
                progress_bar.close()
                return None
            
            progress_bar.update(1)
            progress_bar.set_description(f"💾 Salvando transcrição: {video_name[:30]}...")
            
            # Salva transcrições
            if 'pt' in transcription_results:
                video_record.transcript_pt = transcription_results['pt']['text']
            
            if 'en' in transcription_results:
                video_record.transcript_en = transcription_results['en']['text']
            
            progress_bar.update(1)
            progress_bar.set_description(f"👁️ Analisando visual: {video_name[:30]}...")
            
            # Análise visual
            frames = self.video_analyzer.extract_video_frames(video_path)
            visual_analysis = self.video_analyzer.analyze_visual_content(frames)
            
            progress_bar.update(1)
            progress_bar.set_description(f"🏷️ Classificando: {video_name[:30]}...")
            
            # Classificação
            if video_record.transcript_pt:
                classification = self.video_analyzer.classify_content(
                    video_record.transcript_pt, 
                    visual_analysis
                )
                
                video_record.category = classification['category']
                video_record.confidence_score = classification['confidence']
                
                # Extração de keywords
                keywords = self.video_analyzer.extract_keywords(video_record.transcript_pt)
                video_record.keywords = json.dumps(keywords)
                
                # Geração de contexto
                video_record.video_context = self.video_analyzer.generate_video_context(
                    video_record.transcript_pt,
                    visual_analysis,
                    classification
                )
            
            progress_bar.update(1)
            progress_bar.set_description(f"💾 Salvando no banco: {video_name[:30]}...")
            
            # Salva no banco de dados
            video_id = self.db_manager.add_video(video_record)
            
            # Atualiza índice de busca
            self.search_engine._update_search_index()
            
            progress_bar.update(1)
            progress_bar.set_description(f"✅ Concluído: {video_name[:30]}")
            progress_bar.close()
            
            return video_id
            
        except Exception as e:
            if progress_bar:
                progress_bar.set_description(f"❌ Erro: {video_name[:30]} - {str(e)[:50]}")
                progress_bar.close()
            logger.error(f"Erro ao processar vídeo {video_path}: {str(e)}")
            return None
    
    def process_directory(self, directory_path, recursive=True):
        """
        Processa todos os vídeos em um diretório
        """
        try:
            print(f"📁 Escaneando diretório: {directory_path}")
            
            video_paths = []
            directory = Path(directory_path)
            
            # Busca por arquivos de vídeo
            if recursive:
                for ext in config.VIDEO_EXTENSIONS:
                    video_paths.extend(list(directory.glob(f"**/*{ext}")))
            else:
                for ext in config.VIDEO_EXTENSIONS:
                    video_paths.extend(list(directory.glob(f"*{ext}")))
            
            if not video_paths:
                print(f"⚠️  Nenhum arquivo de vídeo encontrado em: {directory_path}")
                return []
            
            print(f"🎬 Encontrados {len(video_paths)} vídeos para processamento\n")
            
            # Barra de progresso geral para todos os vídeos
            overall_progress = tqdm(
                total=len(video_paths), 
                desc="📺 Processamento Geral", 
                unit="vídeo",
                position=0,
                leave=True
            )
            
            # Processa vídeos sequencialmente para melhor controle da progress bar
            results = []
            for i, video_path in enumerate(video_paths):
                try:
                    overall_progress.set_description(f"📺 [{i+1}/{len(video_paths)}] Processando vídeos")
                    video_id = self.process_video(str(video_path))
                    if video_id:
                        results.append(video_id)
                    overall_progress.update(1)
                except Exception as e:
                    logger.error(f"Erro ao processar {video_path}: {str(e)}")
                    overall_progress.update(1)
            
            overall_progress.set_description(f"✅ Processamento concluído: {len(results)}/{len(video_paths)} vídeos processados")
            overall_progress.close()
            
            print(f"\n🎉 Processamento concluído! {len(results)} vídeos processados com sucesso.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao processar diretório {directory_path}: {str(e)}")
            return []
    
    def search_videos(self, query):
        """
        Interface para busca de vídeos por texto
        """
        results = self.search_engine.search_by_text(query)
        return [
            {
                'id': r['video'].id,
                'file_name': r['video'].file_name,
                'category': r['video'].category,
                'context': r['video'].video_context,
                'score': r['similarity_score']
            }
            for r in results
        ]
    
    def search_by_category(self, category):
        """
        Interface para busca de vídeos por categoria
        """
        results = self.search_engine.search_by_category(category)
        return [
            {
                'id': r['video'].id,
                'file_name': r['video'].file_name,
                'context': r['video'].video_context,
                'confidence': r['confidence']
            }
            for r in results
        ]
    
    def search_by_keywords(self, keywords):
        """
        Interface para busca por palavras-chave
        """
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(',')]
        
        results = self.search_engine.search_by_keywords(keywords)
        return [
            {
                'id': r['video'].id,
                'file_name': r['video'].file_name,
                'category': r['video'].category,
                'context': r['video'].video_context,
                'matched_keywords': r['matched_keywords'],
                'score': r['score']
            }
            for r in results
        ]
    
    def get_content_summary(self):
        """
        Retorna um resumo do conteúdo processado
        """
        return self.search_engine.get_content_summary()

def main():
    # Configuração dos argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Orquestrador de processamento de vídeos com IA')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comando a ser executado')
    
    # Comando para processar diretório
    process_parser = subparsers.add_parser('process', help='Processar vídeos')
    process_parser.add_argument('directory', help='Diretório contendo vídeos para processamento')
    process_parser.add_argument('--recursive', '-r', action='store_true', help='Buscar vídeos recursivamente em subdiretórios')
    
    # Comando para buscar vídeos
    search_parser = subparsers.add_parser('search', help='Buscar vídeos')
    search_parser.add_argument('--query', '-q', help='Termo de busca textual')
    search_parser.add_argument('--category', '-c', help='Buscar por categoria')
    search_parser.add_argument('--keywords', '-k', help='Buscar por palavras-chave (separadas por vírgula)')
    
    # Comando para obter resumo
    subparsers.add_parser('summary', help='Mostrar resumo do conteúdo processado')
    
    # Parseia os argumentos
    args = parser.parse_args()
    
    # Inicializa o orquestrador
    orchestrator = VideoOrchestrator()
    
    # Executa o comando especificado
    if args.command == 'process':
        start_time = time.time()
        orchestrator.process_directory(args.directory, args.recursive)
        elapsed_time = time.time() - start_time
        logger.info(f"Processamento concluído em {elapsed_time:.2f} segundos")
        
    elif args.command == 'search':
        if args.query:
            results = orchestrator.search_videos(args.query)
            print(f"\nResultados da busca por '{args.query}':")
            for i, res in enumerate(results, 1):
                print(f"\n{i}. {res['file_name']} (Categoria: {res['category']})")
                print(f"   Score: {res['score']:.4f}")
                print(f"   Contexto: {res['context'][:150]}...")
        
        elif args.category:
            results = orchestrator.search_by_category(args.category)
            print(f"\nVídeos da categoria '{args.category}':")
            for i, res in enumerate(results, 1):
                print(f"\n{i}. {res['file_name']} (Confiança: {res['confidence']:.2f})")
                print(f"   Contexto: {res['context'][:150]}...")
        
        elif args.keywords:
            results = orchestrator.search_by_keywords(args.keywords)
            print(f"\nResultados da busca por palavras-chave '{args.keywords}':")
            for i, res in enumerate(results, 1):
                print(f"\n{i}. {res['file_name']} (Categoria: {res['category']})")
                print(f"   Palavras encontradas: {', '.join(res['matched_keywords'])}")
                print(f"   Score: {res['score']}")
                print(f"   Contexto: {res['context'][:150]}...")
        
        else:
            print("Erro: Especifique um critério de busca (--query, --category ou --keywords)")
    
    elif args.command == 'summary':
        summary = orchestrator.get_content_summary()
        
        print("\n=== RESUMO DO CONTEÚDO PROCESSADO ===")
        print(f"Total de vídeos: {summary.get('total_videos', 0)}")
        print(f"Duração total: {summary.get('total_duration_hours', 0):.1f} horas")
        
        print("\nVídeos por categoria:")
        for category, count in summary.get('categories', {}).items():
            print(f"  - {category}: {count} vídeos")
        
        print("\nIdiomas:")
        languages = summary.get('languages', {})
        print(f"  - Português: {languages.get('pt', 0)} vídeos")
        print(f"  - Inglês: {languages.get('en', 0)} vídeos")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
