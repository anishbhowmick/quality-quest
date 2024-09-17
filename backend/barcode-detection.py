import cv2
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
import requests
from googletrans import Translator
import json

# Replace with your API key and custom search engine ID (cx)
API_KEY = 'AIzaSyAyE6hNpefh17tRxqsGA9L8F1qAtH5xJU8'
SEARCH_ENGINE_ID = 'c5e2548f18c9b424d'

# Define EAN Country Codes
ean_country_codes = [
    (100, 139, "United States"),
    (200, 299, "Restricted distribution"),
    (300, 379, "France and Monaco"),
    (380, 380, "Bulgaria"),
    (383, 383, "Slovenia"),
    (385, 385, "Croatia"),
    (387, 387, "Bosnia and Herzegovina"),
    (389, 389, "Montenegro"),
    (400, 440, "Germany"),
    (450, 459, "Japan"),
    (460, 469, "Russia"),
    (470, 470, "Kyrgyzstan"),
    (471, 471, "Taiwan"),
    (474, 474, "Estonia"),
    (475, 475, "Latvia"),
    (476, 476, "Azerbaijan"),
    (477, 477, "Lithuania"),
    (478, 478, "Uzbekistan"),
    (479, 479, "Sri Lanka"),
    (480, 480, "Philippines"),
    (481, 481, "Belarus"),
    (482, 482, "Ukraine"),
    (484, 484, "Moldova"),
    (485, 485, "Armenia"),
    (486, 486, "Georgia"),
    (487, 487, "Kazakhstan"),
    (488, 488, "Tajikistan"),
    (489, 489, "Hong Kong"),
    (490, 499, "Japan"),
    (500, 509, "United Kingdom"),
    (520, 521, "Greece"),
    (528, 528, "Lebanon"),
    (529, 529, "Cyprus"),
    (530, 530, "Albania"),
    (531, 531, "Macedonia"),
    (535, 535, "Malta"),
    (539, 539, "Ireland"),
    (540, 549, "Belgium and Luxembourg"),
    (560, 560, "Portugal"),
    (569, 569, "Iceland"),
    (570, 579, "Denmark, Faroe Islands and Greenland"),
    (590, 590, "Poland"),
    (594, 594, "Romania"),
    (599, 599, "Hungary"),
    (600, 601, "South Africa"),
    (603, 603, "Ghana"),
    (604, 604, "Senegal"),
    (608, 608, "Bahrain"),
    (609, 609, "Mauritius"),
    (611, 611, "Morocco"),
    (613, 613, "Algeria"),
    (615, 615, "Nigeria"),
    (616, 616, "Kenya"),
    (618, 618, "Côte d'Ivoire"),
    (619, 619, "Tunisia"),
    (621, 621, "Syria"),
    (622, 622, "Egypt"),
    (624, 624, "Libya"),
    (625, 625, "Jordan"),
    (626, 626, "Iran"),
    (627, 627, "Kuwait"),
    (628, 628, "Saudi Arabia"),
    (629, 629, "United Arab Emirates"),
    (640, 649, "Finland"),
    (690, 695, "China"),
    (700, 709, "Norway"),
    (729, 729, "Israel"),
    (730, 739, "Sweden"),
    (740, 740, "Guatemala"),
    (741, 741, "El Salvador"),
    (742, 742, "Honduras"),
    (743, 743, "Nicaragua"),
    (744, 744, "Costa Rica"),
    (745, 745, "Panama"),
    (746, 746, "Dominican Republic"),
    (750, 750, "Mexico"),
    (754, 755, "Canada"),
    (759, 759, "Venezuela"),
    (760, 769, "Switzerland and Liechtenstein"),
    (770, 771, "Colombia"),
    (773, 773, "Uruguay"),
    (775, 775, "Peru"),
    (777, 777, "Bolivia"),
    (779, 779, "Argentina"),
    (780, 780, "Chile"),
    (784, 784, "Paraguay"),
    (785, 785, "Peru"),
    (786, 786, "Ecuador"),
    (789, 790, "Brazil"),
    (800, 839, "Italy, San Marino and Vatican City"),
    (840, 849, "Spain and Andorra"),
    (850, 850, "Cuba"),
    (858, 858, "Slovakia"),
    (859, 859, "Czech Republic"),
    (860, 860, "Serbia"),
    (865, 865, "Mongolia"),
    (867, 867, "North Korea"),
    (868, 869, "Turkey"),
    (870, 879, "Netherlands"),
    (880, 880, "South Korea"),
    (884, 884, "Cambodia"),
    (885, 885, "Thailand"),
    (888, 888, "Singapore"),
    (890, 890, "India"),
    (893, 893, "Vietnam"),
    (896, 896, "Pakistan"),
    (899, 899, "Indonesia"),
    (900, 919, "Austria"),
    (930, 939, "Australia"),
    (940, 949, "New Zealand")
]

