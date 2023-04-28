def get_coverages(host, user='', pw='', use_credentials=False):
    '''
    get a list of all available data cubes
    
    PARAMETERS:
        host (str): host adress of data cube service
        user (str): credentials username
        pw (str): credentials password
        use_credentials (bool(opt)): If True: personal credentials for datacube service will be used. Defaults to False.
        
    RETURNS:
        coverages (list): list of all available data cubes on given host
    '''
    import requests
    import xmltodict
    from requests.auth import HTTPBasicAuth
    
    query = host + '?SERVICE=WCS&version=2.0.1&request=GetCapabilities'
    if use_credentials == True:
        response = requests.get(query, auth=HTTPBasicAuth(user,pw))
    else:
        response = requests.get(query)
    dict_data = xmltodict.parse(response.content)
    
    coverages = []
    for i in dict_data['wcs:Capabilities']['wcs:Contents']['wcs:CoverageSummary']:
        coverages.append(i['wcs:CoverageId'])
    return coverages

def get_metadata_from_datacube(layer, host, user='', pw='', use_credentials=False):
    '''
    get a list of all available data cubes
    
    PARAMETERS:
        layer (str): coverage name of the data cube
        host (str): host adress of data cube service
        user (str): credentials username
        pw (str): credentials password
        use_credentials (bool(opt)): If True: personal credentials for datacube service will be used. Defaults to False.
        
    RETURNS:
         metadata (dict): list of all available data cubes on given host
    '''

    import requests
    import xmltodict
    from requests.auth import HTTPBasicAuth
    
    query = host+'?&SERVICE=WCS&VERSION=2.0.1&REQUEST=DescribeCoverage&COVERAGEID='+layer
    
    if use_credentials == True:
        response = requests.get(query, auth=HTTPBasicAuth(user,pw))
    else:
        response = requests.get(query)
    
    metadata = xmltodict.parse(response.content)
    
    return  metadata

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
        
