import random
from math import sqrt
from pathlib import Path

from PIL import Image, ImageDraw

# Taken from https://lospec.com/palette-list/lost-century
COLOR_CHOICES = [
    "#8caba1",
    "#b3a555",
    "#ae5d40",
    "#4b726e",
    "#c77b58",
    "#79444a",
    "#d1b187",
    "#77743b",
    "#847875",
    "#927441",
    "#d2c9a5",
]

OUTLINE_COLOR = "#4b3d44"
SHAPES = ["circle", "diamond", "ellipse"]


def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def euclidean_distance(x1, y1, x2, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def elliptical_distance_x(x1, y1, x2, y2):
    dist = ((x1 - x2) / x2) ** 2 + ((y1 - y2) / (y2 / 2)) ** 2
    return dist * x2 * 2


def elliptical_distance_y(x1, y1, x2, y2):
    dist = ((x1 - x2) / (x2 / 2)) ** 2 + ((y1 - y2) / y2) ** 2
    return dist * x2 * 2


def pick_colors(main_color=None):
    if main_color is None:
        main_color = random.choice(COLOR_CHOICES)
    secondary_color = random.choice(COLOR_CHOICES)
    while secondary_color == main_color:
        secondary_color = random.choice(COLOR_CHOICES)
    tertiary_color = random.choice(COLOR_CHOICES)
    while tertiary_color == main_color or tertiary_color == secondary_color:
        tertiary_color = random.choice(COLOR_CHOICES)

    return [main_color] * 4 + [secondary_color] * 2 + [tertiary_color]


class Generator:
    def __init__(self, grid_size=20, cell_size=32) -> None:
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.center = grid_size / 2

    def _fill_likelihood(self, x, y, shape="circle"):
        dist_measure = euclidean_distance
        if shape == "diamond":
            dist_measure = manhattan_distance
        elif shape == "ellipse":
            dist_measure = random.choice([elliptical_distance_x, elliptical_distance_y])

        dist = dist_measure(x, y, self.center, self.center)
        if shape in ["circle", "diamond"]:
            if dist > self.grid_size // 2 + 1:
                return False
        fill_probability = 1 - (dist / self.grid_size)
        return random.random() < fill_probability

    def generate_avatar(self, shape=None, main_color=None):
        size = (self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        if shape is None:
            shape = random.choice(SHAPES)

        propability_grid = [
            [self._fill_likelihood(x, y, shape) for x in range(self.grid_size // 2)]
            for y in range(self.grid_size)
        ]

        filled_cells = self._draw_pixels(propability_grid, draw, main_color)
        self._draw_outline(filled_cells, draw)

        return img

    def _draw_pixels(self, grid, draw, main_color=None):
        colors = pick_colors(main_color)
        filled_cells = []

        for y in range(self.grid_size):
            for x in range(self.grid_size // 2):
                if grid[y][x]:
                    color = random.choice(colors)
                    top_left = (x * self.cell_size, y * self.cell_size)
                    bottom_right = ((x + 1) * self.cell_size, (y + 1) * self.cell_size)
                    draw.rectangle([top_left, bottom_right], fill=color)
                    filled_cells.append((x, y))

                    # Mirror horizontally
                    mirrored_x = self.grid_size - 1 - x
                    top_left_mirrored = (
                        mirrored_x * self.cell_size,
                        y * self.cell_size,
                    )
                    bottom_right_mirrored = (
                        (mirrored_x + 1) * self.cell_size,
                        (y + 1) * self.cell_size,
                    )
                    draw.rectangle(
                        [top_left_mirrored, bottom_right_mirrored], fill=color
                    )
                    filled_cells.append((mirrored_x, y))

        return filled_cells

    def _draw_outline(self, filled_cells, draw):
        for x, y in filled_cells:
            if (x - 1, y) not in filled_cells:
                outline_rect = [
                    ((x - 1) * self.cell_size, y * self.cell_size),
                    (x * self.cell_size, (y + 1) * self.cell_size),
                ]
                draw.rectangle(outline_rect, fill=OUTLINE_COLOR)

            if (x + 1, y) not in filled_cells:
                outline_rect = [
                    ((x + 1) * self.cell_size, y * self.cell_size),
                    ((x + 2) * self.cell_size, (y + 1) * self.cell_size),
                ]
                draw.rectangle(outline_rect, fill=OUTLINE_COLOR)

            if (x, y - 1) not in filled_cells:
                outline_rect = [
                    (x * self.cell_size, (y - 1) * self.cell_size),
                    ((x + 1) * self.cell_size, y * self.cell_size),
                ]
                draw.rectangle(outline_rect, fill=OUTLINE_COLOR)

            if (x, y + 1) not in filled_cells:
                outline_rect = [
                    (x * self.cell_size, (y + 1) * self.cell_size),
                    ((x + 1) * self.cell_size, (y + 2) * self.cell_size),
                ]
                draw.rectangle(outline_rect, fill=OUTLINE_COLOR)


if __name__ == "__main__":
    generator = Generator(grid_size=15, cell_size=16)

    for group_idx, main_color in enumerate(COLOR_CHOICES):
        shape = random.choice(SHAPES)
        group_path = Path(f"creatures/{group_idx:02}")
        group_path.mkdir(exist_ok=True)
        for creature_idx in range(50):
            avatar = generator.generate_avatar(shape, main_color)
            avatar.save(group_path / f"creature_{creature_idx:02}.png")
