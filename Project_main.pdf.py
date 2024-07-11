import os
from google.cloud import vision
import io
from PIL import Image
import pytesseract
import pandas as pd
from pdf2image import convert_from_path

# variable for Google API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ("scannerproject-428812-c4bc2a81767a.json")

images = convert_from_path("folder_path\\naveenaadhaar.pdf", 200,poppler_path=r'C:\python\Python\Scanner_Project\poppler-23.11.0\Library\bin')
for i, image in enumerate(images):
    fname = 'image'+str(i)+'.png'
    image.save(fname, "PNG")

def extract_text_google_vision(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'{response.error.message}')

    return texts[0].description if texts else ''

def extract_text_tesseract(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

def convert_pdf_to_images(pdf_path, output_folder):
    images = convert_from_path(pdf_path)
    image_paths = []

    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"{os.path.basename(pdf_path)}_page_{i}.jpg")
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)

    return image_paths

def process_documents(folder_path, output_folder, use_google_vision=True):
    data = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith('.pdf'):
                image_paths = convert_pdf_to_images(file_path, output_folder)
                for image_path in image_paths:
                    if use_google_vision:
                        text = extract_text_google_vision(image_path)
                    else:
                        text = extract_text_tesseract(image_path)
                    data.append({
                        "file_name": image_path,
                        "extracted_text": text
                    })
            else:
                if use_google_vision:
                    text = extract_text_google_vision(file_path)
                else:
                    text = extract_text_tesseract(file_path)

                data.append({
                    "file_name": file_name,
                    "extracted_text": text
                })

    df = pd.DataFrame(data)
    return df


# example
folder_path = "folder_path"
output_folder = "output_folder"
df = process_documents(folder_path, output_folder)
df.to_csv("extracted_data.csv", index=False)
print(df)
