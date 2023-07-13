from colorama import Back, Style


def print_color(text, color):
  color_to_colorama = {
    'green': Back.GREEN,
    'blue': Back.BLUE,
  }
  print(color_to_colorama[color], text, Style.RESET_ALL)