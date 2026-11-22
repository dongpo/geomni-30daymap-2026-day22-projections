from pathlib import Path
import json,math,hashlib
from collections import defaultdict
from shapely.geometry import shape,box,Polygon
from shapely.ops import transform
from pyproj import Proj,Geod
p=Path(__file__).resolve().parents[1];g=Geod(ellps='WGS84');projs=[Proj('+proj=merc +ellps=WGS84 +lon_0=0 +units=m'),Proj('+proj=eqearth +ellps=WGS84 +lon_0=0 +units=m')];raw=json.loads((p/'source/countries.geojson').read_text());out=[];tot=defaultdict(lambda:[0,0,0]);errors=[]
def densify(r):
 out=[]
 for a,b in zip(r,r[1:]):
  n=max(1,math.ceil(max(abs(a[0]-b[0]),abs(a[1]-b[1]))/.2))
  for i in range(n):out.append([a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n])
 out.append(list(r[-1]));return out
def polygon_parts(geom):
 if geom.geom_type=='Polygon':return [geom]
 return [p for c in getattr(geom,'geoms',[]) for p in polygon_parts(c)]
for f in raw['features']:
 props=f['properties'];cont=props['CONTINENT'];name=props['NAME_EN']
 if cont in ['Antarctica','Seven seas (open ocean)']:continue
 geom=shape(f['geometry']).intersection(box(-180,-60,180,85));polys=polygon_parts(geom);rings=[];areas=[0,0,0]
 for poly in polys:
  if poly.is_empty or poly.geom_type!='Polygon':continue
  rr=[densify(list(poly.exterior.coords))]+[densify(list(r.coords)) for r in poly.interiors]
  areas[0]+=abs(g.polygon_area_perimeter(*zip(*rr[0]))[0])-sum(abs(g.polygon_area_perimeter(*zip(*r))[0]) for r in rr[1:])
  prr=[]
  for pr in projs:
   projected=[[[x/1000,-y/1000] for x,y in zip(*pr(*zip(*r)))] for r in rr];prr.append(projected)
  for j in range(2):areas[j+1]+=Polygon(prr[j][0],prr[j][1:]).area*1e6
  rings.extend([{'merc':a,'equal':b} for a,b in zip(*prr)])
 if areas[0]>0:
  errors.append(abs(areas[2]/areas[0]-1));out.append({'name':name,'continent':cont,'rings':rings,'areas':[x/1e6 for x in areas]})
  tot[cont]=[a+b/1e6 for a,b in zip(tot[cont],areas)]
assert max(errors)<.001
# These areas describe the clipped, generalized source geometry, not official land-area statistics.
data={'features':out,'continents':dict(tot),'extent':[-180,-60,180,85],'source_sha256':hashlib.sha256((p/'source/countries.geojson').read_bytes()).hexdigest()};(p/'world.js').write_text('const W='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
green=next(f for f in out if f['name']=='Greenland')['areas'];af=tot['Africa'];qa={'features':len(out),'max_equal_area_relative_error':max(errors),'africa_km2':af,'greenland_km2':green,'africa_greenland_ratios':[a/b for a,b in zip(af,green)],'sha256':data['source_sha256'],'assertions':'Equal Earth area error <0.1% each source feature; same geometry and clipped latitude extent for both projections'};(p/'evidence/qa.json').write_text(json.dumps(qa,indent=2));print(qa)
