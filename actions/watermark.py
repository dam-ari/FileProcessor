import os
import logging
import json
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from file_utils import get_metadata, get_files_to_process
from datetime import datetime
from config import (
    DEFAULT_WATERMARK_SIZE,
    DEFAULT_WATERMARK_TRANSPARENCY,
    DEFAULT_FONT_SIZE,
    DEFAULT_SOFT_EDGE,
    DEFAULT_INCLUDE_DATE,
    DEFAULT_WATERMARK_POSITION
)

def apply_watermark_to_files(directory, watermark, text=None, include_date=DEFAULT_INCLUDE_DATE, image_position=DEFAULT_WATERMARK_POSITION, text_position=DEFAULT_WATERMARK_POSITION, size=DEFAULT_WATERMARK_SIZE, transparency=DEFAULT_WATERMARK_TRANSPARENCY, soft_edge=DEFAULT_SOFT_EDGE, font_size=DEFAULT_FONT_SIZE, font="", include_subdirectories=True):
    files_to_process = get_files_to_process(directory, include_subdirectories)
    if not files_to_process:
        logging.error(f"No files found to process in directory: {directory}")
        return False, False

    return apply_watermark(files_to_process, watermark, text, include_date, image_position, text_position, size, transparency, soft_edge, font_size, font)

def apply_watermark(files, watermark, text=None, include_date=False, image_position="bottom_center", text_position="bottom_center", size=10, transparency=128, soft_edge=True, font_size=20, font=""):
    success = True
    partial_success = False
    for file in files:
        try:
            if file.endswith('.pdf'):
                apply_pdf_watermark(file, watermark, text, include_date, image_position, text_position, size, font_size, font)
            elif file.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                apply_image_watermark(file, watermark, text, include_date, image_position, text_position, size, transparency, soft_edge, font_size, font)
            else:
                logging.info(f"Skipping unsupported file type: {file}")
        except Exception as e:
            partial_success = True
            metadata = get_metadata(file)
            logging.error(f"Error applying watermark to {file}: {str(e)}, Metadata: {json.dumps(metadata)}")
            success = False
    return success, partial_success

def apply_image_watermark(input_image, watermark, text, include_date, image_position, text_position, size, transparency, soft_edge, font_size, font):
    output_image = os.path.join(os.path.dirname(input_image), f"watermarked_{os.path.basename(input_image)}")
    try:
        base_image = Image.open(input_image).convert("RGBA")

        # Create a transparent layer the size of the base image
        txt = Image.new('RGBA', base_image.size, (255, 255, 255, 0))

        if watermark:
            watermark = watermark.strip()  # Trim any leading or trailing spaces
            watermark_image = Image.open(watermark).convert("RGBA")

            # Scale the watermark to fit the base image if necessary
            watermark_size = (base_image.width * size // 100, base_image.height * size // 100)
            watermark_image.thumbnail(watermark_size)

            # Apply transparency to the watermark
            watermark_image = adjust_transparency(watermark_image, transparency)

            # Apply soft edges to the watermark
            if soft_edge:
                watermark_image = apply_soft_edges(watermark_image)

            watermark_position = get_watermark_position(base_image.size, watermark_image.size, image_position)
            txt.paste(watermark_image, watermark_position, watermark_image)

        if text or include_date:
            draw = ImageDraw.Draw(txt)
            if font:
                font = ImageFont.truetype(font, font_size)
            else:
                font = ImageFont.truetype("arial.ttf", font_size)  # Use a default truetype font
            text_position = get_text_position(base_image.size, text_position)
            text_content = text if text else ""
            if include_date:
                date_str = datetime.now().strftime("%Y-%m-%d")
                text_content += f" {date_str}"
            draw.text(text_position, text_content, font=font, fill=(255, 255, 255, 128))  # White text with transparency

        # Combine the base image with the text/watermark layer
        watermarked_image = Image.alpha_composite(base_image, txt)
        
        if input_image.lower().endswith('.jpg') or input_image.lower().endswith('.jpeg'):
            watermarked_image = watermarked_image.convert("RGB")
        
        watermarked_image.save(output_image)
        logging.info(f"Watermark applied to image file: {input_image}, saved as {output_image}")
    except Exception as e:
        metadata = get_metadata(input_image)
        logging.error(f"Error applying image watermark to {input_image}: {str(e)}, Metadata: {json.dumps(metadata)}")
        raise

def adjust_transparency(image, transparency):
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 255.0)
    image.putalpha(alpha)
    return image

def apply_soft_edges(image):
    width, height = image.size
    alpha = image.split()[3]

    new_alpha = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(new_alpha)
    for i in range(width):
        for j in range(height):
            distance = min(i, j, width - i, height - j)
            new_alpha.putpixel((i, j), max(0, min(255, distance * 5)))

    alpha = ImageEnhance.Brightness(new_alpha).enhance(1.0)
    image.putalpha(alpha)
    return image

def get_watermark_position(base_size, watermark_size, position):
    if position == "top_left":
        return (0, 0)
    elif position == "top_center":
        return ((base_size[0] - watermark_size[0]) // 2, 0)
    elif position == "top_right":
        return (base_size[0] - watermark_size[0], 0)
    elif position == "middle_left":
        return (0, (base_size[1] - watermark_size[1]) // 2)
    elif position == "middle_center":
        return ((base_size[0] - watermark_size[0]) // 2, (base_size[1] - watermark_size[1]) // 2)
    elif position == "middle_right":
        return (base_size[0] - watermark_size[0], (base_size[1] - watermark_size[1]) // 2)
    elif position == "bottom_left":
        return (0, base_size[1] - watermark_size[1])
    elif position == "bottom_center":
        return ((base_size[0] - watermark_size[0]) // 2, base_size[1] - watermark_size[1])
    elif position == "bottom_right":
        return (base_size[0] - watermark_size[0], base_size[1] - watermark_size[1])
    else:
        return (0, base_size[1] - watermark_size[1])

def get_text_position(base_size, position):
    if position in ["top_left", "middle_left", "bottom_left"]:
        return (10, base_size[1] - 50)
    elif position in ["top_center", "middle_center", "bottom_center"]:
        return ((base_size[0] // 2) - 50, base_size[1] - 50)
    elif position in ["top_right", "middle_right", "bottom_right"]:
        return (base_size[0] - 100, base_size[1] - 50)
    else:
        return (10, base_size[1] - 50)
