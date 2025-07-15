import fitz
from PIL import Image
import os
import pytesseract

def words_in_box(data, bounds):
    x_min, y_min, x_max, y_max = bounds
    words = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 0 and data['text'][i].strip() != "":
            x_word = data['left'][i]
            y_word = data['top'][i]
            w_word = data['width'][i]
            h_word = data['height'][i]
            
            if (x_word >= x_min and y_word >= y_min and
                (x_word + w_word) <= x_max and (y_word + h_word) <= y_max):
                words.append(data['text'][i])
    return words

labelMap = {
    "fedex ground": "/fedex_ground",
    "express saver": "/fedex_express",
    "2day": "/fedex_express",
    "usps parcel select": "/ups_surepost",
    "ups ground": "/ups_ground",
    "ups next day": "/ups_ground",
    "usps priority": "/usps_prio",
    "usps ground": "/usps_ground"
}

label_bounded_Map = {
    "fedex ground": (440, 146, 866, 261),
    "express saver": (148, 253, 800, 460),
    "2day": (148, 253, 800, 460),
    "usps parcel select": (226, 920, 800, 992),
    "ups ground": (160, 285, 800, 480),
    "ups next day": (160, 285, 800, 480),
    "usps priority": (185, 643, 820, 840),
    "usps ground": (190, 640, 866, 840)
}

usps_prio_cubic = (320, 546, 880, 706)

def extract_label_info(i, page):
    dpi = 200
    crop_rect = (0, 4.2*72, 4.6*72, 12*72)
    clip = fitz.Rect(*crop_rect)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip)

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    text = pytesseract.image_to_string(img)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    if len(text) == 0: 
        return None
    
    box = None
    label = None
    for key, bounds in label_bounded_Map.items():
        if key in text.lower():
            if key == "usps priority" and "cubic" in text.lower():
                box = usps_prio_cubic
                label = "usps priority - cubic"
                break
            box = bounds
            label = key
            break
    
    if box:
        words = words_in_box(data, box)
        words = " ".join(words).strip()
        return words
        # print(f"Index: {i+1}\n")
        # print(f"Address: {words}\n")
        # print(f"Label: {label}\n \n")
        
    else:
        print(f"label {i} not indentified")
        save_path = f"{os.getcwd()}/unknown/label_{i}.png"
        img.save(save_path)
        return None

def extract_sku_info(i, page):
    # Define bounding boxes: (x_min, y_min, x_max, y_max)
    sku_bbox = (300, 120, 380, 150)
    qty_bbox = (460, 120, 480, 150)

    sku_words = []
    qty_words = []

    for w in page.get_text("words"):
        x0, y0, x1, y1, word = w[:5]
        x_center = (x0 + x1) / 2
        y_center = (y0 + y1) / 2

        # Check if word is in SKU bounding box
        if (sku_bbox[0] <= x_center <= sku_bbox[2]) and (sku_bbox[1] <= y_center <= sku_bbox[3]):
            sku_words.append(word)
        # Check if word is in Quantity bounding box
        if (qty_bbox[0] <= x_center <= qty_bbox[2]) and (qty_bbox[1] <= y_center <= qty_bbox[3]):
            qty_words.append(word)

    sku = " ".join(sku_words).strip()
    quantity = " ".join(qty_words).strip()
    return (sku, quantity)
    
    