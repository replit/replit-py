# Pure Python ANSI Color Escape Code generator

def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)

class hexdec():
  def __init__(self, hexvalue : str):

    '''
    Convert Hex Value to RGB
    then generate an ANSI escape code
    '''

    hexvalue = hexvalue.lstrip('#')
    self.rgb = tuple(int(hexvalue[i:i+2], 16) for i in (0, 2, 4))

    r, g, b = self.rgb

    self.fg = f'\033[38;2;{r};{g};{b}m'
    self.bg = f'\033[48;2;{r};{g};{b}m'

class rgb():
  def __init__(self, r : int, g : int, b : int):

    '''
    Generate an ANSI escape code for color

    Exceptions:
      ValueError  
    
    '''

    if r < 0 or g < 0 or b < 0:
      raise ValueError('RGB Pallete - No Color Support for colors under 0')
    if r > 255 or g > 255 or b > 255:
      raise ValueError('RGB Pallete - No Color Support for colors over 255')

    self.fg = f'\033[38;2;{r};{g};{b}m'
    self.bg = f'\033[48;2;{r};{g};{b}m'

class bit():
  def __init__(self, value : int):
    '''
    Use a 8bit colorpallete
    colors from  0-255 (256 total)
    Exceptions:
      ValueError
    '''

    if value > 255:
      raise ValueError('8 Bit Pallete - No Color Support for Colors over 255')

    self.fg = f'\033[38;5;{value}m'
    self.bg = f'\033[48;5;{value}m'

attributes = { #use only repl.it supported ansi codes. Codes such as blink do not work.
  'reset': 0,
  'bold': 1,
  'faint': 2,
  'italic': 3,
  'underline': 4,
  'highlight': 7
}

class attr():
  def __init__(self, attrib : str):
    '''
    Custom Attributes such as bold and italic
    Returns ANSI Escape
    Exceptions:
      ValueError
    '''

    if attrib in attributes:
      self.attr = f'\033[{attributes[attrib]}m'
    else:
      raise ValueError(f"Attributes - {attrib} is not supported.")
  
#predefined variables
reset = attr('reset').attr
bold = attr('bold').attr
italic = attr('italic').attr
red = rgb(255, 0, 0)
orange = rgb(255, 165, 0)
yellow = rgb(255,255,0)
green = rgb(0,255,0)
blue = rgb(0,0,255)
indigo = rgb(75,0,130)
violet = rgb(238,130,238)
purple = rgb(128,0,128)
pink = rgb(255,105,180)
brown = rgb(165,42,42)
brightred = rgb(250,128,114)
brightorange = rgb(255,215,0)
brightyellow = rgb(255, 255, 102)
brightgreen = rgb(102, 255, 102)
brightblue = rgb(102, 178, 255)
brightpurple = rgb(178, 102, 255)
darkred = rgb(139,0,0)
darkorange = rgb(255,140,0)
darkyellow = rgb(204, 204, 0)
darkgreen = rgb(0, 153, 0)
darkblue = rgb(0, 0, 204)
darkpurple = rgb(102, 0, 204)