def get_phases_from_point(year, crop, easting, northing, epsg, host, printout=False, get_query=False):
    '''
    get PHASE data from JKI DataCube 
    (more info: https://sf.julius-kuehn.de/openapi/phase/)
    
    PARAMETERS:
        year (str): year YYYY
        crop (str): choose one of the available crops on JKI DataCube
        easting (float): longitude coordinate
        northing (float): latitude coordinate
        epsg (int): defines coordinate reference system (CRS) of the input (easting and northing) and output coordinates
        host (str): the host adress of the Data Cube
        printout (bool(opt)): If True, some information will be printed about the success of request. Defaults to False.
        get_query (bool(opt)): If True, final WCS URL will be printed. Defaults to False.
        
    RETURNS:
        list_ (list): A list of the potential starting dates of the phenological stages.
    
    '''
    import requests # python package to handle REST query

    try:
        date = str(year)+'-01-01' # multiband layers of the whole year are always stored at the 1st of january
        
        # available crop types
        if crop == 'corn':
            rasdaman_layer = 'PHASE_215_Mais'
        elif crop == 'grassland':
            rasdaman_layer = 'PHASE_201_Dauergruenland'
        elif crop == 'winterwheat':
            rasdaman_layer = 'PHASE_202_Winterweizen'
        elif crop == 'winterrye':
            rasdaman_layer = 'PHASE_203_Winterroggen'
        elif crop == 'winterbarley':
            rasdaman_layer = 'PHASE_204_Wintergerste'
        elif crop == 'winterrape':
            rasdaman_layer = 'PHASE_205_Winterraps'
        elif crop == 'winteroat':
            rasdaman_layer = 'PHASE_208_Hafer'
        elif crop == 'fodderbeet':
            rasdaman_layer = 'PHASE_252_Futter_Ruebe'
        elif crop == 'sugarbeet':
            rasdaman_layer = 'PHASE_253_ZuckerRuebe'
        elif crop == 'apple':
            rasdaman_layer = 'PHASE_311_Apfel'
        else:
            print('wrong name for crop name!')
        
        service = '?&SERVICE=WCS'
        version = '&VERSION=2.0.1'
        request = '&REQUEST=GetCoverage'
        coverage_id = '&COVERAGEID=' + rasdaman_layer
        subset_time = '&SUBSET=ansi(\"' + date + '\")'
        subsetting_crs = '&subsettingCrs=http://ows.rasdaman.org/def/crs/EPSG/0/' + str(epsg)
        subset_lat = '&SUBSET=E(' + str(easting) + ',' + str(easting) + ')'
        subset_long = '&SUBSET=N('+ str(northing) + ',' + str(northing) + ')'
        output_crs = '&outputCrs=http://ows.rasdaman.org/def/crs/EPSG/0/' + str(epsg)
        encode_format = '&FORMAT=text/csv'
        
        query = host + service + version + request + coverage_id + subset_time + subsetting_crs + subset_lat + subset_long + output_crs + encode_format
        if get_query == True:
            print(query)

        # run query
        img = requests.get(query)
        
        # check if query successful
        if img.status_code == 200: # ststus code 200 means request wasd successful
            if printout==True:
                print('request was sucessfull! Request Status: {}'.format(img.status_code))
            # transform binary result to python-like list
            list_ =str(img.content).split('"')[1].split(' ') 
            for ind, i in enumerate(list_):
                list_[ind] = float(i)
            return list_
        else:
            if printout==True:
                print('something went wrong. Request was answered with request code: {}. URL: {}'.format(img.status_code, img.url))
            else:
                pass
    
    except Exception as e:
        print('something went wrong: {}'.format(e))
        

