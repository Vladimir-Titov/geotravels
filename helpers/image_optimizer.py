import pyvips


class InvalidImageError(Exception):
    pass


def optimaze_image(raw_image: bytes, quality: int = 80) -> bytes:
    try:
        image = pyvips.Image.new_from_buffer(raw_image, '', access='sequential')

        image = image.autorot()
        width = image.width
        height = image.height

        max_side = max(width, height)
        if max_side > 1600:
            scale = 1600 / max_side
            image = image.resize(scale)

        return image.write_to_buffer(
            '.webp',
            Q=quality,
            strip=True,
        )
    except pyvips.Error as e:
        raise InvalidImageError from e
