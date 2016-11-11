from manytomos import ManyTomos
from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv

zone_plate_def = [['ZP_Z', Type.Float, None, ('Position of the zone plane'
                    ' motor')],
                  ['ZP_step', Type.Float, None, 'Zone plate z step'],
                  {'min' : 1, 'max' : 4 }]

energy_def = [['energy', Type.Float, None, 'Beam energy'],
              ['ZP_Z', Type.Float, None, 'Zone plate central position'],
              ['ZP_step', Type.Float, None, 'Zone plate z step'],
              {'min' : 1}]

regions_def = [['start', Type.Float, None, 'Theta start position'],
               ['end', Type.Float, None, 'Theta end position'],
               ['exp_time', Type.Float, None, 'Exposure time'],
               ['theta_step', Type.Integer, 1, 'Theta step'],
                {'min' : 1, 'max' : 5 }]

NAME = 0 # name position in sample
ZP_Z = 4 # ZP_Z position in sample

class manytomosbase:
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """

    def _verifySamples(self, samples, zp_limit_neg, zp_limit_pos):
        pass
        #for sample in samples:
            # check the zone_plate value



            #for counter, zone_plate in enumerate(sample[ZP_Z]):
            #    if zone_plate < zp_limit_neg or zone_plate > zp_limit_pos:
            #        msg = ("The sample {0} has the zone_plate #{1} out of"
            #               " range. The accepted range is from %s to"
            #               " %s um.") % (zp_limit_neg, zp_limit_pos)
            #        raise ValueError(msg.format(sample[NAME], counter))

    def run(self, samples, filename):
        try:
            zp_limit_neg = self.getEnv("ZP_Z_limit_neg")
        except UnknownEnv:
            zp_limit_neg = float("-Inf")
        try:
            zp_limit_pos = self.getEnv("ZP_Z_limit_pos")
        except UnknownEnv:
            zp_limit_pos = float("Inf")
        self._verifySamples(samples, zp_limit_neg, zp_limit_pos)
        manytomos = ManyTomos(samples, filename)
        manytomos.generate()


class manytomos(manytomosbase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['ZP_Z', energy_def, None, ('Beam energies and ZP_Z'
                                                 ' positions')],
                     ['sample_theta', regions_def, None, ('Regions of the'
                         ' theta motor')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                         ' for the flat field acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                         ' for the flat field acquisition')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]

class manytomosAvg(manytomosbase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                      ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['ZP_Z', zone_plate_def, None, ('Zone plates'
                         ' positions')],
                     ['sample_theta', regions_def, None, ('Regions of the'
                         ' theta motor')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                         ' for the flat field acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                         ' for the flat field acquisition')],
                    ['n_images', Type.Integer, 1, 'Number of images per saple']],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]

class manytomosE(manytomosbase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['ZP_Z', energy_def, None, ('Beam energies and ZP_Z'
                                                 ' positions')],
                     ['sample_theta', regions_def, None, ('Regions of the'
                         ' theta motor')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                         ' for the flat field acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                         ' for the flat field acquisition')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]
