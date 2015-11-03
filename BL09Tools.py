import PyTango
import time
import taurus
from sardana.macroserver.macro import *
import fitlib
#import matplotlib.pyplot as plt



@macro()
def isblready(self):
    DevEPS = taurus.Device('bl09/ct/eps-plc-01')
    if DevEPS.BL_READY:
        self.output('BL09 beamline is ready')
    else:
        self.output('BL09 beamline is NOT ready')


@macro([["action", Type.String, 'status', "status, open, close"]])
def mvfe(self,action):
    DevEPS = taurus.Device('bl09/ct/eps-plc-01')
    dicto={0:'close',1:'open'}
    action = action.upper()
    if action not in ['CLOSE', 'OPEN','STATUS', '']:
        self.error('mode should be one of: open, close, status ')
        return

    elif action == 'OPEN' :
        try:
            DevEPS['OPEN_FE'] = True
        except:
            self.warning('Cannot open the FE')
    
    elif action == 'CLOSE' :
        try:
            DevEPS['CLOSE_FE'] = True
        except:
            self.warning('Cannot close the FE')
        
    self.output('Checking status...')
    time.sleep(5)
    self.output('FE is %s' % dicto[DevEPS["fe_open"].value])



@macro()
def StatusTXMValve(self):
    for DevName in ['BL09/EH/PNV-05']:
    
        DevState = taurus.Device(DevName).state()
        self.output('Status of TXM Valve is %s' % (DevState))


@macro()
def OpenTXMValve(self):
    for DevName in ['BL09/EH/PNV-05']:
    
        self.output('Opening TXM Valve: BL09/EH/PNV-05')
        try:
            taurus.Device(DevName).Open()
            time.sleep(1)
        except:
            self.warning('Could not open TXM Valve: BL09/EH/PNV-05')


@macro()
def CloseTXMValve(self):
    for DevName in ['BL09/EH/PNV-05']:
    
        self.output('Closing TXM Valve: BL09/EH/PNV-05')
        try:
            taurus.Device(DevName).Close()
            time.sleep(1)
        except:
            self.warning('Could not close TXM Valve: BL09/EH/PNV-05')



@macro()
def ValvesStatus(self):
    for DevName in ['FE09/VC/PNV-TRU-01',
                    'BL09/OH/PNV-01',
                    'BL09/OH/PNV-02',
                    'BL09/OH/PNV-03',
                    'BL09/OH/PNV-04',
                    'BL09/EH/PNV-01',
                    'BL09/EH/PNV-02',
                    'BL09/EH/PNV-03',
                    'BL09/EH/PNV-04',
                    'BL09/EH/PNV-05']:
    
        DevState = taurus.Device(DevName).state()
        self.output('Valve %s is %s' % (DevName,DevState))


@macro()
def OpenValves(self):

    DevName = ['FE09/VC/PNV-TRU-01',
               'BL09/OH/PNV-01',
               'BL09/OH/PNV-02',
               'BL09/OH/PNV-03',
               'BL09/OH/PNV-04',
               'BL09/EH/PNV-01',
               'BL09/EH/PNV-02',
               'BL09/EH/PNV-03',
               'BL09/EH/PNV-04']
   
    DevName.reverse() 
    for a in DevName:    
        self.output('Opening %s ...' % a )
        try:
            taurus.Device(a).Open()
            time.sleep(1)
        except:
            self.warning('Could not open %s' % a )


@macro()
def CloseValves(self):
    for DevName in ['FE09/VC/PNV-TRU-01',
                    'BL09/OH/PNV-01',
                    'BL09/OH/PNV-02',
                    'BL09/OH/PNV-03',
                    'BL09/OH/PNV-04',
                    'BL09/EH/PNV-01',
                    'BL09/EH/PNV-02',
                    'BL09/EH/PNV-03',
                    'BL09/EH/PNV-04',
                    'BL09/EH/PNV-05']:
    
        self.output('Closing %s ...' % DevName )
        try:
            taurus.Device(DevName).Close()
            time.sleep(1)
        except:
            self.warning('Could not close %s' % DevName )



