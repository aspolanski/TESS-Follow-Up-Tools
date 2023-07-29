#!/usr/bin/env python3

import pandas as pd
import numpy as np
from astroquery.mast import Catalogs


class Starlist(object):
    def __init__(self,targets=None):
        
        """
        Initialize Starlist object.
        targets - A Pandas dataframe of TOIs from ExoFOP search with columns:
        TOI: TESS Object of INterest number
        TIC: TESS Input Catalog identifier
        RA: RA of target
        Dec: Dec of target
        SG3 priority
        vmag: Host V mag
        kmag: Host K mag
        prad: Planet radius
        teff: Host effective tmeperature
        """

        if targets is not None:
            if not isinstance(targets, pd.DataFrame):
                print("Targets must be a Pandas dataframe")
                exit()
            else:
                self.targets = targets
                self.targets['comment'] = ['']*len(self.targets.index)
        

        print("Loading TOI catalog...")
        exofop = pd.read_csv("https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi&output=csv",delimiter=',')
        self.exofop = exofop
        print("Complete.")

    def add_target(self):

        """
        Function to manually add a target (e.g not a TOI).
        """
        
        target = input("Name of target (no spaces)\n")
        ra = input("RA (colon separated)\n")
        dec = input("Dec (colon separated)\n")
        vmag = input(f"V mag of {target})\n")
        kmag = input(f"K mag of {target})\n")
        steff = input(f"Effective Temperature of {target})\n")
        comment = input(f"Provide additional comments\n")

        new = pd.DataFrame(columns=['TIC ID','TOI','RA','Dec','V mag','K mag','SG3 Priority','Planet Radius (TOI)','Teff (TOI)','comment'])

        new = new.append({'TOI':target,
            'TIC ID':target,
            'RA':ra,
            'Dec':dec,
            'V mag':vmag,
            'K mag':kmag,
            'SG3 Priority':0,
            'Planet Radius (TOI)':0,
            'Teff (TOI)':steff,
            'comment':comment},ignore_index=True)

        self.targets = pd.concat([self.targets,new]).reset_index(drop=True)


    def add_target_exofop(self, toi=None, tic=None,comment=None): 

        """
        Function to add a target to your starlist. Takes either TOI or TIC ID as input.
        Searches all current TOIs and obtains Host parameters from TIC.
        """
    
        new = pd.DataFrame(columns=['TIC ID','TOI','RA','Dec','V mag','K mag','SG3 Priority','Planet Radius (TOI)','Teff (TOI)','comment'])

        if not toi:
            x = self.exofop[self.exofop['TIC ID'] == tic]
            targ_name = tic

        elif toi:
            x = self.exofop[self.exofop['TOI'] == toi]
            targ_name = toi
        else:
            print("Provide either TOI or TIC.\n")
            exit()

        if not comment:
            comment = ''

        tic_query = Catalogs.query_object(f"TIC {x['TIC ID'].item()}", radius=0.00013, catalog="TIC").to_pandas().iloc[0]

        new = pd.concat([new,pd.DataFrame({'TOI':x.TOI.item(),
            'TIC ID':x['TIC ID'].item(),
            'RA':x.RA.item(),
            'Dec':x.Dec.item(),
            'V mag':tic_query['Vmag'].item(),
            'K mag':tic_query['Kmag'].item(),
            'SG3 Priority':x['SG3'].item(),
            'Planet Radius (TOI)':x['Planet Radius (R_Earth)'].item(),
            'Teff (TOI)':x['Stellar Eff Temp (K)'].item(),
            'comment':comment},index=[0])],ignore_index=True)

        self.targets = pd.concat([self.targets,new],ignore_index=True).reset_index(drop=True)

    def remove_target(self,toi=None):

        """
        Function to remove target from starlist based on TOI.
        """

        if not toi:
            print("Provide the name of target to remove.\n")
            exit()

        else:
            self.targets = self.targets[self.targets['TOI'] != toi].reset_index(drop=True)

    def add_comment(self,toi=None):        

        """
        Function to add comment to existing line in starlist.
        """


        if not toi:
            print("Provide the name of target to remove.\n")
            exit()
        else:
            comment = input(f"Provide comment for {toi}\n")

            row = self.targets[self.targets.TOI == toi].index
            col = self.targets.columns.get_loc('comment')
            self.targets.iloc[row,col] = comment

    def make_starlist(self,obs_date,save=False):
        
        """
        Function to create starlist in a Keck/Palomar readable form.
        """

        df = self.targets #make copy of working DataFrame

        df.RA = df.RA.str.replace(":"," ")
        df.Dec = df.Dec.str.replace(":"," ")

        #deal with stars with only TIC ID's

        tics = df[df.TOI.isna()]
        tics.TOI = "TIC" + tics['TIC ID'].astype(str)+ "          "
        df = df[~df.TOI.isna()]

        
        df.TOI = "TOI"+df.TOI.astype(str).str.split(".").str[0] + "          " #reformat name

        #df=df.append(tics) #add back in the TIC only targets
        df = pd.concat([df,tics],ignore_index=True)

        f = pd.DataFrame({'Target':df.TOI,'RA':df.RA,'Dec':df.Dec,'Equinox':['2000.0']*len(df.index)}) #create new dataframe

        #compile comment information
        f['comment'] = "vmag="+df['V mag'].astype(str) + " kmag="+df['K mag'].astype(str) + " lgs=0" + " SG3=" +df['SG3 Priority'].astype(str) + " rp=" + df['Planet Radius (TOI)'].map(lambda x:'%2.1f' % x).astype(str) + " steff=" + df['Teff (TOI)'].map(lambda x:'%5.0f' % x).astype(str) + " " + df['comment']


        if save == True:
            np.savetxt(f"starlist_{obs_date}.tbl",f,delimiter="  ",fmt='%s')


        return(f)

    def load_starlist(self,starlist):
        raise NotImplementedError

