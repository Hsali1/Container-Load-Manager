from collections import namedtuple
from os import name

Box = namedtuple("Box", "id name height width length")

Container = namedtuple("Container", "id occupied_volume")