import os
import csv
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs

# --- 1. PENGATURAN (GANTI INI) ---

VIDEO_URLS = [
    "https://youtu.be/MIo4tGN11j0?si=_u13wYQ-sdvNoJnX",
    "https://youtu.be/QE-L40X-DYg?si=NTfyJjQGEes99Oc5",
    "https://youtu.be/ngj-6pkSsaQ?si=oCP7uWl0jsEGvd91",
]
TARGET_PERSENTASE = 60  # Ambil 60% dari total komentar setiap video
MAX_KOMENTAR_PER_VIDEO = 500  # Batas maksimal komentar per video
NAMA_FILE_OUTPUT = "raw-scrape-yt.csv"

# Simpan output di folder script (misalnya folder kabur-aja-dulu tempat scrape.py ada)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, NAMA_FILE_OUTPUT)

# --- 2. FUNGSI HELPER ---

def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def get_total_comments(youtube, video_id):
    """Mengambil jumlah total komentar dari video statistics"""
    try:
        request = youtube.videos().list(
            part="statistics",
            id=video_id
        )
        response = request.execute()
        
        if response['items']:
            total = int(response['items'][0]['statistics'].get('commentCount', 0))
            return total
        return 0
    except Exception as e:
        print(f"Error mendapatkan total komentar: {e}")
        return 0

# --- 3. FUNGSI UTAMA SCRAPING ---

def scrape_comments():
    print("Memulai proses scraping dengan YouTube Data API...")
    print(f"Output akan disimpan di: {OUTPUT_PATH}")
    
    load_dotenv()
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not API_KEY:
        print("Error: YOUTUBE_API_KEY tidak ditemukan di file .env")
        return

    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
    except Exception as e:
        print(f"Error saat membangun layanan YouTube: {e}")
        return

    header = ['Video_ID', 'Teks_Komentar']
    total_komentar_keseluruhan = 0
    
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for idx, VIDEO_URL in enumerate(VIDEO_URLS, 1):
            print(f"\n{'='*60}")
            print(f"🎬 Video {idx}/{len(VIDEO_URLS)}: {VIDEO_URL}")
            print(f"{'='*60}")
            
            video_id = get_video_id(VIDEO_URL)
            if not video_id:
                print(f"❌ Error: Tidak dapat mengekstrak Video ID dari URL: {VIDEO_URL}")
                continue
            
            print(f"✅ Video ID terdeteksi: {video_id}")
            
            # Dapatkan total komentar dari video
            total_komentar_video = get_total_comments(youtube, video_id)
            
            if total_komentar_video == 0:
                print("⚠️  Error: Tidak dapat mendapatkan jumlah komentar atau komentar dinonaktifkan.")
                continue
            
            # Hitung target berdasarkan persentase
            TARGET_KOMENTAR = int(total_komentar_video * (TARGET_PERSENTASE / 100))
            
            # Terapkan batas maksimal
            TARGET_KOMENTAR = min(TARGET_KOMENTAR, MAX_KOMENTAR_PER_VIDEO)
            
            print(f"📊 Total komentar di video: {total_komentar_video:,}")
            print(f"🎯 Target scraping ({TARGET_PERSENTASE}%): {TARGET_KOMENTAR:,} komentar (max: {MAX_KOMENTAR_PER_VIDEO})")
            print("-"*60)

            total_komentar_video_didapat = 0
            next_page_token = None

            while True:
                try:
                    request = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        textFormat="plainText",
                        maxResults=100,
                        pageToken=next_page_token
                    )
                    response = request.execute()

                    for item in response['items']:
                        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                        teks_bersih = comment.replace('\n', ' ').replace('\r', ' ')
                        writer.writerow([video_id, teks_bersih])
                        total_komentar_video_didapat += 1
                        total_komentar_keseluruhan += 1

                    persentase_sekarang = (total_komentar_video_didapat / TARGET_KOMENTAR) * 100
                    print(f"📥 Video ini: {total_komentar_video_didapat}/{TARGET_KOMENTAR} ({persentase_sekarang:.1f}%) | Total keseluruhan: {total_komentar_keseluruhan:,}")

                    next_page_token = response.get('nextPageToken')
                    if not next_page_token or total_komentar_video_didapat >= TARGET_KOMENTAR:
                        break
                
                except HttpError as e:
                    if e.resp.status == 403 and "commentsDisabled" in str(e.content):
                        print("❌ Error: Komentar dinonaktifkan untuk video ini.")
                    else:
                        print(f"❌ Terjadi error API: {e}")
                    break
                except Exception as e:
                    print(f"❌ Terjadi error tidak terduga: {e}")
                    break
            
            persentase_akhir_video = (total_komentar_video_didapat / total_komentar_video) * 100
            print(f"✅ Selesai untuk video ini! Berhasil: {total_komentar_video_didapat:,} komentar ({persentase_akhir_video:.1f}%)")

    print(f"\n{'='*60}")
    print(f"🎉 SCRAPING SELESAI!")
    print(f"{'='*60}")
    print(f"📹 Total video diproses: {len(VIDEO_URLS)}")
    print(f"💬 Total komentar terkumpul: {total_komentar_keseluruhan:,}")
    print(f"💾 Disimpan di: '{OUTPUT_PATH}'")
    print(f"{'='*60}")

if __name__ == "__main__":
    scrape_comments()
