from manytomos import ManyTomos
from sardana.macroserver.macro import Macro, Type

zone_plate_def = [['pos_zp_z', Type.Float, None, ('Position of the zone plane'
                    ' motor')], {'min' : 1, 'max' : 4 }]

regions_def = [['start', Type.Float, None, 'Theta start position'],
               ['end', Type.Float, None, 'Theta end position'],
               ['exp_time', Type.Float, None, 'Exposure time'],
               ['theta_step', Type.Integer, 1, 'Theta step'],
                {'min' : 1, 'max' : 3 }]


class manytomos(Macro):
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """
    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['ZP_Z', zone_plate_def, None, ('Zone plates'
                        'positions')],
                     ['sample_theta', regions_def, None, 'Regions of the theta motor'],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                        ' for the flat field acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                        ' for the flat field acquisition')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]

    def run(self, samples, filename):
        manytomos = ManyTomos(samples, filename)
        manytomos.generate()