# Define UPC Country Codes
upc_country_codes = [
    (0, 19, "United States and Canada"),
    (20, 29, "Restricted distribution"),
    (30, 39, "United States drugs (National Drug Code)"),
    (40, 49, "Used to issue restricted circulation numbers within a geographic region"),
    (50, 59, "Reserved for future use"),
    (60, 99, "United States and Canada")
]

def get_country(barcode_type, barcode_data):
    try:
        if barcode_type in ['EAN13', 'EAN8']:
            prefix = int(barcode_data[:3])
            for start, end, country in ean_country_codes:
                if start <= prefix <= end:
                    return country
        elif barcode_type in ['UPC-A', 'UPC']:
            prefix = int(barcode_data[:3])
            for start, end, country in upc_country_codes:
                if start <= prefix <= end:
                    return country
    except (ValueError, IndexError):
        pass
    return "Unknown"

def search_product_by_barcode(barcode_number):
    search_query = barcode_number
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_query}"

    translator = Translator()

    try:
        response = requests.get(url)
        response.raise_for_status()
        search_results = response.json()

        if 'items' in search_results:
            for item in search_results['items'][:1]:  # Get only top result
                title = item.get('title')
                snippet = item.get('snippet').replace('\n', ' ')
                link = item.get('link')

                # Detect and translate title/snippet if needed
                if translator.detect(title).lang != 'en':
                    title = translator.translate(title, dest='en').text
                if translator.detect(snippet).lang != 'en':
                    snippet = translator.translate(snippet, dest='en').text

                # Return search result
                # return f"Product: {title}\nDescription: {snippet}\n"
                return(f"Product: {title}")
        else:
            return "No results found for the given barcode."
    except requests.exceptions.RequestException as e:
        return f"API request error: {e}"
    except Exception as e:
        return f"Translation error: {e}"

def detect_and_decode_barcode(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray)

    results = []

    for barcode in barcodes:
        if barcode.type not in ['EAN13', 'EAN8', 'UPC-A', 'UPC']:
            continue

        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type
        country = get_country(barcode_type, barcode_data)
        product_info = search_product_by_barcode(barcode_data)

        results.append({
            "barcode_data": barcode_data,
            "barcode_type": barcode_type,
            "country": country,
            "product_info": product_info
        })
        
        # print(results)
        for result in results:
            print(f"Barcode Number: {result['barcode_data']}, \nBarcode Type: {result['barcode_type']}, \nCountry: {result['country']}, \nProduct Info: {result['product_info']}")
            # print(f"Barcode Type: {result['barcode_type']}")
            # print(f"Country: {result['country']}")
            # print(f"Product Info: {result['product_info']}")

        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        text = f"{barcode_data} ({barcode_type}) - {country}"
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10, 8))
    plt.imshow(image_rgb)
    plt.axis('off')

    return results

if __name__ == "__main__":
    import sys
    image_path = sys.argv[1]  # Get image path from the command-line arguments

    detection_result = detect_and_decode_barcode(image_path)

    # Print the result as JSON so that it can be captured by the server
    # print(json.dumps(detection_result))