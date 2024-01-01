from enum import Enum, auto
from dash import html

import util


class License(Enum):
    UNSPECIFIED = auto()
    OPEN_RAIL_M = auto()
    CREATIVEML_OPEN_RAIL_M = auto()
    CC_UNSPECIFIC = auto()
    CC_BY_4 = auto()
    CC0_1 = auto()
    AFL_3 = auto()
    LGPL_LR = auto()
    GPL = auto()
    CC_BY_NC_ND_2 = auto()
    CC_BY_NC_ND_3 = auto()
    ARTISTIC_2 = auto()
    MIT = auto()


def get_license_enum(license_name):
    return util.get_enum_by_string(License, license_name)


def is_ui_notice_required(license_enum):
    return license_enum in [License.OPEN_RAIL_M, License.CC_UNSPECIFIC, License.LGPL_LR, License.GPL,
                            License.CC_BY_NC_ND_2, License.CC_BY_NC_ND_3]


def get_verbiage(license_enum, additional_text):
    if additional_text is None:
        additional_text = ''
    return{
        License.OPEN_RAIL_M: [html.Div('The use of this model is governed by the Open RAIL-M license. By using this '
                                       'model, you agree to the restrictions outlined in Attachment A of the license:'),
                              html.A('Open RAIL-M License', href=get_license_link(license_enum))],
        License.CREATIVEML_OPEN_RAIL_M: [html.Div('The use of this model is governed by the CreativeML Open RAIL-M '
                                                  'license. By using this model, you agree to the restrictions '
                                                  'outlined in Attachment A of the license:'),
                              html.A('CreativeML Open RAIL-M License', href=get_license_link(license_enum))],

        License.CC_UNSPECIFIC: [html.Div('This model is licensed under Creative Commons by ' + additional_text)],
        License.CC_BY_NC_ND_2: [html.Div('This model is licensed under Creative Commons (BY-NC-ND) by '
                                         + additional_text
                                         + '. You may use this model for noncommercial purposes only.')],
        License.CC_BY_NC_ND_3: [html.Div('This model is licensed under Creative Commons (BY-NC-ND) by '
                                         + additional_text
                                         + '. You may use this model for noncommercial purposes only.')],
        License.LGPL_LR: [html.Div('This model is licensed under LGPL-LR by ' + additional_text),
                          html.A('Lesser General Public License for Linguistic Resources',
                                 href=get_license_link(license_enum))],
        License.GPL: [html.Div('This model is licensed under GPL by ' + additional_text),
                      html.A('GNU General Public License',
                             href=get_license_link(license_enum))]
    }.get(license_enum, html.Div(''))


def get_license_link(license_enum):
    return {
        License.OPEN_RAIL_M: 'https://static1.squarespace.com/static/5c2a6d5c45776e85d1482a7e/t/'
                             '6308bb4bba3a2a045b72a4b0/1661516619868/BigScience+Open+RAIL-M+License.pdf',
        License.CREATIVEML_OPEN_RAIL_M: 'https://huggingface.co/spaces/CompVis/stable-diffusion-license',
        License.CC_UNSPECIFIC: 'https://creativecommons.org/licenses/',
        License.CC_BY_4: 'https://creativecommons.org/licenses/by/4.0/',
        License.CC0_1: 'https://creativecommons.org/publicdomain/zero/1.0/',
        License.AFL_3: 'https://opensource.org/license/afl-3-0-php/',
        License.LGPL_LR: 'https://spdx.org/licenses/LGPLLR',
        License.GPL: 'https://www.gnu.org/licenses/gpl-3.0',
        License.CC_BY_NC_ND_2: 'https://creativecommons.org/licenses/by-nc-nd/2.0/',
        License.CC_BY_NC_ND_3: 'https://creativecommons.org/licenses/by-nc-nd/3.0/',
        License.ARTISTIC_2: 'https://opensource.org/license/artistic-2-0/'
    }.get(license_enum)
