from PIL import Image, ImageSequence

def resize_image(input_path, output_path, new_size):
    """
    Resize an image.

    Parameters:
    - input_path: Path to the input image file.
    - output_path: Path to save the resized file.
    - new_size: Tuple containing the new width and height (width, height)
    """
    original_image = Image.open(input_path)
    resized_image = original_image.resize(new_size)
    
    resized_image.save(output_path)

def resize_gif(input_path, output_path, new_size):
    """
    Resize a GIF.

    Parameters:
    - input_path: Path to the input GIF file.
    - output_path: Path to save the resized GIF.
    - new_size: Tuple containing the new width and height (width, height)
    """
    original_gif = Image.open(input_path)

    resized_frames = []

    # Resize each frame and append to the list
    for frame in ImageSequence.Iterator(original_gif):
        resized_frame = frame.resize(new_size)
        resized_frames.append(resized_frame)

    # Save the resized GIF
    resized_gif = Image.new('RGB', new_size)
    resized_gif.info = original_gif.info

    resized_gif.save(
        output_path,
        save_all=True,
        append_images=resized_frames,
        disposal=1)

if __name__ == "__main__":
    resize_gif("test/test_input.gif", "test/test_output.gif", (32, 32))