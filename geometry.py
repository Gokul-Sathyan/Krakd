from shapely.geometry import Point

def distance2D(P1, P2):
    return Point(P1.x(), P1.y()).distance(Point(P2.x, P2.y))


def convertToVirtual(scale, T, p):
    return (p[0]*scale + T[0], -p[1]*scale + T[1])

def convertToReal(scale, T, p):
    return ((p[0] - T[0])/scale, (-p[1] + T[1])/scale)