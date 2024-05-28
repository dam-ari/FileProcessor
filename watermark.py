import os
import logging
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import PyPDF2
from file_utils import get_metadata, get_files_to_process
from datetime import datetime

def apply_watermark_to_files(directory, watermark, text=None, include_date=False, image_position="bottom_center", text_position="bottom_center", size=10, transparency=128, soft_edge=True):
    files_to_process = get_files_to_process(directory)
    if not files_to_process:
        logging.error(f"No files found to process in directory: {directory}")
        return False, False

    return apply_watermark(files_to_process, watermark, text, include_date, image_position, text_position, size, transparency, soft_edge)

def apply_watermark(files, watermark, text=None, include_date=False, image_position="bottom_center", text_position="bottom_center", size=10, transparency=100, soft_edge=True):
    success = True
    partial_success = False
    logging.debug(f"Applying watermark: {watermark}, text: {text}, date: {include_date}, image position: {image_position}, text position: {text_position}, size: {size}%, transparency: {transparency}, soft edge: {soft_edge}")
    for file in files:
        logging.debug(f"Processing file: {file}")
        try:
            if file.endswith('.pdf'):
                apply_pdf_watermark(file, watermark, text, include_date, image_position, text_position, size)
            elif file.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                apply_image_watermark(file, watermark, text, include_date, image_position, text_position, size, transparency, soft_edge)
            else:
                logging.info(f"Skipping unsupported file type: {file}")
        except Exception as e:
            partial_success = True
            metadata = get_metadata(file)
            logging.error(f"Error applying watermark to {file}: {str(e)}, Metadata: {json.dumps(metadata)}")
            success = False
    return success, partial_success

def apply_pdf_watermark(input_pdf, watermark, text, include_date, image_position, text_position, size):
    output_pdf = os.path.join(os.path.dirname(input_pdf), f"watermarked_{os.path.basename(input_pdf)}")
    try:
        pdf_reader = PyPDF2.PdfFileReader(input_pdf)
        pdf_writer = PyPDF2.PdfFileWriter()
        watermark_obj = PyPDF2.PdfFileReader(watermark)

        for i in range(pdf_reader.numPages):
            page = pdf_reader.getPage(i)
            page.merge_page(watermark_obj.getPage(0))
            pdf_writer.addPage(page)

        with open(output_pdf, 'wb') as out_file:
            pdf_writer.write(out_file)
        logging.info(f"Watermark applied to PDF file: {input_pdf}, saved as {output_pdf}")
    except Exception as e:
        metadata = get_metadata(input_pdf)
        logging.error(f"Error applying PDF watermark to {input_pdf}: {str(e)}, Metadata: {json.dumps(metadata)}")
        raise

def apply_image_watermark(input_image, watermark, text, include_date, image_position, text_position, size, transparency, soft_edge):
    output_image = os.path.join(os.path.dirname(input_image), f"watermarked_{os.path.basename(input_image)}")
    try:
        logging.debug(f"Opening base image: {input_image}")
        base_image = Image.open(input_image).convert("RGBA")

        # Create a transparent layer the size of the base image
        txt = Image.new('RGBA', base_image.size, (255, 255, 255, 0))

        if watermark:
            logging.debug(f"Opening watermark image: {watermark}")
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
            logging.debug(f"Adding text watermark: {text}")
            draw = ImageDraw.Draw(txt)
            font = ImageFont.load_default()
            text_position = get_text_position(base_image.size, text_position)
            text_content = text if text else ""
            if include_date:
                date_str = datetime.now().strftime("%Y-%m-%d")
                text_content += f" {date_str}"
            draw.text(text_position, text_content, font=font, fill=(255, 255, 255, 128))  # White text with transparency

        # Combine the base image with the text/watermark layer
        watermarked_image = Image.alpha_composite(base_image, txt)
        watermarked_image.save(output_image)
        logging.info(f"Watermark applied to image file: {input_image}, saved as {output_image}")
    except Exception as e:
        metadata = get_metadata(input_image)
        logging.error(f"Error applying image watermark to {input_image}: {str(e)}, Metadata: {json.dumps(metadata)}")
        raise

def adjust_transparency(image, transparency):
    # Adjust the transparency of the watermark image
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 255.0)
    image.putalpha(alpha)
    return image

def apply_soft_edges(image):
    width, height = image.size
    alpha = image.split()[3]

    # Create a new alpha channel with the soft edges
    new_alpha = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(new_alpha)
    for i in range(width):
        for j in range(height):
            distance = min(i, j, width - i, height - j)
            new_alpha.putpixel((i, j), max(0, min(255, distance * 5)))

    # Combine the original alpha with the new alpha channel
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
