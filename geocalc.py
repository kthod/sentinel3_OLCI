def geocalc():
    with open('locations2.txt', 'r') as f:
        lines = f.readlines()
        # split each line in pieces in order to store the coordinate values
        for i in lines:
            x = i.split()
            print(x)
            lat_deg = float(x[0])
            lat_m = float(x[1])
            lat_s = float(x[2])
            lon_deg = float(x[4])
            lon_m = float(x[5])
            lon_s = float(x[6])
            # calculate the decimal values
            lat =  float(lat_deg) + float(lat_m) / 60.0 + float(lat_s) / 3600.0
            lon =  float(lon_deg) + float(lon_m) / 60.0 + float(lon_s) / 3600.0
        return(lat, lon)
   
geocalc()

