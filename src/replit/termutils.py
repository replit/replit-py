"""Pure Python ANSI Color Escape Code generator."""
import colorsys


def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)


class Color:
    """Dynamic Color: Accepts RGB Color."""

    def __init__(self, r: int, g: int, b: int) -> None:

        """
        Generate an ANSI escape code for color

        Args:
          r (int): Amount of red in color
          g (int): Amount of green in color
          b (int): Amount of blue in color

        Raises:
          ValueError
        """

        if r < 0 or g < 0 or b < 0:
            raise ValueError("No Color Support for colors under 0")
        if r > 255 or g > 255 or b > 255:
            raise ValueError("No Color Support for colors over 255")

        self.rgb = (r, g, b)
        self.fg = f"\033[38;2;{r};{g};{b}m"
        self.bg = f"\033[48;2;{r};{g};{b}m"

    @classmethod
    def hexdec(cls, hexvalue: str) -> None:
        """
        Convert Hex Value to RGB
        then generate an ANSI escape code

        Args:
          hexvalue (str): The color's hex value
        
        Raises:
          ValueError

        Returns:
          color : RGB colors from Hex Value
        """

        try:
            hexvalue = hexvalue.lstrip("#")
            r, g, b = tuple(int(hexvalue[i : i + 2], 16) for i in (0, 2, 4))
        except Exception as e:
            raise ValueError(f"Error while converting Hex to RGB - {e}")

        return cls(r, g, b)

    @classmethod
    def hsv(cls, h, s, v) -> None:
        """
        Convert Hex Value to RGB
        then generate an ANSI escape code

        Args:
          hexvalue (str): The color's hex value
        
        Raises:
          ValueError

        Returns:
          color : RGB colors from Hex Value
        """
        try:
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
        except:
            raise ValueError("Converting HSV to RGB ran into an error")

        return cls(r, g, b)

    @classmethod
    def hls(cls, h, l, s):
        """
        Convert Hex Value to RGB
        then generate an ANSI escape code

        Args:
          hexvalue (str): The color's hex value
        
        Raises:
          ValueError

        Returns:
          color : RGB colors from Hex Value
        """
        try:
            r, g, b = colorsys.hls_to_rgb(h, s, v)
        except:
            raise ValueError("Converting HLS to RGB ran into an error")

        return cls(r, g, b)


class Bit:
    def __init__(self, value: int) -> None:
        """
        Use a 8bit colorpallete
        colors from  0-255 (256 total)

        Args:
          value (int): A color value from 0 to 255

        Raises:
          ValueError
        """

        if value > 255:
            raise ValueError("8 Bit Pallete - No Color Support for Colors over 255")
        if value < 0:
            raise ValueError("8 Bit Pallete - No Color Support for colors under 0")

        self.fg = f"\033[38;5;{value}m"
        self.bg = f"\033[48;5;{value}m"


attributes = {  # use only repl.it supported ansi codes. Codes such as blink do not work.
    "reset": 0,
    "bold": 1,
    "faint": 2,
    "italic": 3,
    "underline": 4,
    "highlight": 7,
}


class Attr:
    def __init__(self, attrib: str) -> None:
        """
        Custom Attributes such as bold and italic
        Returns ANSI Escape

        Args:
          attrib (str): Special Styles for characters

        Raises:
          ValueError
        """

        if attrib in attributes:
            self.attr = f"\033[{attributes[attrib]}m"
        else:
            raise ValueError(f"Attributes - {attrib} is not supported.")


reset = Attr("reset").attr
bold = Attr("bold").attr
italic = Attr("italic").attr
red = Color(255, 0, 0)
orange = Color(255, 165, 0)
yellow = Color(255, 255, 0)
green = Color(0, 255, 0)
blue = Color(0, 0, 255)
indigo = Color(75, 0, 130)
violet = Color(238, 130, 238)
purple = Color(128, 0, 128)
pink = Color(255, 105, 180)
brown = Color(165, 42, 42)
brightred = Color(250, 128, 114)
brightorange = Color(255, 215, 0)
brightyellow = Color(255, 255, 102)
brightgreen = Color(102, 255, 102)
brightblue = Color(102, 178, 255)
brightpurple = Color(178, 102, 255)
darkred = Color(139, 0, 0)
darkorange = Color(255, 140, 0)
darkyellow = Color(204, 204, 0)
darkgreen = Color(0, 153, 0)
darkblue = Color(0, 0, 204)
darkpurple = Color(102, 0, 204)
