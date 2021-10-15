from PIL import Image, ImageDraw
import json

colors = {0: "brown", 1: "red", 2: "green", 3: "blue", 4: "yellow", 5: "orange", 6: "purple", 7: "pink", 9: "black", 10: "white"}

def get_shapes(fpath):
    with open(fpath) as f:
        data = json.load(f)
    shapes = data["shapes"]
    return shapes

def crop_shapes(shapes: list, crop_bbox: list):
    """
    shapes is a list of dicts where each dict has the following keys:
    - label: str - name of the label
    - points: list of lists - list of points with actual coordinates
    - shape_type: str - type of the shape

    image_width and image_height are the width and height of the image
    crop_bbox is a list of 4 numbers representing the bounding box along which the annnotations inside the image are cropped
    """
    def is_outside_crop_bbox(point, bbox):
        """
        point is a list of 2 numbers representing the x and y coordinates of a point
        """
        x, y = point
        return x < bbox[0] or x > bbox[2] or y < bbox[1] or y > bbox[3]

    def clip_point(point, bbox):
        """" clips a point inside bbox """
        x, y = point
        x = max(x, bbox[0])
        x = min(x, bbox[2])
        y = max(y, bbox[1])
        y = min(y, bbox[3])
        return x, y

    cropped_shapes = []
    for shape in shapes:
        cropped_points = []
        for point in shape["points"]:
            if not is_outside_crop_bbox(point, crop_bbox):
                cropped_points.append(point)
            else:
                new_point = clip_point(point, crop_bbox)
                cropped_points.append(new_point)

        cropped_shapes.append({"label": shape["label"], "points": cropped_points, "shape_type": shape["shape_type"]})
    return cropped_shapes

def draw_shapes(shapes, im, bb_actual, show=False):
    """
    shapes is a list of dicts where each dict has the following keys:
    - label: str - name of the label
    - points: list of lists - list of points with actual coordinates
    - shape_type: str - type of the shape

    im is a PIL image object
    """
    draw = ImageDraw.Draw(im)
    draw.rectangle(bb_actual, outline="black", width=40)
    for id, shape in enumerate(shapes):
        points = [tuple(i) for i in shape["points"]]
        if shape["shape_type"] == "rectangle":
            draw.rectangle(points, outline="red")
        elif shape["shape_type"] == "polygon":
            draw.polygon(points, outline="red", fill=colors[id])
        elif shape["shape_type"] == "point":
            draw.point(points, fill="red")
        elif shape["shape_type"] == "line":
            draw.line(points, fill="red")
        elif shape["shape_type"] == "circle":
            draw.ellipse(points, outline="red")
        else:
            print("Shape type not supported")
    if show:
        im.show()
    return im

if __name__ == "__main__":
    annot_path = '1_0000000104.json'
    image_path = '1_0000000104.JPG'
    
    im = Image.open(image_path)
    bb_actual = [0.6*im.width, 
                 0.05*im.height, 
                 im.width-(1-0.9)*im.width, 
                 im.height-(1-0.8)*im.height]

    shapes_annot = get_shapes(annot_path)
    shapes_crop = crop_shapes(shapes_annot, bb_actual)
    
    im = draw_shapes(shapes_crop, im, bb_actual)
    im.save("test.jpg")