class loopscan(Macro):
    param_def = [["motor", Type.Moveable, None, "Motor to scan"],
                 ["nrofpoints", Type.Integer, None, "Number of points for iteration"],
                 ["numiters", Type.Integer, None, "Number of iterations"],
                 ["timesleep", Type.Float, None, "Time sleep"]]

    def run(self, motor, nrofpoints, numiters, timesleep):
        for i in range(numiters):
            self.dscan(motor, -0.025, 0.025, nrofpoints, 1)
            #self.info('scan')
            time.sleep(timesleep)

        self.mvfe('close')
        #self.info('FE close, sleep, open')
        time.sleep(3600)
        self.mvfe('open')

        for i in range(numiters):
            self.dscan(motor, -0.025, 0.025, nrofpoints, 1)
            #self.info('scan')
            time.sleep(timesleep)

        self.mvfe('close')
        #self.info('FE close, sleep, open')
        time.sleep(3600)
        self.mvfe('open')

        for i in range(numiters):
            self.dscan(motor, -0.025, 0.025, nrofpoints, 1)
            #self.info('scan')
            time.sleep(timesleep)

        self.feauto('1')

        #self.mvfe('close')
        #self.CloseValves()

#*******************************************************************************
#               Macros to aling the mirrors.
#*******************************************************************************

class M_mesh(object):
    m1_pitch_name = 'm1_pitch'
    m2_pitch_name = 'm2_pitch'
    m1_trans_name = 'm1_z'
    m2_trans_name = 'm2_x'

    def run_scan(self, mirror, step_pitch, step_trans, st_trans_dscan, 
                 end_trans_dscan, intervals, int_time, repetitions):
        """
        :param mirror[str]: m1 or m2, to select which mirror will use it
        :param step_pitch: step between scans in pitch
        :param step_trans: step between scans in translation
        :param st_trans_dscan: start position to use in dscan for translation
        :param end_trans_dscan: end position to use in dscan for translation
        :param intervals: number of interval in the dscan
        :param int_time: integration time
        :param repetitions: number of scans
        :return:
        """

        try:
            chn = self.getEnv('MMeshChn')
        except Exception as e:
            msg = 'You must declare the MMeshChn in the environment with ' + \
                'the name of the channel in the measurement group to ' + \
                'to calculate the results.'
            raise RuntimeError(msg)

        # TODO verify the channel in the MntGrp

        # Select motors between mirrors (1 or 2)
        if mirror.lower() == 'm1':
            m_pitch_name = self.m1_pitch_name
            m_trans_name = self.m1_trans_name
        elif mirror.lower() == 'm2':
            m_pitch_name = self.m2_pitch_name
            m_trans_name = self.m2_trans_name
        else:
            msg = 'Mirror should be m1 or m2. Passed value: %' % mirror
            raise ValueError(msg)

        self.m_pitch = self.getMoveable(m_pitch_name)
        self.m_trans = self.getMoveable(m_trans_name)
        self.fit_obj = fitlib.GaussianFit()
        self.dscan_macro, _ = self.createMacro('dscan', self.m_trans,
                                               st_trans_dscan, end_trans_dscan,
                                               intervals, int_time)

        results = [['ScanID', m_pitch_name, m_trans_name, 'Intensity', 'FWHM']]

        try:
            for i in range(repetitions):
                if i == 0:
                    first_scan_id = res[0]     
                res = self.get_result('umvr', m_trans_name, chn, step_pitch,
                                      step_trans)
                results.append(res)
            last_scan_id = res[0]

        except Exception as e:
            self.error('There was an error: %s' % e)

        finally:
            # Save and show results for each scan
            filename = 'fit_%s_%s.txt' % (first_scan_id, last_scan_id)
            path = self.getEnv('ScanDir')
            file_fullname = '%s/%s' %(path, filename)
            with open(file_fullname, 'w') as f:
                self.info('Saving report in: \n%s' % file_fullname)
                for r in results:
                    line = ''
                    for i in r:
                        line += '%s/t' % i
                    self.output(line)
                    f.write(line)

    def get_result(self, x_name, y_name, step_pitch, step_trans):
        st_scan_id = self.getEnv('ScanID')
        # Move the m#_pitch to scan start position 
        cmd_macro = 'umvr %s %s' % (self.m_pitch.getName(), step_pitch)
        self.execMacro(cmd_macro)
        # Move the m#_trans to scan start position 
        cmd_macro = 'umvr %s %s' % (self.m_trans.getName(), step_trans)
        self.execMacro(cmd_macro)

        pitch_pos = self.m_pitch.read_attribute('Position').value

        self.runMacro(self.dscan_macro)
        x_data = []
        y_data = []
        for data in self.dscan_macro.data:
            x_data.append(data[x_name])
            y_data.append(data[y_name])
        offset, slope, height, center_x, sigma, fwhm = self.fit_obj.fit(x_data,
                                                                        y_data)
        result = [st_scan_id, pitch_pos, center_x, height, fwhm]
        return result


