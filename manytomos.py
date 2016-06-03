from manytomos import ManyTomos
from sardana.macroserver.macro import Macro, Type

zone_plate_def = [['pos_zp_z', Type.Float, None, ('Position of the zone plane'
                    ' motor')], {'min' : 1, 'max' : 4 }]

energy_def = [['energy', Type.Float, None, 'Beam energy'],
              ['ZP_Z', zone_plate_def, None, 'Zone plates positions'],
              {'min' : 1}]

regions_def = [['start', Type.Float, None, 'Theta start position'],
               ['end', Type.Float, None, 'Theta end position'],
               ['exp_time', Type.Float, None, 'Exposure time'],
               ['theta_step', Type.Integer, 1, 'Theta step'],
                {'min' : 1, 'max' : 3 }]

NAME = 0 # name position in sample
ZP_Z = 4 # ZP_Z position in sample

class manytomosbase:
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """

    def _verifySamples(self, samples):
        for sample in samples:
            # check the zone_plate value
            for counter, zone_plate in enumerate(sample[ZP_Z]):
                if zone_plate < -11275.0 or zone_plate > -11200.0:
                    msg = ("The sample {0} has the zone_plate #{1} out of"
                           " range. The accepted range is from -11275.0 to"
                           " -11200.0 um.")
                    raise ValueError(msg.format(sample[NAME], counter))

    def run(self, samples, filename):
#         self._verifySamples(samples)
        manytomos = ManyTomos(samples, filename)
        manytomos.generate()


class manytomos(manytomosbase, Macro):

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
                         ' for the flat field acquisition')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]


class manytomosE(manytomosbase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['energies', energy_def, None, 'Beam energies and ZP_Z'],
                     ['sample_theta', regions_def, None, ('Regions of the'
                         ' theta motor')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                         ' for the flat field acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                         ' for the flat field acquisition')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]
