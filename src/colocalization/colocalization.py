import math

import numpy as np
import scipy.stats as stats

from .. import ImageTIFF


def costesthresholds(img: ImageTIFF, channel1: str, channel2: str):
    threshold1 = img.maxvalue // 10
    threshold2 = img.maxvalue // 10
    c1_values = np.array([])
    c2_values = np.array([])
    temparr_copy = img.copyArray()
    c1_temparr = np.ravel(temparr_copy[:, :, img.colors[channel1]], order='C')
    c2_temparr = np.ravel(temparr_copy[:, :, img.colors[channel2]], order='C')
    for i in range(img.maxvalue // 10):
        list1 = np.where(c1_temparr > threshold1 - i)
        list2 = np.where(c2_temparr > threshold2 - i)
        indices = np.intersect1d(list1, list2)
        c1_values = np.concatenate((c1_values, c1_temparr[indices]))
        c2_values = np.concatenate((c2_values, c2_temparr[indices]))
        c1_temparr[indices] = 0
        c2_temparr[indices] = 0
        if not (np.size(c1_values) < 2 or np.size(c2_values) < 2):
            r, p = stats.pearsonr(c1_values, c2_values)
            print(f'r = {r}, p = {p}')
            if r <= 0:
                return [threshold1 - i + 1, threshold2 - i + 1]
    return [threshold1, threshold2]


def costesthresholdsfast(image: ImageTIFF, channel1: str, channel2: str):
    rthreshold = math.pow(10, -13)
    c1_values = np.ravel(ImageTIFF.getChannel(image, channel1), order='C')
    c2_values = np.ravel(ImageTIFF.getChannel(image, channel2), order='C')

    threshold1 = (np.max(c1_values) + np.mean(c1_values)) // 2
    threshold2 = (np.max(c2_values) + np.mean(c2_values)) // 2
    previousT1 = threshold1
    previousT2 = threshold2
    lastpositivet1 = threshold1
    lastpositivet2 = threshold2
    stopBoolean = False
    niter = math.ceil(math.log2(image.maxvalue))
    while not stopBoolean:
        list1 = np.where(c1_values < threshold1)
        list2 = np.where(c2_values < threshold2)
        indices = np.intersect1d(list1, list2)
        # print(f'T1 = {threshold1}, T2 = {threshold2}, size(indices) = {np.size(indices)}')
        if np.size(indices) > 1:
            r, p = stats.pearsonr(c1_values[indices], c2_values[indices])
            # print(f'r = {r}, p = {p}')
            if abs(r) < rthreshold or (threshold1 == 0 and threshold2 == 0) or niter < 1:
                stopBoolean = True
                pass
            elif r > 0:
                if previousT1 < threshold1 and previousT2 < threshold2:
                    lastpositivet1 = threshold1
                    lastpositivet2 = threshold2
                    threshold1 = (threshold1 + previousT1) // 2
                    threshold2 = (threshold2 + previousT2) // 2
                    previousT1 = lastpositivet1
                    previousT2 = lastpositivet2
                    pass
                else:
                    lastpositivet1 = threshold1
                    lastpositivet2 = threshold2
                    previousT1 = lastpositivet1
                    previousT2 = lastpositivet2
                    threshold1 = threshold1 // 2
                    threshold2 = threshold2 // 2
                pass
            elif r < 0:
                previousT1 = threshold1
                previousT2 = threshold2
                threshold1 = (threshold1 + lastpositivet1) // 2
                threshold2 = (threshold2 + lastpositivet2) // 2
                pass
            pass
        else:
            threshold1 = threshold1 // 2
            threshold2 = threshold2 // 2
            previousT1 = threshold1
            previousT2 = threshold2
            pass
        niter = niter - 1
    return [threshold1, threshold2]


def colocalization(img: ImageTIFF, channel1: str, threshold1: int, channel2: str, threshold2: int):
    c1_values = np.ravel(ImageTIFF.getChannel(img, channel1), order='C')
    c2_values = np.ravel(ImageTIFF.getChannel(img, channel2), order='C')
    list1 = np.where(c1_values >= threshold1)
    list2 = np.where(c2_values >= threshold2)
    indices = np.intersect1d(list1, list2)
    outr, outp = stats.pearsonr(c1_values[indices], c2_values[indices])
    outm1 = np.sum(c1_values[indices]) / np.sum(c1_values)
    outm2 = np.sum(c2_values[indices]) / np.sum(c2_values)
    return outr, outp, outm1, outm2


