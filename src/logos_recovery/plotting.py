from pathlib import Path
import matplotlib.pyplot as plt
BLUE, ORANGE, GRAY = '#176B91', '#C55A11', '#666666'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def savefig(fig, out, name):
    (out/'figures').mkdir(parents=True, exist_ok=True)
    metadata = {
        'png': {'Software': None},
        'svg': {'Creator': None, 'Date': None, 'Format': None, 'Type': None},
        'pdf': {'Creator': None, 'Producer': None, 'CreationDate': None,
                'ModDate': None, 'Author': None, 'Title': None,
                'Subject': None, 'Keywords': None},
    }
    for ext in ('png','svg','pdf'):
        fig.savefig(out/'figures'/f'{name}.{ext}', bbox_inches='tight', dpi=180,
                    metadata=metadata[ext])
    plt.close(fig)
def write(df, out, name):
    (out/'tables').mkdir(parents=True, exist_ok=True)
    df.to_csv(out/'tables'/f'{name}.csv', index=False, float_format='%.12g')
