def get_phases_from_point(year, crop, easting, northing, host, epsg=32632, printout=False, get_query=False):
    '''
    get PHASE data from JKI DataCube 
    (more info: https://sf.julius-kuehn.de/openapi/phase/)
    
    PARAMETERS:
        year (str): year YYYY
        crop (str): choose one of the available crops on JKI DataCube
        easting (float): longitude coordinate
        northing (float): latitude coordinate
        host (str): the host adress of the Data Cube
        epsg (int): defines coordinate reference system (CRS) of the input (easting and northing) and output coordinates. Defaults to 32632.
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
        response = requests.get(query)
        
        
        # check if query successful
        if response.status_code == 200: # status code 200 means request wasd successful
            if printout==True:
                print('request was sucessfull! Request Status: {}'.format(response.status_code))
            # transform binary result to python-like list
            list_ =str(response.content).split('"')[1].split(' ') 
            for ind, i in enumerate(list_):
                list_[ind] = float(i)
            return list_
        elif response.status_code == 404: # status code 404 means bad request
            if printout==True:
                print('bad request! Request Status: {}'.format(response.status_code))
                print('response content: ', response.text)
            return response
        else:
            if printout==True:
                print('something went wrong. Request was answered with request code: {}. URL: {}'.format(response.status_code, response.url))
                print('response content: ', response.text)
            else:
                pass
            return response
        
    except Exception as e:
        print('something went wrong: {}'.format(e))
        