import matplotlib.pyplot as plt
import numpy as np
import cv2
from pillow_heif import open_heif
from pathlib import Path
import os
import pandas as pd
from scipy.stats import circmean, circstd

# heic to BGR helper function
def heicread(file_path): 
    heif_file = open_heif(file_path)
    image_np = np.asarray(heif_file)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    return image_bgr

def plot_hsv_singular(filepath):
    image = heicread(filepath)
    
    lower_white = np.array([61, 61, 61], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(image, lower_white, upper_white)

    mask_invert = cv2.bitwise_not(white_mask)
    result = cv2.bitwise_and(image, image, mask=mask_invert)

    hsv_image = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
    hue, sat, val = cv2.split(hsv_image)

    mask = sat > 30

    plt.subplot(1,3,1)
    plt.hist(hue[mask], bins=180, density=True, color='red', alpha=0.6) 

    plt.subplot(1,3,2)
    plt.hist(sat[mask], bins=256, density=True, color='red', alpha=0.6) 

    plt.subplot(1,3,3)
    plt.hist(val[mask], bins=256, density=True, color='red', alpha=0.6) 

    plt.show()

def plot_hsv_multiple(folderpath, freq=False, compare=True):
    stats_df = pd.DataFrame(columns=(['File','Mean Hue','SD Hue','Mean Sat','SD Sat','Mean Val', 'SD Val','Mean Hue SE','Mean Sat SE','Mean Val SE']))
    control_files = []
    exp_files = []

    folderpath = Path(folderpath)
    for filepath in folderpath.iterdir():
        if filepath.is_file():
            if 'Control' in filepath.name:
                control_files.append(filepath.name)
            elif 'Exp' in filepath.name:
                exp_files.append(filepath.name)
            else:
                raise FileNotFoundError
    
    fig, axes = plt.subplots(2,3,figsize=(16,8))

    # Controls
    for i, file in enumerate(control_files):
        filepath = os.path.join(folderpath, file)
        if ('.HEIC' in file) or ('.heic' in file):
            image = heicread(filepath)
        else:
            image = cv2.imread(filepath)

        

        lower_white = np.array([61, 61, 61], dtype=np.uint8)
        upper_white = np.array([255, 255, 255], dtype=np.uint8)
        white_mask = cv2.inRange(image, lower_white, upper_white)

        mask_invert = cv2.bitwise_not(white_mask)
        result = cv2.bitwise_and(image, image, mask=mask_invert)

        hsv_image = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
        hue, sat, val = cv2.split(hsv_image)

        mask = sat > 30
        if i == 0:
            COLOR = 'pink'
        elif i == 1:
            COLOR = 'red'
        elif i == 2:
            COLOR = 'orange'
        elif i == 3:
            COLOR = 'yellow'
        elif i == 4:
            COLOR = 'green'
        elif i == 5:
            COLOR = 'blue'
        elif i == 6:
            COLOR = 'purple'

        h, s, v = hue[mask], sat[mask], val[mask]
        print(h)
        print(s)
        print(v)
        row = pd.DataFrame({'File':[f'{file}'],'Mean Hue':[circmean(h, high=180, low=0)], 'SD Hue':[circstd(h, high=180, low=0)], 'Mean Sat':[np.mean(s)], 'SD Sat':[np.std(s)], 'Mean Val':[np.mean(v)],'SD Val':[np.std(v)]})
        stats_df = pd.concat([stats_df,row])
        # print(row)
        # if freq==True:
        #     axes[0,0].hist(hue[mask], bins=180, density=True, color=COLOR, alpha=0.6)
        #     axes[0,1].hist(sat[mask], bins=256, density=True, color=COLOR, alpha=0.6) 
        #     axes[0,2].hist(val[mask], bins=256, density=True, color=COLOR, alpha=0.6) 

    # Experimentals
    for i, file in enumerate(exp_files):
        filepath = os.path.join(folderpath, file)
        
        if ('.HEIC' in file) or ('.heic' in file):
            image = heicread(filepath)
        else:
            image = cv2.imread(filepath)

        lower_white = np.array([61, 61, 61], dtype=np.uint8)
        upper_white = np.array([255, 255, 255], dtype=np.uint8)
        white_mask = cv2.inRange(image, lower_white, upper_white)

        mask_invert = cv2.bitwise_not(white_mask)
        result = cv2.bitwise_and(image, image, mask=mask_invert)

        hsv_image = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
        hue, sat, val = cv2.split(hsv_image)

        mask = sat > 30
        if i == 0:
            COLOR = 'pink'
        elif i == 1:
            COLOR = 'red'
        elif i == 2:
            COLOR = 'orange'
        elif i == 3:
            COLOR = 'yellow'
        elif i == 4:
            COLOR = 'green'
        elif i == 5:
            COLOR = 'blue'
        elif i == 6:
            COLOR = 'purple'

        h, s, v = hue[mask], sat[mask], val[mask]
        row = pd.DataFrame({'File':[f'{file}'],'Mean Hue':[circmean(h, high=180, low=0)], 'SD Hue':[circstd(h, high=180, low=0)], 'Mean Sat':[np.mean(s)], 'SD Sat':[np.std(s)], 'Mean Val':[np.mean(v)],'SD Val':[np.std(v)]})
        stats_df = pd.concat([stats_df,row])

        # if freq==True:
        #     axes[1,0].hist(hue[mask], bins=180, density=True, color=COLOR, alpha=0.6) 
        #     axes[1,1].hist(sat[mask], bins=256, density=True, color=COLOR, alpha=0.6) 
        #     axes[1,2].hist(val[mask], bins=256, density=True, color=COLOR, alpha=0.6)

    stats_df = stats_df.reset_index(drop=True)
    for i in range(len(stats_df)):
        
        SEhue = (stats_df.loc[i,'SD Hue'])/(np.sqrt(len(stats_df)/2))
        stats_df.loc[i,'Mean Hue SE'] = SEhue

        SEsat = (stats_df.loc[i,'SD Sat'])/(np.sqrt(len(stats_df)/2))
        stats_df.loc[i,'Mean Sat SE'] = SEsat

        SEval = (stats_df.loc[i,'SD Val'])/(np.sqrt(len(stats_df)/2))
        stats_df.loc[i,'Mean Val SE'] = SEval

    midp = len(stats_df)//2
    control_df = stats_df.iloc[:midp]
    exp_df = stats_df.iloc[midp:]
    print(control_df,exp_df)

    for i in range(len(control_df)):
        control_df.loc[i,'File'] = (f'Day {i}')
   
    if freq==False:
        control_df.plot.bar(x='File', y='Mean Hue', yerr='Mean Hue SE',ax=axes[0,0], title='Control: Mean Hue')
        control_df.plot.bar(x='File', y='Mean Sat', yerr='Mean Sat SE',ax=axes[0,1], title='Control: Mean Saturation')
        control_df.plot.bar(x='File', y='Mean Val', yerr='Mean Val SE',ax=axes[0,2], title='Control: Mean Value')
    
        exp_df.plot.bar(x='File', y='Mean Hue', yerr='Mean Hue SE',ax=axes[1,0], title='Experimental: Mean Hue')
        exp_df.plot.bar(x='File', y='Mean Sat', yerr='Mean Sat SE',ax=axes[1,1], title='Experimental: Mean Saturation')
        exp_df.plot.bar(x='File', y='Mean Val', yerr='Mean Val SE',ax=axes[1,2], title='Experimental: Mean Value')
    
    if (freq==True) & (compare==True):
        days_c = range(len(control_df))
        days_e = range(len(exp_df))

        axes[0,0].errorbar(days_c, control_df['Mean Hue'], yerr=control_df['Mean Hue SE'], marker='o', label='Control',alpha=0.5)
        axes[0,0].errorbar(days_e, exp_df['Mean Hue'], yerr=exp_df['Mean Hue SE'], marker='o', label='Experimental',alpha=0.5)
        axes[0,0].set_title('Mean Hue Compared Between Groups')
        axes[0,0].legend()

        axes[0,1].errorbar(days_c, control_df['Mean Sat'], yerr=control_df['Mean Sat SE'], marker='o', label='Control',alpha=0.5)
        axes[0,1].errorbar(days_e, exp_df['Mean Sat'], yerr=exp_df['Mean Sat SE'], marker='o', label='Experimental',alpha=0.5)
        axes[0,1].set_title('Mean Saturation Compared Between Groups')
        axes[0,1].legend()

        axes[0,2].errorbar(days_c, control_df['Mean Val'], yerr=control_df['Mean Val SE'], marker='o', label='Control',alpha=0.5)
        axes[0,2].errorbar(days_e, exp_df['Mean Val'], yerr=exp_df['Mean Val SE'], marker='o', label='Experimental',alpha=0.5)
        axes[0,2].set_title('Mean Value Compared Between Groups')
        axes[0,2].legend()


    stats_df.to_csv('Apple HSV Values.csv',index=False)

    fig.tight_layout()
    plt.show()



plot_hsv_multiple(folderpath='C:/Users/rad11/Downloads/Banana Apple/',freq=True, compare=True)