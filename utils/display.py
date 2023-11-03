from rgbmatrix import RGBMatrixOptions, RGBMatrix

# Display info
display_rows = 32
display_columns = 64

# Pre-initialized matrix
matrix = None

# Matrix instance
def initialize_display():
    global matrix
    options = RGBMatrixOptions()
    options.rows = display_rows
    options.cols = display_columns
    matrix = RGBMatrix(options=options)

def get_rgb_matrix():
    return matrix
