from nose.tools import assert_true, assert_equal, raises
import os
import numpy as np
from pathlib import Path
import tempfile
import datajoint as dj
from . import PREFIX, CONN_INFO

schema = dj.Schema(PREFIX + '_update1', connection=dj.conn(**CONN_INFO))

dj.config['stores']['update1_store'] = dict(
    stage=tempfile.mkdtemp(),
    protocol='file',
    location=tempfile.mkdtemp())

scratch_folder = tempfile.mkdtemp()

@schema
class Thing(dj.Manual):
    definition = """
    thing   :   int    
    ---
    number=0  : int   
    frac    : float
    picture = null    :   attach@update1_store
    params = null  : longblob 
    timestamp = CURRENT_TIMESTAMP :   datetime
    """


def test_update1():
    """test normal updates"""

    # CHECK 1
    key = dict(thing=1)
    Thing.insert1(dict(key, frac=0.5))
    check1 = Thing.fetch1()

    # CHECK 2 -- some updates
    Thing.update1(dict(key, number=3, frac=30))
    attach_file = Path(scratch_folder, 'attach1.dat')
    buffer1 = os.urandom(100)
    attach_file.write_bytes(buffer1)
    Thing.update1(dict(key, picture=attach_file))
    Thing.update1(dict(key, timestamp="2020-01-01 10:00:00"))
    check2 = Thing.fetch1(download_path=scratch_folder)
    buffer2 = Path(check2['picture']).read_bytes()

    # CHECK 3
    Thing.update1(dict(key, timestamp=None, picture=None, params=np.random.randn(3, 3)))  # rest to default
    check3 = Thing.fetch1()

    assert_true(check1['number'] == 0 and check1['picture'] is None and check1['params'] is None)
    assert_true(check2['number'] == 0 and check1['picture'] is None and check2['params'] is None)
    assert_true(check3['timestamp'] > check2['timestamp'])
    assert_equal(buffer1, buffer2)

    print(check1, check2)







