"""Media, desvio padrao amostral e intervalo de confianca (regra do enunciado):
   n >= 30            -> Normal:    x̄ ± z_{α/2} · s/√n
   n < 30, σ desconh. -> t-Student: x̄ ± t_{α/2, n-1} · s/√n"""
import math

from scipy import stats


def resumo(amostras, confianca=0.95):
    n = len(amostras)
    media = sum(amostras) / n
    dp = math.sqrt(sum((x - media) ** 2 for x in amostras) / (n - 1)) if n > 1 else 0.0
    alfa = 1 - confianca
    if n >= 30:
        critico, dist = stats.norm.ppf(1 - alfa / 2), "Z"
    else:
        critico, dist = stats.t.ppf(1 - alfa / 2, n - 1), "t"
    margem = critico * dp / math.sqrt(n)
    return {"n": n, "media": media, "desvio_padrao": dp, "ic_inf": media - margem,
            "ic_sup": media + margem, "distribuicao": dist, "valor_critico": critico}


if __name__ == "__main__":
    # autoverificacao: n = 4 usa t com 3 g.l. (t_0.975,3 = 3.182)
    r = resumo([1.0, 2.0, 3.0, 4.0])
    assert r["distribuicao"] == "t" and abs(r["valor_critico"] - 3.1824) < 1e-3
    assert abs(r["ic_sup"] - (2.5 + 3.1824 * 1.2910 / 2)) < 1e-3
    r = resumo([float(i % 7) for i in range(40)])
    assert r["distribuicao"] == "Z" and abs(r["valor_critico"] - 1.95996) < 1e-4
    print("ok")
