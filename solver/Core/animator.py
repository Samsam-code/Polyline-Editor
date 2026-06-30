from YansAnimator import draw_svg as svg
from YansAnimator import video_svg as video
from GeneralCase import center_core as cc

DEFAULT_GRID = (15, 50, 30, 20)

def draw_polyline(grid, points, path, filename="svg-polyline.svg", center=None):
    file = svg.createSVG(filename)

    polyline = [points[v] for v in path]
    svg.drawWindow(file, grid)
    svg.drawGrid(file, grid, "black")
    svg.drawPolyline(file, grid, polyline, "teal")

    endpoints = {path[0], path[-1]}
    turning_vertices = set(path[i] for i in cc.turning_vertices(points, center, path))
    for i, p in enumerate(points):
        if i in endpoints:
            color = "red" 
        elif i in turning_vertices:
            color = "olive"
        else:
            color = "yellowgreen"
        svg.drawPoint(file, grid, p, color)

    if center is not None:
        svg.drawPoint(file, grid, center, "orange")

    svg.closeSVG(file)

def generate_image_t(grid, points, path_sequence, center=None):
    l = len(path_sequence)
    epsilon = .0001
    def image_t(t, filename):
        t-=epsilon
        return draw_polyline(grid, points, path_sequence[int(l*t)], filename, center=center)
    return image_t

def create_video_polyline(grid, points, path_sequence, video_name, duration=None, center=None):
    if duration is None:
        duration = len(path_sequence)
    fps = (len(path_sequence)-1)//duration +1
    image_t = generate_image_t(grid, points, path_sequence, center=center)
    video.create_video(video_name, image_t, fps, duration)

def create_gif_polyline(grid, points, path_sequence, gif_name, duration=None, center=None):
    if duration is None:
        duration = len(path_sequence)
    fps = (len(path_sequence)-1)//duration +1
    image_t = generate_image_t(grid, points, path_sequence, center=center)
    video.create_gif(gif_name, image_t, fps, duration)


if __name__ == "__main__":
    from polyline import generate_random_points, generate_random_polyline

    points = generate_random_points(10)
    polyline = generate_random_polyline(points)
    #draw_polyline(DEFAULT_GRID, points, polyline)

    random_paths = [generate_random_polyline(points) for _ in range(10)]
    create_gif_polyline(DEFAULT_GRID, points, random_paths, "Random polylines")





