from PIL import Image, ImageOps


# TODO: change str to Path?
def convert_image(filename: str):
    image = Image.open(filename)

    # TODO: use ImageOps? or image.convert
    #
    # image_grayscale = ImageOps.grayscale(image)
    # image_grayscale.save(f'{filename}_grayscale.png')

    image_grayscale = image.convert("L")
    image_grayscale.save(f"{filename[:filename.rindex('.')]}_grayscale.png")


def main():
    convert_image("image.png")


if __name__ == "__main__":
    main()