class M1_mesh(Macro, M_mesh):
    def run(self):
        self.execMacro('umvr m1_pitch 0.015')
        self.execMacro('umvr m1_z -0.240')
        self.run_scan('m1', -0.005, 0.08, -0.14, 0.10, 90, 1, 3)


class M1_mesh2(Macro, M_mesh):
    def run(self):
        self.execMacro('umv m1_pitch -0.055')
        self.execMacro('umv m1_z 0.697')
        self.run_scan('m1', -0.005, 0.08, -0.14, 0.10, 90, 1, 3)


class M2_mesh(Macro, M_mesh):
    def run(self):
        self.execMacro('umvr m2_pitch 0.010')
        self.execMacro('umvr m2_x -0.32')
        self.run_scan('m2', -0.005, 0.16, -0.32, 0.32, 60, 0.5, 3)


class M2_mesh2(Macro, M_mesh):
    def run(self):
        self.execMacro('umv m2_pitch -0.035')
        self.execMacro('umv m2_x 2.217')
        self.run_scan('m2', -0.005, 0.16, -0.32, 0.32, 60, 0.5, 3)


@macro()
def pencil_beam(self): #THIS MACRO SHOULD BE USED WITH SHUTTER OUT & E OFFSET=18 eV (HOPG)
    self.execMacro('senv ActiveMntGrp flux_albaem')#set measurement group
    #ch4_emetrange_ch4_attr = PyTango.AttributeProxy("bl09/di/albaem-01/range_ch4")
    #ch3_emetrange_ch3_attr = PyTango.AttributeProxy("bl09/di/albaem-01/range_ch3")
    #ch3_emetinverted_ch3_attr = PyTango.AttributeProxy("bl09/di/albaem-01/dInversion_ch3")

    self.execMacro('umv jj_d -2.0') #set gap of jj
    self.execMacro('umv jj_u 0.0')
    #self.execMacro('umv __DO_NOT_TOUCH_motcalib 68.5') #diag2 motor at Fe

    #self.execMacro('umv xs_l 0.0')
    #ch4_emetrange_ch4_attr.write('100 pA') #set range of ALBA em
    self.execMacro('umv EnergyCff2.25 768')
    self.execMacro('ascan EnergyCff2.25 772 788 160 1')
    self.execMacro('umv EnergyCff2.25 768')
    self.execMacro('ascan EnergyCff2.25 772 788 160 1')
    self.execMacro('umv EnergyCff2.25 768')
    #self.execMacro('ascan EnergyCff2.25 635 650 150 1')
    #self.execMacro('umv EnergyCff2.25 735')
    #self.execMacro('umv EnergyCff2.25 698')
    for i in range(8):
        for j in range(20):
            self.execMacro('umvr jj_offset 0.025')
        self.execMacro('ascan EnergyCff2.25 772 788 160 1.0')
        self.execMacro('umv EnergyCff2.25 768')
        #self.execMacro('umv EnergyCff2.25 698')
        self.execMacro('ascan EnergyCff2.25 772 788 160 1.0')
        self.execMacro('umv EnergyCff2.25 768')
        #self.execMacro('ascan EnergyCff2.25 740 760 100 1.0')
        #self.execMacro('umv EnergyCff2.25 735')
        #self.execMacro('umv EnergyCff2.25 698')


    # self.execMacro('umv jj_offset -2.5')
    # self.execMacro('umv xs_l 0')
    # self.execMacro('ascan EnergyCff2.25 535 555 200 1')
    # self.execMacro('umv EnergyCff2.25 530')
    # self.execMacro('ascan EnergyCff2.25 535 555 200 1.0')
    # self.execMacro('umv EnergyCff2.25 530')
    # for i in range(14):
    #     self.execMacro('umvr jj_offset 0.5')
    #     self.execMacro('ascan EnergyCff2.25 535 555 200 1.0')
    #     self.execMacro('umv EnergyCff2.25 530')
    #     self.execMacro('ascan EnergyCff2.25 535 555 200 1.0')
    #     self.execMacro('umv EnergyCff2.25 530')


    # self.execMacro('umv jj_offset -1.0')
    # self.execMacro('umv xs_l 0')
    # self.execMacro('ascan EnergyCff2.25 280 290 100 1')
    # self.execMacro('umv EnergyCff2.25 275')
    # self.execMacro('ascan EnergyCff2.25 280 290 100 1.0')
    # self.execMacro('umv EnergyCff2.25 275')
    # for i in range(10):
    #     self.execMacro('umvr jj_offset 0.5')
    #     self.execMacro('ascan EnergyCff2.25 280 290 100 1.0')
    #     self.execMacro('umv EnergyCff2.25 275')
    #     self.execMacro('ascan EnergyCff2.25 280 290 100 1.0')
    #     self.execMacro('umv EnergyCff2.25 275')


    # self.execMacro('umv jj_offset -1.0')
    # self.execMacro('umv xs_l 0')
    # self.execMacro('ascan EnergyCff2.25 280 290 100 1')
    # self.execMacro('umv EnergyCff2.25 275')
    # self.execMacro('ascan EnergyCff2.25 280 290 100 1.0')
    # self.execMacro('umv EnergyCff2.25 275')
    # for i in range(10):
    #     self.execMacro('umvr jj_offset 0.5')
    #     self.execMacro('ascan EnergyCff2.25 280 290 100 1.0')
    #     self.execMacro('umv EnergyCff2.25 275')
    #     self.execMacro('ascan EnergyCff2.25 280 290 100 1.0')
    #     self.execMacro('umv EnergyCff2.25 275')

    # self.execMacro('umv jj_offset -1.5')
    # self.execMacro('umv __DO_NOT_TOUCH_motcalib 82') #diag2 motor at photodiode
    # ch3_emetrange_ch3_attr.write('1uA')#set range of ALBA em
    # ch3_emetinverted_ch3_attr.write('YES')#set range of ALBA em
    #
    # self.execMacro('umv xs_l -9')BL09Tools.py
    # self.execMacro('umv EnergyCff2.25 698')
    # self.execMacro('ascan EnergyCff2.25 700 730 300 1')
    # self.execMacro('umv EnergyCff2.25 698')
    # self.execMacro('ascan EnergyCff2.25 700 730 300 1.0')
    # self.execMacro('umv EnergyCff2.25 698')
    # for i in range(4):
    #     self.execMacro('umvr jj_offset 1')
    #     self.execMacro('ascan EnergyCff2.25 700 730 300 1.0')
    #     self.execMacro('umv EnergyCff2.25 698')
    #     self.execMacro('ascan EnergyCff2.25 700 730 300 1.0')
    #     self.execMacro('umv EnergyCff2.25 698')


    #        self.execMacro('umv jj_offset -1.5')
    #        self.execMacro('umv xs_l 0')
    #        self.execMacro('ascan EnergyCff2.25 278 298 200 1')
    #        self.execMacro('umv EnergyCff2.25 277')
    #        self.execMacro('ascan EnergyCff2.25 278 298 200 1.0')
    #        self.execMacro('umv EnergyCff2.25 277')
    #        for i in range(4):
    #                self.execMacro('umvr jj_offset 1')
    #                self.execMacro('ascan EnergyCff2.25 278 298 200 1.0')
    #                self.execMacro('umv EnergyCff2.25 277')
    #                self.execMacro('ascan EnergyCff2.25 278 298 200 1.0')
    #                self.execMacro('umv EnergyCff2.25 277')


    #        self.execMacro('umv jj_offset -1.5')
    #        self.execMacro('umv xs_l 9')
    #        self.execMacro('ascan EnergyCff2.25 278 298 200 1')
    #        self.execMacro('umv EnergyCff2.25 277')
    #        self.execMacro('ascan EnergyCff2.25 278 298 200 1.0')
    #        self.execMacro('umv EnergyCff2.25 277')
    #        for i in range(4):
    #                self.execMacro('umvr jj_offset 1')
    #                self.execMacro('ascan EnergyCff2.25 278 298 200 1.0')
    #                self.execMacro('umv EnergyCff2.25 277')
    #                self.execMacro('ascan EnergyCff2.25 278 298 200 1.0')
    #                self.execMacro('umv EnergyCff2.25 277')

    #self.execMacro('umv __DO_NOT_TOUCH_motcalib 5')
    #self.execMacro('umv jj_d -8')
    #self.execMacro('umv jj_u 8')
    #self.execMacro('umv xs_l 0')

