from flask import Flask, request
import numpy as np
import plotly.graph_objects as go
from tools.PolygonRequest import *
from db.Building import Building
import time

app = Flask(__name__)
BuildingObject = Building('buildings', 'postgres', '127.0.0.1', 'psw')
BuildingObject.create_tb()


@app.route('/', methods=['GET', 'POST'])
def route():
    if request.method == 'POST':  # this block is only entered when the form is submitted
        start = time.time()
        address = request.form.get('address')
        # return render_template('index.html', address=address)
        # return '''<h1>The address value is: {}</h1>'''.format(address)
        # Tiff files path
        data_dsm_path = "/home/agcia/3DHouse/Data/DSM/GeoTIFF/"
        data_dtm_path = "/home/agcia/3DHouse/Data/DTM/GeoTIFF/"

        # Request the formatted address
        # Raise an error msg if the address doesn't exist
        try:

            req = requests.get(f"http://loc.geopunt.be/geolocation/location?q={address}&c=1").json()

            formattedaddress = req["LocationResult"][0]["FormattedAddress"]
            result = BuildingObject.select_db(formattedaddress)

            if not result:

                result = requests.get(f"http://127.0.0.0:5000/getnparray/?address={formattedaddress}").json()
                BuildingObject.insert_db(result)

            end = time.time()
            print("--- Run Time : %s seconds ---" % (end - start))
        except IndexError:
            print(address, " :Address doesn't exist")
            return '''<h1>Address doesn't exist</h1>'''
        except Exception as e:
            print("Something else went wrong: "+str(e))
            exit()

        crop_chm_img = result["BuildingNPArray"]
        #print(crop_chm_img)
        # 3D plot
        # fliplr: Reverse the order of elements in 'crop_chm_img' array horizontally
        fig = go.Figure(data=go.Surface(z=np.fliplr(crop_chm_img), colorscale='plotly3'))
        fig.update_layout(scene_aspectmode='manual', scene_aspectratio=dict(x=1, y=1, z=0.5))
        fig.update_layout(
            title={
                'text': "3D Building at " + formattedaddress,
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            title_font_color="green")

        fig.show()

    return '''<form method="POST">
                  Please enter an address: <input type="text" name="address"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
