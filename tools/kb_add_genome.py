"""Añade a biosim_kb.json el genoma modelo (fichas de gen, Fase 2 Modulo A) y reglas de ADN R18-R30."""
import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "backend" / "app" / "knowledge" / "biosim_kb.json"
kb = json.loads(p.read_text(encoding="utf-8-sig"))

NOTE = ("Aminoacidos N-terminales segun UniProt; codones, intron y promotor son DIDACTICOS "
        "(no es la secuencia genomica real). Sustituir por RefSeq versionado antes de comparar con datos reales.")

def gene(gid, product, uniprot, strand, promoter, exon1, intron, exon2, role, promoter_kind="TATA"):
    return {
        "id": gid, "product": product, "organism": "Homo sapiens (referencia)",
        "cell_type_reference": "celula madre pluripotente (modelo)",
        "strand": strand, "uniprot": uniprot, "evidence": "didactico", "source_note": NOTE,
        "role": role, "promoter_kind": promoter_kind,
        "parts": [
            {"type": "promoter", "seq": promoter},
            {"type": "utr5", "seq": "ACGC"},
            {"type": "exon", "seq": exon1},
            {"type": "intron", "seq": intron},
            {"type": "exon", "seq": exon2},
            {"type": "utr3", "seq": "AATAAA"},
        ],
    }

kb["genome"] = {
    "description": "Loci modelo de la celula pluripotente. Cada gen es una ficha (Fase 2, Modulo A) en orientacion codificante 5'->3'; si strand='-' el motor lo coloca invertido-complementado en la hebra directa del segmento.",
    "lineage_gene": {
        "pluripotente": "POU5F1", "ectodermo": "PAX6", "endodermo": "SOX17",
        "mesodermo": "TBXT", "trofectodermo": "CDX2", "dano": "CDKN1A", "basal": "TP53"
    },
    "loci": {
        "TP53":   gene("TP53", "p53", "P04637", "+", "GCGCTATAAAAGGCCGCTGC", "ATGGAGGAGCCG", "GTAAGTACTTATCTTTGCAG", "CAGTCAGATCCTTGA", "supresor tumoral; factor de transcripcion"),
        "CDKN1A": gene("CDKN1A", "p21", "P38936", "-", "GAACATGTCCCAACATGTTG", "ATGTCAGAACCG", "GTGAGTCCTTTCCTCCACAG", "GCTGGGTAA", "inhibidor CDK; diana de p53", "p53_RE"),
        "POU5F1": gene("POU5F1", "OCT4", "Q01860", "+", "CCCTATAAATCCCTTTGGAC", "ATGGCGGGACAC", "GTAAGGCTCTCTTCCCACAG", "CTGGCTTCAGATTTTTGA", "nucleo de pluripotencia"),
        "PAX6":   gene("PAX6", "PAX6", "P26367", "+", "GGATATAAAGCCTCTCCGCA", "ATGCAGAACAGT", "GTAAGAGCTTGTTTCTTCAG", "CACAGCGGAGTGTAA", "neuroectodermo"),
        "SOX17":  gene("SOX17", "SOX17", "Q9H6I2", "+", "CTGTATAAAAGGGCTCCAGC", "ATGAGCAGCCCG", "GTGAGCTTCCTTCTCCCTAG", "GATGCGGGATACTAG", "endodermo definitivo"),
        "TBXT":   gene("TBXT", "BRACHYURY", "O15178", "+", "AGCTATAAATGCGCGTCCGA", "ATGAGCTCCCCT", "GTAAGTTTCTCTCCTTGCAG", "GGCACCGAGTGA", "mesodermo"),
        "CDX2":   gene("CDX2", "CDX2", "Q99626", "+", "TCCTATAAAGGCCTCGCTGG", "ATGTACGTGAGC", "GTGAGACCCTCTTTTCTCAG", "TACCTCCTGTAA", "trofectodermo"),
    },
    "dna_geometry": {
        "form": "ADN-B", "rise_A": 3.4, "bp_per_turn": 10.5, "diameter_nm": 2.0,
        "phosphate_radius_A": 8.9, "c1_radius_A": 5.9,
        "colors": {"fosfato": "#f59e0b", "desoxirribosa": "#d1d5db", "A": "#22c55e", "T": "#ef4444", "G": "#eab308", "C": "#2563eb", "U": "#ec4899"},
        "h_bonds": {"AT": 2, "GC": 3},
        "nucleosome": {"bp": 147, "turns": 1.65, "octamer": "2x(H2A,H2B,H3,H4)"},
        "source": "COLAB"
    },
}

dna_rules = [
    {"id": "R18", "if": "ficha de gen", "then": "promotor, region transcrita, exones/intrones y CDS son entidades distintas; no toda secuencia se transcribe", "evidence": "literatura", "source": "ALB_DNA_RNA"},
    {"id": "R19", "if": "transcripcion", "then": "se identifica primero la hebra molde segun la orientacion del gen (+/-); ARN 5'->3' complementario a la molde", "evidence": "literatura", "source": "ALB_DNA_RNA"},
    {"id": "R20", "if": "secuencia con simbolos no ACGT o incompleta", "then": "se marca invalida/no resuelta; nunca se corrige en silencio", "evidence": "didactico", "source": "COLAB"},
    {"id": "R21", "if": "pre-ARNm", "then": "se anade caperuza 5' (presente/ausente, sin quimica)", "evidence": "literatura", "source": "ALB_DNA_RNA"},
    {"id": "R22", "if": "intron con senales GU...AG", "then": "splicing: se retira el intron y se unen exones; se guardan pre-ARNm, intrones retirados y ARNm maduro (patron fijo)", "evidence": "literatura", "source": "ALB_DNA_RNA"},
    {"id": "R23", "if": "senal AAUAAA en 3'", "then": "corte y poliadenilacion (cola poli-A como propiedad)", "evidence": "literatura", "source": "ALB_DNA_RNA"},
    {"id": "R24", "if": "ARNm maduro", "then": "traduccion desde el primer AUG en marco hasta el primer STOP; detecta longitud no multiplo de 3 y ausencia de STOP", "evidence": "literatura", "source": "ALB_BGM"},
    {"id": "R25", "if": "variante sinonima", "then": "cambia codon, mismo aminoacido; no se declara neutra automaticamente", "evidence": "literatura", "source": "COLAB"},
    {"id": "R26", "if": "variante missense", "then": "se registra posicion y aa ref/var; sin declarar patogenicidad", "evidence": "literatura", "source": "COLAB"},
    {"id": "R27", "if": "variante nonsense", "then": "proteina truncada potencial; NMD no simulado", "evidence": "literatura", "source": "COLAB"},
    {"id": "R28", "if": "p53 activo y elemento de respuesta en promotor (CDKN1A)", "then": "p53 tetramero se une por el surco mayor y activa la transcripcion (alta afinidad)", "evidence": "literatura", "source": "LEVINE09"},
    {"id": "R29", "if": "gen silenciado / expresion < 0.1", "then": "cromatina compacta en nucleosomas (147 pb, 1,65 vueltas); sin transcripcion", "evidence": "literatura", "source": "ALB_CGE"},
    {"id": "R30", "if": "DSB dentro del locus", "then": "la ARN polimerasa no atraviesa la rotura; transcripcion del locus bloqueada hasta reparar", "evidence": "literatura", "source": "JACKSON09"},
]
ids = {r["id"] for r in kb["rules"]}
kb["rules"] += [r for r in dna_rules if r["id"] not in ids]
kb["version"] = "kb-0.2.0"
p.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok", len(kb["rules"]), "reglas,", len(kb["genome"]["loci"]), "loci")
