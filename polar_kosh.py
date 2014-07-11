from PIL import Image, ImageDraw
from scipy.ndimage import geometric_transform
from pylab import subplot, imshow, show
import math
import cmath

back_image = Image.new("RGBA", (640, 480), color=(127, 0, 255))
init_image = Image.open("kosh_2.png")
init_image_pixels_per_unit = init_image.size[0]
init_image_width = init_image.size[0]
init_image_height = init_image.size[0]
result_image_pixels_per_unit = 150.0
result_image_width = back_image.size[0]
result_image_height = back_image.size[1]

phi_0 = math.pi / 4.0 
theta = (1 + 0.5 * phi_0) / (1 - 0.5 * phi_0)
nit = 24
k_0 = 1
delta_k = pow(theta, 1.0 / nit) * cmath.exp(complex(0, phi_0 / nit))
k = k_0

def result_image_to_plane(x, y):
    return complex(
            (x - result_image_width / 2) / result_image_pixels_per_unit,
            (result_image_height / 2 - y) / result_image_pixels_per_unit)

def polar_grid_to_init_image(z):
    if z == 0:
        return 0, 0
    r = abs(z)
    a = cmath.phase(z)
    n = math.floor(math.log(r) / math.log(theta))
    m = math.floor(a / phi_0)
    t_n = pow(theta, n)
    x = (r - t_n) / (t_n * theta - t_n) * init_image_pixels_per_unit
    y = init_image_height - (a - phi_0 * m) / phi_0 * init_image_pixels_per_unit
    return y, x

# r(z) = (z - 1) / (z + 1)
def r_inverted(z):
    if z == 1:
        return 0 # infty 
    return (1 + z) / (1 - z)

# t(z) = kz
def t_inverted(z):
    return z / k

def image_transform(point):
    z = result_image_to_plane(point[1], point[0])
    z = r_inverted(z)
    z = t_inverted(z)
    x, y = polar_grid_to_init_image(z)
    return y, x, point[2]

for i in range(0, nit):
    transformed_image = Image.fromarray(
            geometric_transform(init_image, image_transform, output_shape=(result_image_height, result_image_width, 4), order=1)) 
    result_image = Image.new("RGBA", back_image.size)
    result_image.paste(back_image, (0, 0))
    result_image.paste(transformed_image, (0, 0), transformed_image)
    result_image.save(str(i) + ".png")
    k *= delta_k

