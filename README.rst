TESS Follow-up Tools
====================

A few scripts to help with high contrast imaging follow up of TESS objects of interest (TOIs). Currently just a script that helps makes target lists and a guide to NIRC2 operations. Augmentable for anyone doing follow up of TESS targets.

Script Maker Usage::

  from starlist_utils import Starlist
  import pandas as pd
  tess_targets = pd.read_csv(<result_from exofop_search>.csv,comment='#')
  
  starlist = Starlist(targets=tess_targets)
  
  starlist.add_target_exofop(toi=509.01,comment='additional target')
  
  starlist.make_starlist(obs_date='6-10-23',save=True)
  
The scriptmaker is able to pull information on targets from ExoFOP and directly from the TIC in addition to explicitly asking for information about targets that do not have a TOI designation. One can also remove targets from the list and export a target list in Keck-readable form.
  
