def invert_color(color):
    """
    Invert a color by creating the new color as (255 - r, 255 - g, 255 - b)

    :param color: color to invert
    :type color: (int,int,int)
    :rtype: (int,int,int)
    """
    return (255 - color[0], 255 - color[1], 255 - color[2])

