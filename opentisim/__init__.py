"""Top-level package for OpenTISim."""

# import pkg_resources

import opentisim.core as core
import opentisim.plot as plot
import opentisim.liquidbulk as liquidbulk
import opentisim.containers as containers
#import opentisim.drybulk as drybulk

__author__ = """Mark van Koningsveld"""
__email__ = 'M.vanKoningsveld@tudelft.nl'
__version__ = 'v0.6.2'
__all__ = ["model", "plugins", "core", "plot"]
# __version__ = pkg_resources.get_distribution(__name__).version


