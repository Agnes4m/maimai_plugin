import base64
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from .tool import STATIC

path = STATIC + "/high_eq_image.png"
fontpath = STATIC + "/msyh.ttc"


def draw_text(img_pil, text, offset_x):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(fontpath, 48)
    left, top, right, bottom = draw.textbbox((0, 0), text, font)
    width, height = right - left, bottom - top
    x = 5
    if width > 390:
        font = ImageFont.truetype(fontpath, int(390 * 48 / width))
        left, top, right, bottom = draw.textbbox((0, 0), text, font)
        width, height = right - left, bottom - top
    else:
        x = int((400 - width) / 2)
    draw.rectangle(
        (x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2),
        fill=(0, 0, 0, 255),
    )
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 255))


def text_to_image(text):
    font = ImageFont.truetype(fontpath, 24)
    padding = 10
    margin = 4
    text_list = text.split("\n")
    max_width = 0
    h = 0
    for text in text_list:
        left, top, right, bottom = font.getbbox(text)
        w, h = right - left, bottom - top
        max_width = max(max_width, w)
    wa = int(max_width + padding * 2)
    ha = int(h * len(text_list) + margin * (len(text_list) - 1) + padding * 2)
    i = Image.new("RGB", (wa, ha), color=(255, 255, 255))
    draw = ImageDraw.Draw(i)
    for j in range(len(text_list)):
        text = text_list[j]
        draw.text((padding, padding + j * (margin + h)), text, font=font, fill=(0, 0, 0))
    return i


def image_to_base64(img, format="PNG"):  # noqa: A002
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    return base64.b64encode(byte_data)
