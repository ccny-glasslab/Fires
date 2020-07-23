from datetime import datetime, timedelta
import itertools
from tempfile import NamedTemporaryFile

import boto3
import botocore
from botocore.config import Config

class GOESArchiveDownloader(object):
    def __init__(self):
        s3 = boto3.resource('s3', config=Config(signature_version=botocore.UNSIGNED, user_agent_extra='Resource'))
        self._bucket = s3.Bucket('noaa-goes17')

    def _get_iter(self, start, product):
        prod_prefix = str(product)
        start_marker = product.with_start_time(start)
        print(prod_prefix, start_marker)
        return self._bucket.objects.filter(Marker=start_marker, Prefix=str(product))
        
    def get_next(self, time, product):
        return next(iter(self._get_iter(time, product)))

    def get_range(self, start, end, product):
        end_key = product.with_start_time(end)

        # Get a list of files that have the proper prefix up to the hour
        return list(itertools.takewhile(lambda obj: obj.key <= end_key, self._get_iter(start, product)))

#ABI-L1b-RadC/2017/191/21/OR_ABI-L1b-RadC-M3C02_G16_s20171912142189_e20171912144562_c20171912144599.nc
class GOESProduct(object):
    def __init__(self, **kwargs):
        self.sector = 'conus'
        self.satellite = 'goes16'
        self.typ = 'ABI'
        self.channel = 1
        self.mode = 6
        self.datetime = datetime.utcnow()
        self.__dict__.update(kwargs)

    def __str__(self):
        env = 'OR'
        sat = {'goes16': 'G16', 'goes17': 'G17'}[self.satellite]

        if self.typ == 'ABI':
            sector = {'conus': 'C', 'meso1': 'M1', 'meso2': 'M2', 'full': 'F'}[self.sector]
            short_id = 'ABI-L1b-Rad{sector}'.format(sector=sector)
            prod_id = short_id + '-M{mode}C{channel:02d}'.format(mode=self.mode, channel=self.channel)
        elif self.typ == 'GLM':
            short_id = prod_id = 'GLM-L2-LCFA'
        else:
            raise ValueError('Unhandled data type: {}'.format(self.typ))
        return '{short_id}/{datetime:%Y/%j/%H}/{env}_{prodid}_{sat}'.format(short_id=short_id, datetime=self.datetime,
                                                                   env=env, prodid=prod_id, sat=sat)

    __repr__ = __str__

    def with_start_time(self, time):
        return str(self) + '_s{time:%Y%j%H%M%S}'.format(time=time)