import json
import requests
import rasterio
from rasterio.mask import mask
from pathlib import Path
from tools.BBox import BBox
from tools.PolygonRequest import PolygonRequest


def dictionaryValue(address):
    """ Function to return address and building numpy array """

    polygon = PolygonRequest(address)

    # Tiff files path
    data_dsm_path = "/home/agcia/3DHouse/Data/DSM/GeoTIFF/"
    data_dtm_path = "/home/agcia/3DHouse/Data/DTM/GeoTIFF/"

    # Request the formatted address
    # Request BBox of the address
    # Raise an error msg if the address doesn't exist
    try:

        req = requests.get(f"http://loc.geopunt.be/geolocation/location?q={address}&c=1").json()

        # Get Bounding Box of the entered address
        bb_addr = BBox(req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["X_Lambert72"],
                       req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["Y_Lambert72"],
                       req["LocationResult"][0]["BoundingBox"]["UpperRight"]["X_Lambert72"],
                       req["LocationResult"][0]["BoundingBox"]["UpperRight"]["Y_Lambert72"])

    except IndexError:
        print(address, " :Address doesn't exist")
    except:
        print("Something else went wrong")
        exit()

    # List all tiff files in directory using Path
    # Search for the matched tiff
    # Compare the BBox address to the BBox tiff file
    files_in_data_dsm = (entry for entry in Path(data_dsm_path).iterdir() if entry.is_file())
    for item in files_in_data_dsm:
        tiff_dsm = rasterio.open(data_dsm_path + item.name)
        if bb_addr.isIn(BBox(tiff_dsm.bounds.left, tiff_dsm.bounds.bottom, tiff_dsm.bounds.right, tiff_dsm.bounds.top)):
            tiff_dtm = rasterio.open(data_dtm_path + item.name.replace("DSM", "DTM"))
            break

    # Crop tiff files
    crop_dsm_img, crop_dsm_transform = mask(dataset=tiff_dsm, shapes=polygon, crop=True, indexes=1)
    crop_dtm_img, crop_dtm_transform = mask(dataset=tiff_dtm, shapes=polygon, crop=True, indexes=1)
    crop_chm_img = crop_dsm_img - crop_dtm_img

    # Create dictionary
    # Add address & building's np array
    # Convert building np array to list
    result = {"Address": address, "BuildingNPArray": crop_chm_img.tolist()}

    return result
