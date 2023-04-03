from enum import Enum
from dataclasses import dataclass


class Brand(Enum):
    """Enum of all the manufacturer emojis."""

    AUDI = '<:audi:1039362791565447207>'
    BENTLEY = '<:bentley:1039364290458693632>'
    CORVETTE = '<:corvette:1041686375419887706>'
    BMW = '<:bmw:1039365772042043432>'
    DODGE = '<:dodge:1041687321717768222>'
    FERRARI = '<:ferrari:1039362310596198500>'
    HONDA = '<:honda:1039364889371742328>'
    LAMBORGHINI = '<:lamborghini:1039363557659267102>'
    MCLAREN = '<:mclaren:1039363410401439844>'
    MERCEDES = '<:mercedes:1039365454659072030>'
    NISSAN = '<:nissan:1039364475020660747>'
    PORSCHE = '<:porsche:1039368080981233704>'


@dataclass(frozen=True)
class GT3Team:
    """A dataclass for GT3 teams in OM.

    Attributes:
        role_id: GT3 team role ID in the OM server
        supported_brands: Brands supported by the team"""

    role_id: int
    supported_brands: list[Brand]


GT3_TEAMS = [
    GT3Team(1060062099402932284, [Brand.AUDI, Brand.LAMBORGHINI]),  # Attempto Racing
    GT3Team(1060098426123067475, [Brand.HONDA]),  # Team Honda Racing
    GT3Team(1060059982877425724, [Brand.FERRARI, Brand.MCLAREN]),  # Inception Racing
    GT3Team(1060067765085552670, [Brand.MERCEDES, Brand.MCLAREN]),  # JP Motorsports
    GT3Team(1060060816377905252, [Brand.LAMBORGHINI, Brand.BENTLEY]),  # K-PAX Racing
    GT3Team(1060060292870053939, [Brand.HONDA, Brand.NISSAN]),  # KCMG
    GT3Team(1060099546480390154, [Brand.NISSAN]),  # Motul Team RJN
    GT3Team(1061580491913953352, [Brand.DODGE]),  # Riley Motorsports
    GT3Team(1060097709140344853, [Brand.BMW]),  # Schubert Motorsport
    GT3Team(1059822368597483600, [Brand.PORSCHE, Brand.MERCEDES]),  # Toro Racing Team
    GT3Team(1059830758769950741, [Brand.AUDI, Brand.BMW]),  # WRT Racing Team
    GT3Team(1061581029724393492, [Brand.DODGE]),  # Team Zakspeed
]


@dataclass(frozen=True)
class GTETeam:
    """A dataclass for GTE teams in OM.

    Attributes:
        role_id: GTE team role ID in the OM server
        supported_brands: Team's manufacturer brand (named as such for compatibility with GT3)"""

    role_id: int
    supported_brands: list[Brand]


GTE_TEAMS = [
    GTETeam(1058481242334564424, [Brand.BMW]),  # BMW M8 GTE
    GTETeam(1039197978977652886, [Brand.CORVETTE]),  # Chevrolet Corvette C8 GTE
    GTETeam(1058480948989149424, [Brand.FERRARI]),  # Ferrari 458 GTE
    GTETeam(1058481450124578866, [Brand.PORSCHE]),  # Porsche 911 RSR GTE
]
