import numpy as np

from copy import deepcopy
from .. import ImageTIFF


def thresholdchannel(img: ImageTIFF, tissue='Gastroc', channelcolor='red', whitebackground=True):
    # Gastroc is base case
    # Soleus = Gastroc
    # Pancreus is very blue (maybe 3rd factor for blue only)?
    # Adrenal is very red and blue
    # Heart is similar to gastroc but a little more blue
    # Ileum is similar to Heart
    # Tunica Muscularis is similar to Pancreus
    # Kidney is like Adrenal, maybe less blue but it is also a bit red
    # Liver is like Heart
    # Lung is like Pancreus
    # Skin is like Ileum
    tissuetypes = {'Gastroc': 0,  # pretty good,
                   'Soleus': 0,  # pretty good
                   'Heart': 1,
                   # half of the heart is good and the other half is too red (high values of all colors but mostly red)
                   'Ileum': 1,  # pretty good but dots are too concentrated to distinguish them
                   'Liver': 1,  # works great
                   'Skin': 1,
                   'Pancreas': 2,
                   # pretty good but there are a bunch of blue dots which not sure if they are structres or actual dots
                   'TunicaMuscularis': 2,  # pretty good, picks up some non dots
                   'Lung': 2,  # pretty good as well
                   'AdrenalMedulla': 2,  # good
                   'Adrenal': 3,
                   # think it works great, cannot tell because the analyze particles isn't working properly
                   'Kidney': 3,  # pretty good too
                   'KidneyMedulla': 2,  # pretty good actually
                   'KidneyInnerMedulla': 2}  # works amazingly

    def colorish(r, g, b):
        cutoff = 85

        def isnotcolorC2correction(c1, c2, c3):
            c1factor = 1
            c2factor = 1.15
            return c1 > cutoff and c2 > cutoff and c3 > cutoff and c1 > c2 * c1factor and c2 > c3 * c2factor

        def iscolorC3correction(c1, c2, c3):
            c2factor = 1.1
            c1c3_offset_ratio = 0.15
            c1c3max = np.max([c1, c3, 1])
            return c1 > cutoff and c1 > c2 * c2factor and c3 > c2 * c2factor \
                   and 1 - (c1 / c1c3max) <= c1c3_offset_ratio and 1 - (c3 / c1c3max) <= c1c3_offset_ratio

        def iscolor(c1, c2, c3):
            factor1 = 1.3
            factor2 = 1.15
            mean_offset_ratio = 0.15
            mean = np.mean([c2, c3])
            c2_diff = np.abs(c2 - mean)
            c3_diff = np.abs(c3 - mean)
            return c1 > cutoff and ((c1 > c2 * factor1 and c1 > c3 * factor1)
                                    or (c2_diff < mean * mean_offset_ratio and c3_diff < mean * mean_offset_ratio
                                        and c1 > c2 * factor2 and c1 > c3 * factor2))

        # i love cc
        if not isnotcolorC2correction(r, g, b) and (iscolor(r, g, b) or iscolorC3correction(r, g, b)):
            return 'red'
        elif not isnotcolorC2correction(g, r, b) and (iscolor(g, r, b) or iscolorC3correction(g, r, b)):
            return 'green'
        elif not isnotcolorC2correction(b, r, g) and (iscolor(b, r, g) or iscolorC3correction(b, r, g)):
            return 'blue'
        else:
            return 'other'

    channel = img.colors[channelcolor]
    for [i, j], value in np.ndenumerate(img.image[:, :, channel]):
        red = img.image[i, j, channel]
        blue = img.image[i, j, img.colors['blue']]
        green = img.image[i, j, img.colors['green']]
        color = colorish(red, green, blue)
        if color == channelcolor:
            tmp = deepcopy(img.image[i, j, img.colors[channelcolor]]).astype(np.uint8)
            # self.image[i, j, :] = np.zeros(3, dtype=np.uint8)
            if whitebackground:
                img.image[i, j, img.colors[channelcolor]] = np.uint8(255) - tmp
                pass
            else:
                img.image[i, j, img.colors[channelcolor]] = tmp
                pass
            pass
        else:
            # self.image[i, j, :] = np.zeros(3, dtype=np.uint8)
            img.image[i, j, channel] = np.uint8(0)
            pass
    return img

