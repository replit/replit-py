# Pure Python ANSI Color Escape Code generator

def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)

class color():
  '''
  Dynamic Color: Accepts RGB Color
  '''

  def __init__(self, r : int, g : int, b : int):

    '''
    Generate an ANSI escape code for color

    Exceptions:
      ValueError  
    
    '''

    if r < 0 or g < 0 or b < 0:
      raise ValueError('No Color Support for colors under 0')
    if r > 255 or g > 255 or b > 255:
      raise ValueError('No Color Support for colors over 255')

    self.rgb = (r, g, b)
    self.fg = f'\033[38;2;{r};{g};{b}m'
    self.bg = f'\033[48;2;{r};{g};{b}m'

  @classmethod
  def hexdec(cls, hexvalue : str):
    '''
    Convert Hex Value to RGB
    then generate an ANSI escape code
    '''

    try:
      hexvalue = hexvalue.lstrip('#')
      r, g, b = tuple(int(hexvalue[i:i+2], 16) for i in (0, 2, 4))
    except Exception as e:
      raise ValueError(f'Error while converting Hex to RGB - {e}')

    return cls(r, g, b)

class bit():
  def __init__(self, value : int):
    '''
    Use a 8bit colorpallete
    colors from  0-255 (256 total)
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
red = color(255, 0, 0)
orange = color(255, 165, 0)
yellow = color(255,255,0)
green = color(0,255,0)
blue = color(0,0,255)
indigo = color(75,0,130)
violet = color(238,130,238)
purple = color(128,0,128)
pink = color(255,105,180)
brown = color(165,42,42)
brightred = color(250,128,114)
brightorange = color(255,215,0)
brightyellow = color(255, 255, 102)
brightgreen = color(102, 255, 102)
brightblue = color(102, 178, 255)
brightpurple = color(178, 102, 255)
darkred = color(139,0,0)
darkorange = color(255,140,0)
darkyellow = color(204, 204, 0)
darkgreen = color(0, 153, 0)
darkblue = color(0, 0, 204)
darkpurple = color(102, 0, 204)
