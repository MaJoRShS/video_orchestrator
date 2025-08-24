import whisper
import os
import logging
import signal
import threading
import torch
from moviepy.video.io.VideoFileClip import VideoFileClip
import config

class TranscriptionEngine:
    def __init__(self, model_size=config.WHISPER_MODEL):
        """
        Inicializa o motor de transcrição com Whisper
        model_size: tiny, base, small, medium, large
        """
        self.logger = logging.getLogger(__name__)
        
        # Verifica disponibilidade de GPU
        self.device = self._get_device()
        self.logger.info(f"Usando dispositivo: {self.device}")
        
        # Carrega o modelo com o dispositivo apropriado
        self.model = whisper.load_model(model_size, device=self.device)
        
        # Log informações sobre GPU se disponível
        if self.device != "cpu":
            self._log_gpu_info()
    
    def _get_device(self):
        """
        Determina qual dispositivo usar (GPU ou CPU)
        """
        if config.USE_GPU and torch.cuda.is_available():
            try:
                # Testa se o dispositivo especificado está disponível
                device = torch.device(config.GPU_DEVICE)
                # Teste simples para verificar se o dispositivo funciona
                torch.cuda.get_device_properties(device)
                return config.GPU_DEVICE
            except Exception as e:
                self.logger.warning(f"GPU especificada ({config.GPU_DEVICE}) não disponível: {e}")
                self.logger.warning("Fallback para CPU")
                return "cpu"
        elif config.USE_GPU and not torch.cuda.is_available():
            self.logger.warning("GPU solicitada mas CUDA não está disponível. Usando CPU.")
            return "cpu"
        else:
            return "cpu"
    
    def _log_gpu_info(self):
        """
        Log informações sobre a GPU sendo usada
        """
        try:
            gpu_id = int(self.device.split(':')[1])
            gpu_name = torch.cuda.get_device_name(gpu_id)
            gpu_memory = torch.cuda.get_device_properties(gpu_id).total_memory / (1024**3)
            self.logger.info(f"GPU detectada: {gpu_name}")
            self.logger.info(f"Memória GPU: {gpu_memory:.1f} GB")
        except Exception as e:
            self.logger.warning(f"Erro ao obter informações da GPU: {e}")
    
    def extract_audio_from_video(self, video_path, audio_path=None):
        """
        Extrai áudio do vídeo e salva como arquivo temporário
        """
        try:
            if audio_path is None:
                # Salva o arquivo temporário no diretório atual com nome simples
                import time
                timestamp = str(int(time.time()))
                audio_path = f"temp_audio_{timestamp}.wav"
            
            video = VideoFileClip(video_path)
            self.logger.info(f"Extraindo áudio para: {audio_path}")
            video.audio.write_audiofile(audio_path, logger=None)
            video.close()
            
            # Verifica se o arquivo foi criado
            if os.path.exists(audio_path):
                self.logger.info(f"Arquivo de áudio criado com sucesso: {audio_path}")
                return audio_path
            else:
                self.logger.error(f"Arquivo de áudio não foi criado: {audio_path}")
                return None
        except Exception as e:
            self.logger.error(f"Erro ao extrair áudio de {video_path}: {str(e)}")
            return None
    
    def transcribe_audio_with_timeout(self, audio_path, language=None, timeout=300, progress_callback=None):
        """
        Transcreve áudio com timeout para evitar travamento
        """
        result_container = [None]
        exception_container = [None]
        
        def transcribe_worker():
            try:
                result = self.model.transcribe(
                    audio_path, 
                    language=language,
                    word_timestamps=True
                )
                result_container[0] = {
                    'text': result['text'],
                    'language': result['language'],
                    'segments': result['segments']
                }
            except Exception as e:
                exception_container[0] = e
        
        # Inicia thread para transcrição
        thread = threading.Thread(target=transcribe_worker)
        thread.daemon = True
        thread.start()
        
        # Aguarda com timeout mostrando progresso
        import time
        start_time = time.time()
        while thread.is_alive():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                self.logger.error(f"Timeout na transcrição de {audio_path} após {timeout} segundos")
                return None
            
            if progress_callback:
                progress_percent = min(95, (elapsed / timeout) * 100)
                progress_callback.set_description(
                    f"🎤 Transcrevendo... {progress_percent:.0f}% ({elapsed:.0f}s/{timeout}s)"
                )
            
            time.sleep(1)
        
        if exception_container[0]:
            raise exception_container[0]
        
        return result_container[0]
    
    def transcribe_audio(self, audio_path, language=None, progress_callback=None):
        """
        Transcreve áudio para texto
        language: 'pt' para português, 'en' para inglês, None para auto-detect
        """
        try:
            # Verifica se o arquivo existe antes de tentar transcrever
            if not os.path.exists(audio_path):
                self.logger.error(f"Arquivo de áudio não encontrado para transcrição: {audio_path}")
                return None
            
            self.logger.info(f"Iniciando transcrição do arquivo: {audio_path}")
            
            # Verificação adicional antes de chamar o Whisper
            file_size = os.path.getsize(audio_path)
            self.logger.info(f"Tamanho do arquivo: {file_size} bytes")
            
            # Verifica se o arquivo é muito grande (mais de 100MB)
            if file_size > 100 * 1024 * 1024:  # 100MB
                self.logger.warning(f"Arquivo muito grande ({file_size/1024/1024:.1f}MB). Pode demorar muito para processar.")
                timeout = 600  # 10 minutos para arquivos grandes
            else:
                timeout = 300  # 5 minutos para arquivos normais
            
            self.logger.info(f"Iniciando transcrição com timeout de {timeout} segundos...")
            
            # Pausa para garantir que o arquivo seja totalmente liberado
            import time
            time.sleep(1)
            
            # Usa transcrição com timeout
            result = self.transcribe_audio_with_timeout(audio_path, language, timeout, progress_callback)
            
            if result:
                self.logger.info(f"Transcrição concluída com sucesso: {len(result['text'])} caracteres")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na transcrição de {audio_path}: {str(e)}")
            return None
    
    def transcribe_video(self, video_path, languages=['pt', 'en'], progress_callback=None):
        """
        Pipeline completo: extrai áudio do vídeo e transcreve
        """
        results = {}
        
        if progress_callback:
            progress_callback.set_description(f"🎤 Extraindo áudio...")
        
        # Extrai áudio do vídeo
        audio_path = self.extract_audio_from_video(video_path)
        if not audio_path:
            return None
        
        try:
            # Transcreve em português
            if 'pt' in languages:
                if progress_callback:
                    progress_callback.set_description(f"🎤 Transcrevendo em português...")
                pt_result = self.transcribe_audio(audio_path, language='pt', progress_callback=progress_callback)
                if pt_result:
                    results['pt'] = pt_result
            
            # Transcreve em inglês
            if 'en' in languages:
                if progress_callback:
                    progress_callback.set_description(f"🎤 Transcrevendo em inglês...")
                en_result = self.transcribe_audio(audio_path, language='en', progress_callback=progress_callback)
                if en_result:
                    results['en'] = en_result
            
            # Remove arquivo de áudio temporário
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no pipeline de transcrição: {str(e)}")
            # Limpa arquivo temporário em caso de erro
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return None
    
    def get_video_duration(self, video_path):
        """
        Obtém a duração do vídeo em segundos
        """
        try:
            video = VideoFileClip(video_path)
            duration = video.duration
            video.close()
            return duration
        except Exception as e:
            self.logger.error(f"Erro ao obter duração do vídeo {video_path}: {str(e)}")
            return None
