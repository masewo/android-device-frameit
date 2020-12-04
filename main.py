import os
import re
from PIL import Image
from pathlib import Path

android_home = os.getenv("ANDROID_HOME")


def main():
    devices = ['pixel_4_xl', 'pixel_c', 'nexus_7_2013']
    Path("input").mkdir(parents=True, exist_ok=True)
    Path("output").mkdir(parents=True, exist_ok=True)
    for device in devices:
        Path("output\\" + device).mkdir(parents=True, exist_ok=True)
        for entry in os.scandir('input'):
            if entry.path.endswith(".png") and entry.is_file():
                frame(device, entry.name)


def frame(device, path):
    layout = read_layout(device)
    display = re.compile(r"display {.*?width (\d{3,4}).*?height (\d{3,4})", re.DOTALL).search(layout)
    display_width = display.group(1)
    display_height = display.group(2)

    background = re.compile(r"landscape {.*?background {.*?image ([^\n]+)", re.DOTALL).search(layout)
    if background:
        landscape = True
        image = background.group(1)
    else:
        landscape = False
        background = re.compile(r"portrait {.*?background {.*?image ([^\n]+)", re.DOTALL).search(layout)
        image = background.group(1)

    foreground = re.compile(r"portrait {.*?foreground {.*?mask ([^\n]+)", re.DOTALL).search(layout)
    mask_path = ""
    if foreground:
        mask_path = foreground.group(1)

    if landscape:
        part2 = re.compile(r"layouts.*?landscape.*?name device.*?x (\d{1,4}).*?y (\d{1,4})", re.DOTALL).search(layout)
    else:
        part2 = re.compile(r"layouts.*?portrait.*?name device.*?x (\d{1,4}).*?y (\d{1,4})", re.DOTALL).search(layout)

    offset_x = int(part2.group(1))
    offset_y = int(part2.group(2))

    back = Image.open(os.path.join(android_home, "skins", device, image))
    back_size = back.size

    screenshot = Image.open('input\\' + path)
    screenshot_size = screenshot.size

    if landscape:
        if str(screenshot_size[0]) != display_height or str(screenshot_size[1]) != display_width:
            # does NOT have the right device resolution
            return
    else:
        if str(screenshot_size[0]) != display_width or str(screenshot_size[1]) != display_height:
            # does NOT have the right device resolution
            return

    if landscape:
        offset_y = offset_y - screenshot_size[1]

    mask = ""
    if mask_path:
        mask = Image.open(os.path.join(android_home, "skins", device, mask_path))

    if mask:
        masked_screenshot = Image.alpha_composite(screenshot, mask)
    else:
        masked_screenshot = screenshot

    new_image = Image.new('RGBA', (back_size[0], back_size[1]), (255, 0, 0, 0))

    new_image.paste(back, (0, 0), back)
    new_image.paste(masked_screenshot, (offset_x, offset_y), masked_screenshot)

    new_image.save("output\\" + device + "\\" + path, "PNG")


def read_layout(device):
    layout = open(os.path.join(android_home, "skins", device, "layout")).read()
    return layout


if __name__ == '__main__':
    main()