def get_tif_rasdaman(shp, endpoint, user, pw, layer = 'Nalamki', EPSG = 32632, rDate = '2020-04-01', band1='07_NIR10', band2='03_Red', band3='02_Green', printout=True , get_query=False):
    '''
    get PHASE data from JKI DataCube
    
    PARAMETERS:
        year (str): 
        
    RETURNS:
        list_ (list): 
    
    '''
    # import sys
    # sys.path.insert(1, '/path/to/crdentials.py')
    import credentials
    import geopandas as gpd
    import requests
    from requests.auth import HTTPBasicAuth
    
    polygon = gpd.read_file(shp).to_crs('EPSG:32632')
    polygon = str(polygon.geometry[0]).replace(' (', '(')

    # set WCS query parameters
    service = '?&SERVICE=WCS'
    version = '&VERSION=2.0.1'
    request = '&REQUEST=GetCoverage'
    coverage_id = '&COVERAGEID=' + layer # set name of RASDAMAN layer here
    subset_time = '&SUBSET=ansi(\"' + rDate + '\")'
    subsetting_crs = '&subsettingCrs=http://ows.rasdaman.org/def/crs/EPSG/0/' + str(EPSG) # your EPSG code
    clip = '&CLIP='+polygon
    output_crs = '&outputCrs=http://ows.rasdaman.org/def/crs/EPSG/0/' + str(EPSG) # your EPSG code
    encode_format = '&FORMAT=image/tiff'
    rangesubset = '&RANGESUBSET='+band1+','+band2+','+band3

    # build query string
    query = endpoint + service + version + request + coverage_id + subset_time + subsetting_crs + clip + output_crs + encode_format + rangesubset
    if get_query == True:
        print(query)

    # run WCS query
    img = requests.get(query, auth=HTTPBasicAuth(user, pw))
    # if printout == True:
    #     print('request status = {}'.format(img.status_code))
    
    try:
        if img.status_code != 200 and img.status_code != 404:
            if printout==True:
                print('bad request, trying again!')
            counter = 0
            while img.status_code != 200:
                img = requests.get(query, auth=HTTPBasicAuth(credentials.ras_user, credentials.ras_pw))
                counter += 1
            else:
                if printout==True:
                    print('now it worked after {} trails: {}'.format(counter, img.status_code))
        elif img.status_code == 404:
            if printout == True:
                print('request error {}! something does not work'.format(img.status_code))
        elif img.status_code == 200:
            if printout==True:
                print('request status successful (200)')
    except Exception as e:
        print('something went wrong: {}'.format(e))
        
    return img


def get_REGNIE_from_point(startdate, enddate, layer, easting, northing, epsg, user, passwd, host, printout=False, get_query=False):
    '''
    get PHASE data from JKI DataCube
    
    PARAMETERS:
        year (str): 
        
    RETURNS:
        list_ (list): 
    
    '''
    # import sys
    # sys.path.insert(1, '/path/to/crdentials.py')
    import credentials
    import requests
    from requests.auth import HTTPBasicAuth
    import requests
    from pyproj import Transformer
    try:
                
        if epsg == 4326:
            y=northing
            x=easting
        else:
            transformer = Transformer.from_crs("epsg:"+str(epsg), "epsg:4326")
            y,x = transformer.transform(easting,northing)


        url = host
        service = '?&SERVICE=WCS'
        version = '&VERSION=2.0.1'
        request = '&REQUEST=GetCoverage'
        coverage_id = '&COVERAGEID=' + layer
        subset_time = '&SUBSET=ansi("' + startdate + '","' + enddate + '")'
        subset_lat = '&SUBSET=Lon(' + str(float(x)) + ')'
        subset_long = '&SUBSET=Lat(' + str(float(y)) + ')'
        encode_format = '&FORMAT=text/csv'
        
        query = url + service + version + request + coverage_id + subset_time + subset_lat + subset_long + encode_format         
        if get_query == True:
            print(query)
        
        # run querry
        img = requests.get(query, auth=HTTPBasicAuth(user, passwd))
        
        if img.status_code == 200:
            if printout==True:
                print('request was sucessfull! Request Status: {}'.format(img.status_code))
            float_map = map(float, str(img.content).split("'")[1].split(','))
            float_list = list(float_map)
            
            if float_list[0] != -9999:
                return float_list
            elif float_list[0] == -9999:
                print('No precipitation data, returning a list of zeros...')
                return [0] * len(float_list)
        else:
            print('something went wrong. Request was answered with request code: {}. URL: {}'.format(img.status_code, img.url))
    
    except Exception as e:
        print(e)


