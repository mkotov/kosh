from PIL import Image, ImageDraw
from scipy.ndimage import geometric_transform
from pylab import subplot, imshow, show
import math
import cmath

def compose(f, g):
    return (f[0] * g[0] + f[1] * g[2], f[0] * g[1] + f[1] * g[3], f[2] * g[0] + f[3] * g[2], f[2] * g[1] + f[3] * g[3])

def invert(f):
    return (f[3], -f[1], -f[2], f[0])

def apply(f, z):
    try:
        return (f[0] * z + f[1]) / (f[2] * z + f[3])
    except:
        return 0

result_image_size = 300
init_image = Image.open("kosh_2.png")
init_image_size = init_image.size[0]

result_image_scale = 2.0

def result_image_to_plane(x, y):
    return complex(result_image_scale * (x - result_image_size / 2) / result_image_size, 
            result_image_scale * (result_image_size / 2 - y) / result_image_size)

def plane_to_init_image(z):
    z *= 1.2
    z = z + (0.5 + 0.5j)
    x = z.real * init_image_size
    y = init_image_size - z.imag * init_image_size
    return x, y

def image_transform_(f_inverted, point):
    z = result_image_to_plane(point[1], point[0])
    z = apply(f_inverted, z)
    x, y = plane_to_init_image(z)
    return y, x, point[2]

def image_transform(f): 
    return lambda point: image_transform_(f, point)


def iterate_transforms_(ts, ts_inv, i, is_inv, n):
    if n == 1:
        if is_inv:
            return [ts_inv[i]]
        return [ts[i]]
    ss = []
    for j in range(len(ts)):
        if i != j or is_inv:  
            ss += iterate_transforms_(ts, ts_inv, j, True, n - 1)
        if i != j or not is_inv:
            ss += iterate_transforms_(ts, ts_inv, j, False, n - 1)
    result = []
    for t in ss:
        if is_inv:
            result.append(compose(ts_inv[i], t))
        else:
            result.append(compose(ts[i], t))
    return result

def iterate_transforms(ts, n):
    if n == 0:
        return [(1, 0, 0, 1)]
    result = iterate_transforms(ts, n - 1)
    ts_inv = [invert(t) for t in ts]
    for i in range(len(ts)):
        result += iterate_transforms_(ts, ts_inv, i, True, n)
        result += iterate_transforms_(ts, ts_inv, i, False, n)
    return result

def scale(s):
    return (s, 0, 0, 1)

def rotate(a):
    return (cmath.exp(1j * a), 0, 0, 1)

def shift(v):
    return (1, v, 0, 1)

x = math.sqrt(2)
u = math.sqrt(2)
a = (x, 1, 1, x)
b = (u, 1j, -1j, u) 

nit = 10

def c(k, i):
    q = (x + 1)**(1.0 * i / k)
    w = (x - 1)**(1.0 * i / k)
    t = (q + w) / 2.0
    s = (q - w) / 2.0
    return (t, s, s, t)

def d(k, i):
    q = (u + 1)**(1.0 * i / k)
    w = (u - 1)**(1.0 * i / k)
    t = (q + w) / 2.0
    s = (q - w) / 2.0
    return (t, 1j * s, -1j*s, t)

transforms = iterate_transforms([a, b], 3)

for i in range(nit):
    result_image = Image.new("RGBA", (result_image_size, result_image_size), color=(127, 0, 255))
    for f in transforms:
        f_ = invert(compose(f, c(nit, i)))
        transformed_image = Image.fromarray(
                geometric_transform(init_image, image_transform(f_), output_shape=(result_image_size, result_image_size, 4), order=1)) 
        result_image.paste(transformed_image, (0, 0), transformed_image)
    result_image.show()
    result_image.save(str(i) + ".png")

