# UseCase_PHASE

This repo shows, how to query the [JKI](https://www.julius-kuehn.de/en/) DataCube.

The code is part of the publication: coming soon...


## necessary Python3 packages

* datetime, io, requests (standard packages)
* numpy, matplotlib
* geopandas, rasterio
* xmltodict, tqdm, ipyleaflet

## files

1. `UseCase_PHASE_DataCube.ipynb` -> Jupyter Notebook and main file for demonstration
2. `func_datacube_PHASE.py` -> main function to query PHASE data cube
3. `func_datacube_S2.py`  -> main function to query Sentienel-2 data cube (restricted access)
4. `func_datacube_DWD.py`  -> main function to query precipitation data cube
5. `func_misc.py` -> additional functions used in the notebook

## credentials

If you have access to restricted data cubes, then it is recommended to creade a `credentials.py` as follows:

create a file: `credentials.py`

file content:

```
ras_user = 'your user name'
ras_pw = 'your password'
ras_host = 'host ip'

ras_cde_user = 'your user name'
ras_cde_pw = 'your password'
ras_cde_host = 'host ip'
```

Add this lines to your code:
```python
# in case, your credentials.py os in another directory, uncomment the folloing two lines
# import sys
# sys.path.insert(1, '/path/to/crdentials.py')

import credentials # ---> this is the credentials.py

print(credentials.ras_user)

Output:
    your user name
``` 
    
    
    

This line of text is not indented. It ends the code block and starts a new paragraph.