def calculate_savi(img, valid_pixel_portion=50, noData=0):
    '''
    get PHASE data from JKI DataCube
    
    PARAMETERS:
        year (str): 
        
    RETURNS:
        list_ (list): 
    
    '''
    import rasterio
    import numpy as np
    import io
    try:
        with rasterio.open(io.BytesIO(img.content), nodata=noData) as src:
            nir = src.read(1) 
            red = src.read(2) 
            # band3 = src.read(3) 
            meta = src.meta
            meta.update({
                'dtype': rasterio.float32,
                'count': 1
            })
        
        vp = np.count_nonzero(nir !=0) / nir.size *100
        
        if nir.sum()>0 and vp > valid_pixel_portion:
            red = red/10000
            nir = nir/10000
            a = (nir-red)
            b = (nir+red+0.5)
            savi = np.divide(a, b, out=np.zeros_like(a), where=b!=0) *1.5
            savi[savi==0.0] = np.nan
            return [savi, meta]

    except Exception as e:
        print(e)

        
        
def get_map_coords(geometry):
    import geopandas as gpd
    
    if isinstance(geometry, list) and len(geometry) == 2:
        return [(geometry[1],geometry[0]),[]]
    
    elif isinstance(geometry, list) and len(geometry) > 2:
        lon = []
        lat = []
        for x,y in geometry:
            lon.append(x)
            lat.append(y)
        polygon = []
        for i in range(len(lon)):
            polygon.append((lat[i],lon[i]))
    
        return [(sum(lat)/len(lat), sum(lon)/len(lon)), polygon]
    
    elif (isinstance(geometry, str) and geometry.endswith('.geojson')) or (isinstance(geometry, str) and geometry.endswith('.shp')):
        location = gpd.read_file(geometry).to_crs('EPSG:4326')
        polygones = location['geometry']
        
        if len(polygones) == 1:
            coords = list(polygones[0].exterior.coords)
            center = (polygones[0].centroid.coords.xy[1][0], polygones[0].centroid.coords.xy[0][0])
            
            lon = []
            lat = []
            for x,y in coords:
                lon.append(x)
                lat.append(y)
            polygon = []
            for i in range(len(lon)):
                polygon.append((lat[i],lon[i]))
            
            return  [center, polygon]
        
        elif len(polygones) > 1:
            
            all_polygones = []
            
            for polygon in polygones:
                coords_ = list(polygon.exterior.coords)
                center = (polygon.centroid.coords.xy[1][0], polygon.centroid.coords.xy[0][0])

                lon = []
                lat = []
                for x,y in coords_:
                    lon.append(x)
                    lat.append(y)
                polygon_ = []
                for i in range(len(lon)):
                    polygon_.append((lat[i],lon[i]))
                
                all_polygones.append([center, polygon_])
                
            return  all_polygones
    
    else:
        print('Something went wrong with geometry input. Pleace insert point as list of tuples or polygone(s) as geojson file!')
            

def get_map(geometry, zoom=8):
    '''
    get PHASE data from JKI DataCube
    
    PARAMETERS:
        year (str): 
        
    RETURNS:
        list_ (list): 
    
    '''
    from ipyleaflet import Map, Marker, Polygon # interactive maps
        
    if len(get_map_coords(geometry)) == 2 and isinstance(get_map_coords(geometry)[0], tuple):
        center = get_map_coords(geometry)[0]  # lat , lon
        polygon = Polygon(locations=[get_map_coords(geometry)[1]], color="green", fill_color="green")
        m = Map(center=center, zoom=zoom)
        marker = Marker(location=center, draggable=True)
        m.add_layer(marker);
        m.add_layer(polygon);
        display(m)

    else:
        center = get_map_coords(geometry)[0][0]
        m = Map(center=center, zoom=zoom)

        get_map_coords(geometry)[1]
        for area in get_map_coords(geometry):
            marker = Marker(location=area[0], draggable=True)
            m.add_layer(marker);
            polygon = Polygon(locations=[area[1]], color="green", fill_color="green")
            m.add_layer(polygon);

        display(m)        

def get_all_dates(year):
    """This function returns a list of all days of the given year.

    Args:
        year (str): year YYYY

    Returns:
        list: List of days of teh given year
    """
    try:
        from datetime import date, timedelta

        start = date(int(year),1,1)
        end = date(int(year),12,31)


        delta = end - start

        days = []

        for i in range(delta.days + 1):
            day = start + timedelta(days=i)
            day  = day.strftime('%Y-%m-%d')
            days.append(day)

        
        
        return days
    except Exception as e:
        print('Error in get_all_dates function: {}'.format(e))
        
