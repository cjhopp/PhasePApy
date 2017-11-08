
# Pickerr Summary test
#
# Checks the following functions return values for 
# pickers ( AICDPicker, FBPicker, KTPicker )
#
#
#      -- threshold
#      -- uncertanity
#      -- pick_ident
#      -- polarity
#  


from obspy import read as obspy_read

from phasepapy.phasepicker.aicdpicker import AICDSummary
from phasepapy.phasepicker.fbpicker import FBSummary
from phasepapy.phasepicker.ktpicker import KTSummary  

# picker summary

def test_picker_summary(event, picker):

   mseed = event + '_short.mseed'
   st = obspy_read(mseed,details=True)
   print (st)
   picker_class = picker().__class__.__name__
   picker_index = picker_class.index('Picker')
   picker_summary_class = picker_class[:picker_index] + 'Summary'

   for s in st[:2]:
      print ("trace = ")
      print (s)
      print ("")

      picket_summary_str = picker_summary_class + \
                           '(' + 'picker(),' + 's)'
      picker_summary = eval(picket_summary_str)

      res = []; res_deriv = []	
      if 'AICD' in picker_class: 
          res, aic_deriv = picker_summary.cf._statistics()
          print ( "AICD Picker = ")
          print ( "AIC            = {}".format(res))
          print ( "AIC_deriv      = {}".format(res_deriv))
      if 'FB' in picker_class:
          res = picker_summary.cf._statistics()
          print ( "FB Picker = ")
          print ( "Each Band Stats = {}".format(res))
      if 'KT' in picker_class:
          res = picker_summary.cf._statistics()
          print ( "KT Picker = ")
          print ( "kurtosis stats  = {}".format(res))
      assert len(res) > 0
      print ("")
      
      threshold = picker_summary.threshold()
      print ( 'threshold = ',threshold )
      print ("")
      assert len(threshold) > 0
      print ("")

      uncertanity = picker_summary.uncertainty()
      print ( 'uncertainity = ', uncertanity )
      print ("")
      assert len(uncertanity) >= 0

      scnl, picks, trigger,snr = picker_summary.pick_ident()
      print ( 'scbl    = ',scnl )
      print ( 'picks   = ',picks)
      print ( 'trigger = ',trigger)
      print ( 'snr     = ',snr)
      print ("")
      assert len(picks) >= 0
      assert len(trigger) >= 0
      assert len(snr) >=0
  
      polarity = picker_summary.polarity()
      print ( 'Polarity    = ',polarity )
      print ("")
