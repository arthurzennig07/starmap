import numpy as np
import cv2
from skyfield import api, almanac
from PIL import ImageDraw, Image, ImageFilter

def crop_center(pil_img,x,y, crop_width, crop_height):
    img_width, img_height = pil_img.size
    left = int(x - 0.5*crop_width)
    upper = int(y - 0.5*crop_height)
    right = int(x + 0.5*crop_width)
    bottom = int(y + 0.5*crop_height)
    left = img_width if (left > img_width) else left
    left = 0 if (left < 0) else left
    upper = img_height if (upper > img_height) else upper
    upper = 0 if (upper < 0 ) else upper
    right = 0 if right < 0 else right
    right = img_width if right > img_width else right
    bottom = 0 if bottom < 0 else bottom
    bottom = img_height if bottom > img_height else bottom

    return pil_img.crop((left, upper, right, bottom))


def mask_circle_solid(pil_img, offset=0):
    background = Image.new(pil_img.mode, pil_img.size)

    offset = 0
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    result = pil_img.copy()
    result.putalpha(mask)
    return result

'''
retorna right ascension (em horas) e longitude from skymap that is right above the observers head.
https://rhodesmill.org/skyfield/examples.html#when-is-a-body-or-fixed-coordinate-above-the-horizon
'''
def get_ra_dec_above_observer(year,month,day,hour,min,lat,lon):
    ts = api.load.timescale()
    t = ts.utc(year=year, month=month, day=day, hour=hour, minute=min)
    geographic = api.wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon)
    observer = geographic.at(t)
    pos = observer.from_altaz(alt_degrees=90, az_degrees=0)
    ra, dec, distance = pos.radec()
    return ra, dec

'''
converte horas em valor entre 0-100.
'''
def convert_radec_to_centesimal(ra,dec,image_width,image_height):
    y = round(((image_height/2) * dec)/90,0) # 90 graus
    if(y < 0):
        #longitude, valor angulo 0 é no centro da imagem. polo sul é negativo, polo norte positivo.
        y += image_height/2 + abs(y)
    x = round((image_width * (24 - ra))/24,0) #24 horas
    # print('y:{}, x:{}'.format(y,x))
    return x,y


def main():
    print("hello")
    eph = api.load('de421.bsp')
    img = Image.open("./Resources/Original_Images/starmap.png")
    w,h = img.size
    ra,dec = get_ra_dec_above_observer(2021,8,20,20,10, -41.00106,-20.37511)
    print('ra:{}, dec:{}'.format(ra,dec))
    ra_float = float('{:.8f}'.format(ra.hours))
    dec_float = float('{:+.8f}'.format(dec.degrees))
    print('ra:{}, dec:{}'.format(ra_float, dec_float))
    ts = api.load.timescale()
    skytime = ts.utc(2021,8,20,20,10)
    moon_phase = almanac.moon_phase(eph,skytime)
    print("moonphase: {}".format(moon_phase.degrees))
    sky_x, sky_y = convert_radec_to_centesimal(ra_float,dec_float,w,h)
    im_square = crop_center(img, sky_x, sky_y, 700, 700)
    im_thumb = mask_circle_solid(im_square)
    im_thumb.show()
    # im_square.show()

if __name__ == '__main__':
    main()