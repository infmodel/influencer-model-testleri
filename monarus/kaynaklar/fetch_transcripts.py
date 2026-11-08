# Kullanım: python fetch_transcripts.py  (kaynaklar/ içinden). Çıktı transcripts/ (repoya girmez, telif).
import csv, time, os
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
ok=fail=0
os.makedirs('transcripts', exist_ok=True)
for row in csv.DictReader(open('video_listesi.csv', encoding='utf-8')):
    vid, title = row['video_id'], row['baslik']
    out = f'transcripts/{vid}.txt'
    if os.path.exists(out) and os.path.getsize(out) > 0: ok+=1; continue
    try:
        tl = api.list(vid)
        try: t = tl.find_transcript(['tr'])
        except Exception: t = tl.find_transcript(['en'])
        segs = t.fetch()
        with open(out,'w',encoding='utf-8') as f:
            f.write(f'# {title}\n# lang={t.language_code} generated={t.is_generated}\n')
            for s in segs:
                m,sec = divmod(int(s.start),60)
                f.write(f'[{m:02d}:{sec:02d}] {s.text}\n')
        ok+=1
    except Exception as e:
        fail+=1; print('FAIL', vid, title, type(e).__name__, str(e)[:120], flush=True)
    time.sleep(1.5)
print('ok', ok, 'fail', fail)
