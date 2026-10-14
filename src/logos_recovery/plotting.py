from pathlib import Path
import matplotlib.pyplot as plt
BLUE, ORANGE, GRAY = '#176B91', '#C55A11', '#666666'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def savefig(fig, out, name):
    (out/'figures').mkdir(parents=True, exist_ok=True)
    for ext in ('png','svg','pdf'):
        fig.savefig(out/'figures'/f'{name}.{ext}', bbox_inches='tight', dpi=180)
    plt.close(fig)
def write(df, out, name):
    (out/'tables').mkdir(parents=True, exist_ok=True)
    df.to_csv(out/'tables'/f'{name}.csv', index=False, float_format='%.12g')
