from PIL import Image, ImageDraw
from scipy.ndimage import geometric_transform
from pylab import subplot, imshow, show
import math
import cmath

back_image = Image.new("RGBA", (300, 300), color=(127, 0, 255))
init_image = Image.open("kosh_2.png")
init_image_pixels_per_unit = init_image.size[0]
init_image_width = init_image.size[0]
init_image_height = init_image.size[0]
result_image_pixels_per_unit = 100.0
result_image_width = back_image.size[0]
result_image_height = back_image.size[1]


def compose(f, g):
    return (f[0] * g[0] + f[1] * g[2], f[0] * g[1] + f[1] * g[3], f[2] * g[0] + f[3] * g[2], f[2] * g[1] + f[3] * g[3])

def invert(f):
    return (f[3], -f[1], -f[2], f[0])

def apply(f, z):
    try:
        return (f[0] * z + f[1]) / (f[2] * z + f[3])
    except:
        return 0 # infty

def result_image_to_plane(x, y):
    return complex(
            (x - result_image_width / 2) / result_image_pixels_per_unit,
            (result_image_height / 2 - y) / result_image_pixels_per_unit)

def plane_to_init_image(z):
    z = z + (0.5 + 0.5j)
    x = z.real * init_image_pixels_per_unit
    y = init_image_height - z.imag * init_image_pixels_per_unit
    return x, y

def image_transform_(f_inverted, point):
    z = result_image_to_plane(point[1], point[0])
    z = apply(f_inverted, z)
    x, y = plane_to_init_image(z)
    return y, x, point[2]

def image_transform(f): 
    return lambda point: image_transform_(f, point)

def iterate_transforms(ts, n):
    if n == 0:
        return [(1, 0, 0, 1)]
    result = []
    pts = iterate_transforms(ts, n - 1)
    result += pts
    for t in ts:
        for pt in pts:
            result.append(compose(t, pt))
    return result

def scale(s):
    return (s, 0, 0, 1)

def rotate(a):
    return (cmath.exp(1j * a), 0, 0, 1)

def shift(v):
    return (1, v, 0, 1)

nit = 10
for i in range(0, nit):
    transforms = []
    r = rotate(2 * math.pi / 3 * i / nit)
    t1 = compose(r, compose(shift(1j), compose(rotate(math.pi / 2), scale(0.6))))
    t2 = compose(r, compose(shift(math.sqrt(3) / 2 - 0.5j), compose(rotate(-math.pi / 6), scale(0.6))))
    t3 = compose(r, compose(shift(-math.sqrt(3) / 2 - 0.5j), compose(rotate(-math.pi * 5.0 / 6), scale(0.6))))
    transforms = iterate_transforms([t1, t2, t3], 3)

    result_image = Image.new("RGBA", back_image.size)
    result_image.paste(back_image, (0, 0))
    for f in transforms:
        transformed_image = Image.fromarray(
                geometric_transform(
                    init_image, 
                    image_transform(invert(f)), 
                    output_shape=(result_image_height, result_image_width, 4), 
                    order=1)) 
        result_image.paste(transformed_image, (0, 0), transformed_image)
    result_image.show()
    result_image.save(str(i) + ".png")
    print(i)