@macro()
def M1_pencil_beam(self):
    self.execMacro('umv fe_v_offset 0')
    self.execMacro('umv fe_v_gap 2.0') #set gap of fe_v
    self.execMacro('umv fe_v_offset -4')
    self.execMacro('dscan m1_z -0.1 0.1 100 1')
    self.execMacro('dscan m1_z -0.1 0.1 100 1')
    for i in range(9):
        self.execMacro('umvr fe_v_offset 1')
        self.execMacro('dscan m1_z -0.1 0.1 100 1')
        self.execMacro('dscan m1_z -0.1 0.1 100 1')
    self.execMacro('umv fe_v_offset 0')
    self.execMacro('umv fe_v_gap 12')

@macro()
def series_specular_pencil_beam(self):
    self.execMacro('umv m4_pitch -0.510')
    #self.execMacro('umvr m4_pitch -0.005')
    self.execMacro('umv m4_z -2.431')
    self.execMacro('umv gr_pitch 20.993')
    self.execMacro('dscan xs_v -0.065 0.065 130 1')
    for i in range(4):
        #self.execMacro('specular_pencil_beam')
        self.execMacro('umvr m4_pitch -0.005')
        self.execMacro('umvr m4_z -0.076')
        self.execMacro('umvr gr_pitch -0.002')
        self.execMacro('dscan xs_v -0.065 0.065 130 1')

    #self.execMacro('umv jj_d -8')
    #self.execMacro('umv jj_u 8')
        
