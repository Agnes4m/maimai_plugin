import base64
import httpx
from io import BytesIO
from .tool import STATIC
from PIL import ImageFont, ImageDraw, Image
from PIL.Image import Image as Image_tpye


path = STATIC + "/high_eq_image.png"
fontpath = STATIC + "/msyh.ttc"


def draw_text(img_pil, text, offset_x):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(fontpath, 48)
    width, height = draw.textsize(text, font)
    x = 5
    if width > 390:
        font = ImageFont.truetype(fontpath, int(390 * 48 / width))
        width, height = draw.textsize(text, font)
    else:
        x = int((400 - width) / 2)
    draw.rectangle(
        (x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2),
        fill=(0, 0, 0, 255),
    )
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 255))


def text_to_image(text: str):
    font = ImageFont.truetype(fontpath, 24)
    padding = 10
    margin = 4
    h = 0
    text_list = text.split("\n")
    max_width = 0
    for text in text_list:
        w, h = font.getsize(text)
        max_width = max(max_width, w)
    wa = max_width + padding * 2
    ha = h * len(text_list) + margin * (len(text_list) - 1) + padding * 2
    i = Image.new("RGB", (wa, ha), color=(255, 255, 255))
    draw = ImageDraw.Draw(i)
    for j in range(len(text_list)):
        text = text_list[j]
        draw.text(
            (padding, padding + j * (margin + h)),
            text,
            font=font,
            fill=(0, 0, 0),
        )
    return i


def image_to_base64(img: Image_tpye, format="PNG"):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


def url_to_base64(url: str):
    response = httpx.get(url)
    image_data = response.content
    base64_data = base64.b64encode(image_data)
    return base64_data


def url_to_bytes(url: str):
    return httpx.get(url).content