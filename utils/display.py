from rgbmatrix import RGBMatrixOptions, RGBMatrix

# Display info
display_rows = 32
display_columns = 64
chain_length = 1
parallel = 1

# Pre-initialized matrix
matrix = None

# Matrix instance
def initialize_display():
    global matrix
    options = RGBMatrixOptions()
    options.rows = display_rows
    options.cols = display_columns
    options.chain_length = chain_length
    options.parallel = parallel
    options.hardware_mapping = 'regular'
    matrix = RGBMatrix(options=options)

def get_rgb_matrix():
    return matrix
