from .. import threshold_huang, ParticleAnalyzer, FindMaxima

if __name__ == '__main__':
    # Test imagepath
    image_path = r"F:\Aaron Y - extra space\Orbit H&E\Cyno TIF annotations - output\too big\uncompressed" \
                 r"\SP-012102_1001.22 adrenal gland_Mfa-SSB-O1_Default_Extendedlf_UNCOMPRESSED.tif"

    # Threshold the blue channel to get image area
    thresholded_image_array = threshold_huang(image_path, color_channel='blue')
    # Generate particle analyzer
    particle_analyzer = ParticleAnalyzer()
    # Apply particle analyzer to thresholded image
    # Dilate and close holes, then sum particles together to get total area

    # Find maxima of red channel
    maxima = FindMaxima(image_path, color_channel='red')
    pass
