from pathlib import Path
import json,hashlib,math
from shapely.geometry import shape,box,Polygon
from shapely.ops import unary_union
from pyproj import Proj,Geod,__version__
p=Path(__file__).resolve().parents[1];g=Geod(ellps='WGS84');raw=json.loads((p/'source/land.geojson').read_text());land=unary_union([shape(f['geometry']) for f in raw['features']]).intersection(box(25,-15,180,75));polys=list(land.geoms) if hasattr(land,'geoms') else [land]
def ringpoly(poly):return [list(poly.exterior.coords)]+[list(x.coords) for x in poly.interiors]
rings=[r for poly in polys if poly.geom_type=='Polygon' for r in ringpoly(poly)]
configs=[('merc','麥卡托','局部角度保形；高緯度面積放大','+proj=merc +lon_0=110 +ellps=WGS84 +units=m'),('laea','蘭伯特方位等積','保留面積；形狀與距離仍會改變','+proj=laea +lon_0=121.5654 +lat_0=25.033 +ellps=WGS84 +units=m'),('aeqd','臺北中心方位等距','只保留由臺北出發的距離與方位','+proj=aeqd +lon_0=121.5654 +lat_0=25.033 +ellps=WGS84 +units=m')]
cities=[('臺北',121.5654,25.033),('新加坡',103.8198,1.3521),('東京',139.6917,35.6895),('札幌',141.3545,43.0618),('烏蘭巴托',106.9057,47.8864),('雅庫茨克',129.7326,62.0355),('新德里',77.209,28.6139),('雅加達',106.8456,-6.2088)]
grid=[]
for lon in range(30,181,15):grid.append([(lon,-15+i*.5) for i in range(181)])
for lat in range(-15,76,15):grid.append([(25+i*.5,lat) for i in range(311)])
result=[];checks=[]
for key,title,desc,spec in configs:
 pr=Proj(spec)
 def xy(lon,lat):x,y=pr(lon,lat);assert math.isfinite(x+y);return [round(x/1000,4),round(-y/1000,4)]
 outlines=[[xy(*v) for v in r] for r in rings];allpts=[v for r in outlines for v in r];bounds=[min(v[0] for v in allpts),min(v[1] for v in allpts),max(v[0] for v in allpts),max(v[1] for v in allpts)];items=[]
 for name,lon,lat in cities:
  # WGS84 geodesic circle; finite 500km circle, not infinitesimal Tissot ellipse.
  ring=[g.fwd(lon,lat,az,500000)[:2] for az in range(0,361,2)];circle=[xy(*v) for v in ring];area=abs(g.polygon_area_perimeter(*zip(*ring))[0])/1e6;ratio=Polygon(circle).area/area
  fac=pr.get_factors(lon,lat);tx,ty=xy(cities[0][1],cities[0][2]);cx,cy=xy(lon,lat);ground=g.inv(cities[0][1],cities[0][2],lon,lat)[2]/1000;plane=math.hypot(cx-tx,cy-ty)
  items.append({'name':name,'lon':lon,'lat':lat,'point':[cx,cy],'circle':circle,'circle_area_ratio':ratio,'local_area_scale':fac.areal_scale,'angular_distortion':fac.angular_distortion,'ground_km':ground,'plane_km':plane,'distance_error_percent':(plane/ground-1)*100 if ground else None})
  if key=='laea':assert abs(ratio-1)<.0001
  if key=='aeqd' and ground:assert abs(plane/ground-1)<1e-6
 result.append({'id':key,'title':title,'description':desc,'proj':spec,'land':outlines,'grid':[[xy(*v) for v in r] for r in grid],'bounds':bounds,'places':items})
span=max(max(r['bounds'][2]-r['bounds'][0],r['bounds'][3]-r['bounds'][1]) for r in result)*1.07
out={'maps':result,'span_km':span,'radius_km':500,'extent':[25,-15,180,75]};(p/'data.js').write_text('const D='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';');(p/'evidence/qa.json').write_text(json.dumps({'pyproj':__version__,'source_sha256':hashlib.sha256((p/'source/land.geojson').read_bytes()).hexdigest(),'polygons':len(polys),'tests':'LAEA finite-circle area error <0.01%; AEQD Taipei distance error <0.0001%; all coordinates finite','values':[{k:v for k,v in m.items() if k in ['id','proj','places']} for m in result]},ensure_ascii=False,indent=2));print('PASS',len(polys),'polygons',span,'km')
