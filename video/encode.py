from pathlib import Path
import json,subprocess,bisect,hashlib
from PIL import Image
p=Path(__file__).resolve().parent;rows=json.loads((p/'capture.json').read_text());im=Image.open(p/'frames'/rows[0]['file']);w,h=im.size;w+=w%2;h+=h%2
ff=Path('work/day07-env/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v9.0').resolve();out=p/'Day22-Projections-operation.mp4'
pr=subprocess.Popen([str(ff),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
times=[r['t'] for r in rows];last=None
for i in range(32*30):
 r=rows[max(0,bisect.bisect_right(times,i/30)-1)]
 if r['file']!=last:
  im=Image.open(p/'frames'/r['file']).convert('RGB');can=Image.new('RGB',(w,h),'#10232d');can.paste(im,(0,0));buf=can.tobytes();last=r['file']
 pr.stdin.write(buf)
pr.stdin.close();assert pr.wait()==0
subprocess.run([str(ff),'-v','error','-i',str(out),'-f','null','-'],check=True)
for sec in [1,3,7,11,15,19,23,27,31]:
 r=rows[max(0,bisect.bisect_right(times,sec)-1)];Image.open(p/'frames'/r['file']).save(p/f'preview-{sec}.png')
q={'seconds':32,'resolution':[w,h],'encoded_fps':30,'captured_frames':len(rows),'capture':'Actual browser screenshots timestamped during UI operations; no synthesized map frames','audio':'none; map has no sound','max_capture_gap_seconds':max(b-a for a,b in zip(times,times[1:])),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decode':'PASS'};(p/'qa.json').write_text(json.dumps(q,indent=2));print(q)
