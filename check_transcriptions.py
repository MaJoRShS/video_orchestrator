#!/usr/bin/env python3
"""
Script para visualizar transcrições armazenadas no banco de dados
"""
import sqlite3
import sys

def check_transcriptions():
    try:
        conn = sqlite3.connect('video_database.db')
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("📋 Tabelas encontradas:", [table[0] for table in tables])
        
        # Verifica se há vídeos no banco
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]
        print(f"📊 Total de vídeos no banco: {total_videos}")
        
        if total_videos == 0:
            print("⚠️ Nenhum vídeo encontrado no banco de dados.")
            return
        
        # Lista vídeos com transcrições
        cursor.execute("""
            SELECT id, file_name, transcript_pt, transcript_en, created_at 
            FROM videos 
            WHERE transcript_pt IS NOT NULL OR transcript_en IS NOT NULL
            ORDER BY created_at DESC
        """)
        
        videos_with_transcripts = cursor.fetchall()
        
        if not videos_with_transcripts:
            print("⚠️ Nenhuma transcrição encontrada no banco de dados.")
            return
        
        print(f"\n🎤 Vídeos com transcrições ({len(videos_with_transcripts)}):")
        print("=" * 80)
        
        for video in videos_with_transcripts:
            video_id, file_name, transcript_pt, transcript_en, created_at = video
            
            print(f"\n📹 ID: {video_id}")
            print(f"📁 Arquivo: {file_name}")
            print(f"📅 Processado em: {created_at}")
            
            if transcript_pt:
                print(f"🇧🇷 Transcrição (PT) - {len(transcript_pt)} caracteres:")
                print(f"   {transcript_pt[:200]}{'...' if len(transcript_pt) > 200 else ''}")
            
            if transcript_en:
                print(f"🇺🇸 Transcrição (EN) - {len(transcript_en)} caracteres:")
                print(f"   {transcript_en[:200]}{'...' if len(transcript_en) > 200 else ''}")
            
            print("-" * 80)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao acessar banco de dados: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def show_full_transcript(video_id):
    """Mostra a transcrição completa de um vídeo específico"""
    try:
        conn = sqlite3.connect('video_database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT file_name, transcript_pt, transcript_en 
            FROM videos 
            WHERE id = ?
        """, (video_id,))
        
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ Vídeo com ID {video_id} não encontrado.")
            return
        
        file_name, transcript_pt, transcript_en = result
        
        print(f"\n📹 Arquivo: {file_name}")
        print("=" * 80)
        
        if transcript_pt:
            print(f"\n🇧🇷 TRANSCRIÇÃO COMPLETA (PORTUGUÊS):")
            print(f"{transcript_pt}")
        
        if transcript_en:
            print(f"\n🇺🇸 TRANSCRIÇÃO COMPLETA (INGLÊS):")
            print(f"{transcript_en}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao acessar banco de dados: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            video_id = int(sys.argv[1])
            show_full_transcript(video_id)
        except ValueError:
            print("❌ ID do vídeo deve ser um número.")
    else:
        check_transcriptions()
        print(f"\n💡 Para ver a transcrição completa de um vídeo, use:")
        print(f"   python check_transcriptions.py <ID_DO_VIDEO>")
