"""
Estilo comum das figuras. As figuras sao geradas no tamanho em que serao impressas no
formato de duas colunas (WebMedia/ACM sigconf), para que a fonte de 7-8 pt nao encolha
ao ser incluida no artigo.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLUNA = 3.33   # largura de uma coluna, em polegadas
PAGINA = 7.0    # largura das duas colunas (figure*)

# paleta Okabe-Ito (legivel para daltonicos e em impressao em tons de cinza)
COR = {"usuarios": "#0072B2", "cervejas": "#E69F00", "todos": "black", "destaque": "#D55E00",
       "verde": "#009E73", "cinza": "0.45", "roxo": "#CC79A7", "azul_claro": "#56B4E9"}

plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "lines.linewidth": 1.2, "lines.markersize": 3, "axes.linewidth": 0.6,
    "grid.linewidth": 0.3, "grid.alpha": 0.4, "legend.frameon": False,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "figure.dpi": 150,
    "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False,
})


def salvar_figura(fig, caminho_sem_extensao):
    fig.savefig(caminho_sem_extensao + ".pdf")
    fig.savefig(caminho_sem_extensao + ".png", dpi=200)
    plt.close(fig)