@macro()
def specular_pencil_beam(self):
        
    self.execMacro('umv jj_d -3.0') #set gap of jj
    self.execMacro('umv jj_u -1.0')
    self.execMacro('dscan xs_v -0.05 0.05 100 1')
    #self.execMacro('dscan xs_v -0.05 0.05 100 1')
    for i in range(7):
        for j in range(40):
            self.execMacro('umvr jj_offset 0.05')
        self.execMacro('dscan xs_v -0.05 0.05 100 1')
        #self.execMacro('dscan xs_v -0.05 0.05 100 1')
                
           


@macro()
def topup_effect(self):
    
    self.execMacro('umv jj_d 1.0') #set gap of jj
    self.execMacro('umv jj_u 3.0')
    self.execMacro('umv __DO_NOT_TOUCH_motcalib 68.5') #diag2 motor at Fe
    for i in range(30):
        self.execMacro('umv EnergyCff2.25 690')
        self.execMacro('ascan EnergyCff2.25 695 730 175 1.0')

    self.execMacro('umv __DO_NOT_TOUCH_motcalib 5')
    self.execMacro('umv jj_d -10')
    self.execMacro('umv jj_u 10')

#@macro()
#def gas_cell(self):

#	for i in range(7):
#		self.execMacro('umvr xs_l 1')
#		self.execMacro('umv EnergyCff2.25 401')
#		self.execMacro('ascan EnergyCff2.25 401.5 404.0 250 1.0')


