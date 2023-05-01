import cv2


def ParticleAnalyzer(area: tuple[int | float, int | float] | None = None,
                     threshold: tuple[int, int] | None = None,
                     threshold_step: int | float = 10,
                     circularity: tuple[float | float] | None = None,
                     convexity: tuple[float | float] | None = None,
                     inertia_ratio: tuple[float | float] | None = None):
    """
    Create a ParticleAnalyzer object using OpenCV whose default parameters resemble ImageJ's "Analyze Particles"
    analysis as closely as possible.
    :param area:
    :param threshold:
    :param threshold_step:
    :param circularity:
    :param convexity:
    :param inertia_ratio:
    :return:
    """
    # Define the parameters for the Particle Analyzer
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True

    # Define the default parameters used in ImageJ
    default_params = {
        'area': (10, 1000000),
        'threshold': (0, 255),
        'circularity': (0.1, 1.0),
        'convexity': (0.87, 1.0),
        'inertia_ratio': (0.1, 1.0)
    }

    # Set new/default parameters
    if not area:
        area = default_params['area']
    if not threshold:
        threshold = default_params['threshold']
    if not circularity:
        params.filterByCircularity = False
        circularity = default_params['circularity']
    else:
        params.filterByCircularity = True
    if not convexity:
        params.filterByConvexity = False
        convexity = default_params['convexity']
    else:
        params.filterByConvexity = True
    if not inertia_ratio:
        params.filterByInertia = False
        inertia_ratio = default_params['inertia_ratio']
    else:
        params.filterByInertia = True

    # Transfer parameters to particle analyzer
    params.minArea = area[0]
    params.maxArea = area[1]
    params.thresholdStep = threshold_step
    params.minThreshold = threshold[0]
    params.maxThreshold = threshold[1]
    params.minCircularity = circularity[0]
    params.maxCircularity = circularity[1]
    params.minConvexity = convexity[0]
    params.maxConvexity = convexity[1]
    params.minInertiaRatio = inertia_ratio[0]
    params.maxInertiaRatio = inertia_ratio[1]

    return cv2.SimpleBlobDetector_create(params)

