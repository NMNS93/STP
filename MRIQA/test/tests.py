import unittest
import uniformity
import sys
import logging
import pydicom

logger = logging.getLogger('test')

class UniformityTests(unittest.TestCase):
    def setUp(self):
        # Set test DICOM
        self.testfile = '/home/nana/Documents/MRI_QA/results/images_out/hd_uni_cor.dcm'
        self.dicom_image = pydicom.dcmread(self.testfile).pixel_array # Numpy pixelarray dtype uint16
        # Create uniformity object
        self.opts = uniformity.cli(sys.argv[2:])
        self.unif = uniformity.UniformityQA(self.opts.i, self.opts.c)

    def test_centralROI(self):
        print(self.unif.measure(self.dicom_image, 'hd_uni_cor_test'))
        self.assertEqual(self.opts.i, 'test_data/')

if __name__=="__main__":
    unittest.main()