import logging
import os
from PIL import Image
from file_utils import get_files_to_process

def merge_files(directory, rows=1, fill_method="stretch", **kwargs):
    try:
        files_to_process = get_files_to_process(directory)
        images = [Image.open(file) for file in files_to_process if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

        if not images:
            logging.error(f"No images found to merge in directory: {directory}")
            return False, False

        # Determine the number of columns based on the number of rows
        num_images = len(images)
        cols = (num_images + rows - 1) // rows

        # Get the maximum width and height of the images
        max_width = max(image.width for image in images)
        max_height = max(image.height for image in images)

        # Calculate the size of the new image
        new_width = max_width * cols
        new_height = max_height * rows

        new_im = Image.new('RGB', (new_width, new_height), (255, 255, 255))

        x_offset = 0
        y_offset = 0
        for index, im in enumerate(images):
            if index > 0 and index % cols == 0:
                x_offset = 0
                y_offset += max_height

            new_im.paste(im, (x_offset, y_offset))
            x_offset += max_width

        # Handle the last row if the images don't fill the grid exactly
        remaining = num_images % cols
        if remaining != 0:
            gap_width = new_width - x_offset
            last_image = images[-1]

            if fill_method == "stretch":
                stretched = last_image.resize((gap_width, max_height))
                new_im.paste(stretched, (x_offset, y_offset))
            elif fill_method == "repeat":
                for i in range(cols - remaining):
                    new_im.paste(last_image, (x_offset, y_offset))
                    x_offset += max_width
            elif fill_method == "leave":
                pass

        output_image = os.path.join(directory, "merged_image.jpg")
        new_im.save(output_image)
        logging.info(f"Merged image saved as {output_image}")
        return True, False
    except Exception as e:
        logging.error(f"Error merging files: {str(e)}")
        return False, True
