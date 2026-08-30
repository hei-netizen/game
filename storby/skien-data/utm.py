import math
# GRS80 / WGS84 forward transverse Mercator -> UTM33N (EPSG:25833)
a=6378137.0; f=1/298.257222101; e2=f*(2-f); k0=0.9996; lon0=math.radians(15.0)
FE=500000.0; FN=0.0
def ll2utm33(lat,lon):
    lat=math.radians(lat); lon=math.radians(lon)
    ep2=e2/(1-e2)
    N=a/math.sqrt(1-e2*math.sin(lat)**2)
    T=math.tan(lat)**2
    C=ep2*math.cos(lat)**2
    A=(lon-lon0)*math.cos(lat)
    M=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*lat
        -(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*lat)
        +(15*e2**2/256+45*e2**3/1024)*math.sin(4*lat)
        -(35*e2**3/3072)*math.sin(6*lat))
    E=FE+k0*N*(A+(1-T+C)*A**3/6+(5-18*T+T*T+72*C-58*ep2)*A**5/120)
    Nn=FN+k0*(M+N*math.tan(lat)*(A*A/2+(5-T+9*C+4*C*C)*A**4/24
        +(61-58*T+T*T+600*C-330*ep2)*A**6/720))
    return E,Nn
if __name__=="__main__":
    for lat,lon in [(59.2085,9.6090),(59.19952,9.58268),(59.21748,9.63532)]:
        print(f"{lat},{lon} -> {ll2utm33(lat,lon)}")

def utm332ll(E,N):
    ep2=e2/(1-e2); e1=(1-math.sqrt(1-e2))/(1+math.sqrt(1-e2))
    M=(N-FN)/k0
    mu=M/(a*(1-e2/4-3*e2**2/64-5*e2**3/256))
    phi1=(mu+(3*e1/2-27*e1**3/32)*math.sin(2*mu)+(21*e1**2/16-55*e1**4/32)*math.sin(4*mu)
          +(151*e1**3/96)*math.sin(6*mu)+(1097*e1**4/512)*math.sin(8*mu))
    C1=ep2*math.cos(phi1)**2; T1=math.tan(phi1)**2
    N1=a/math.sqrt(1-e2*math.sin(phi1)**2)
    R1=a*(1-e2)/(1-e2*math.sin(phi1)**2)**1.5
    D=(E-FE)/(N1*k0)
    lat=phi1-(N1*math.tan(phi1)/R1)*(D*D/2-(5+3*T1+10*C1-4*C1*C1-9*ep2)*D**4/24
        +(61+90*T1+298*C1+45*T1*T1-252*ep2-3*C1*C1)*D**6/720)
    lon=lon0+(D-(1+2*T1+C1)*D**3/6+(5-2*C1+28*T1-3*C1*C1+8*ep2+24*T1*T1)*D**5/120)/math.cos(phi1)
    return math.degrees(lat), math.degrees(lon)
