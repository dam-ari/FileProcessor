import os
import logging
from PIL import Image
from PyPDF2 import PdfMerger
from file_utils import get_files_to_process


def merge_files(directory, matrix="1,1", fill_method="stretch", include_subdirectories=True):
    
    try:
        files_to_process = get_files_to_process(directory, include_subdirectories)
        pdfs = sorted([file for file in files_to_process if file.lower().endswith('.pdf')])
        images = sorted([file for file in files_to_process if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

        if pdfs:
            merge_pdfs(pdfs, directory)
        if images:
            merge_images(images, directory, matrix, fill_method)
        
        return True, False
    except Exception as e:
        logging.error(f"Error merging files: {str(e)}")
        return False, True

def merge_pdfs(pdfs, output_directory):
    try:
        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        output_pdf = os.path.join(output_directory, "merged_file.pdf")
        merger.write(output_pdf)
        merger.close()
        logging.info(f"Merged PDF saved as {output_pdf}")
    except Exception as e:
        logging.error(f"Error merging PDFs: {str(e)}")
        raise

def merge_images(images, output_directory, matrix, fill_method):
    try:
        rows, cols = map(int, matrix.split(','))
        num_images = len(images)

        # Get the maximum width and height of the images
        max_width = max(Image.open(image).width for image in images)
        max_height = max(Image.open(image).height for image in images)

        # Calculate the size of the new image
        new_width = max_width * cols
        new_height = max_height * rows

        new_im = Image.new('RGB', (new_width, new_height), (255, 255, 255))

        x_offset = 0
        y_offset = 0
        for index, image_path in enumerate(images):
            if index > 0 and index % cols == 0:
                x_offset = 0
                y_offset += max_height

            im = Image.open(image_path)
            new_im.paste(im, (x_offset, y_offset))
            x_offset += max_width

        # Handle the last row if the images don't fill the grid exactly
        remaining = num_images % cols
        if remaining != 0:
            gap_width = new_width - x_offset
            last_image = Image.open(images[-1])

            if fill_method == "stretch":
                stretched = last_image.resize((gap_width, max_height))
                new_im.paste(stretched, (x_offset, y_offset))
            elif fill_method == "repeat":
                for i in range(cols - remaining):
                    new_im.paste(last_image, (x_offset, y_offset))
                    x_offset += max_width
            elif fill_method == "leave":
                pass

        output_image = os.path.join(output_directory, "merged_image.jpg")
        new_im.save(output_image)
        logging.info(f"Merged image saved as {output_image}")
    except Exception as e:
        logging.error(f"Error merging images: {str(e)}")
        raise
