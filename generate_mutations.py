import json
import shutil
from pathlib import Path

ROOT = Path(".")
OUT = ROOT / "mutation_build"
MANIFEST = ROOT / "runs/mutations/mutation_manifest.json"

HEAD_SRC = ROOT / "mutations/head/original_head.c"
CUT_SRC = ROOT / "mutations/cut/original_cut.c"

with MANIFEST.open() as f:
    manifest = json.load(f)


def write_variant(program, mutation_id, source):
    outdir = OUT / program / mutation_id
    outdir.mkdir(parents=True, exist_ok=True)

    source_file = outdir / f"{program}.c"
    source_file.write_text(source)

    return source_file


def head_mutations(src):
    return {
        "H01": src.replace(
            "i += (len && (buf[len - 1] == '\\n'));",
            "i += (len && (buf[len - 1] != '\\n'));",
            1,
        ),

        "H02": src.replace(
            "buf[len - 1] == '\\n'",
            "buf[len - 1] == '\\r'",
            1,
        ),

        "H03": src.replace(
            "while (i < n &&",
            "while (i <= n &&",
            1,
        ),

        "H04": src.replace(
            "fwrite(buf, 1, len, stdout);",
            "fwrite(buf, 1, len - (len > 0), stdout);",
            1,
        ),

        "H05": src.replace(
            "(len = getline(&buf, &size, fp)) > 0",
            "(len = getline(&buf, &size, fp)) >= 0",
            1,
        ),

        "H06": src.replace(
            "size_t n = 10;",
            "size_t n = 5;",
            1,
        ),

        "H07": src.replace(
            "n = estrtonum(EARGF(usage()), 0, MIN(LLONG_MAX, SIZE_MAX));",
            "n = estrtonum(EARGF(usage()), 0, MIN(LLONG_MAX, SIZE_MAX)) + 1;",
            1,
        ),

        "H08": src.replace(
            'printf("==> %s <==\\n", *argv);',
            'printf("FILE: %s\\n", *argv);',
            1,
        ),

        "H09": src.replace(
            'weprintf("fopen %s:", *argv);\n\t\t\t\tret = 1;',
            'weprintf("fopen %s:", *argv);\n\t\t\t\tret = 0;',
            1,
        ),

        "H10": src.replace(
            "ret |= fshut(stdin, \"<stdin>\") | fshut(stdout, \"<stdout>\");",
            "ret = fshut(stdin, \"<stdin>\") | fshut(stdout, \"<stdout>\");",
            1,
        ),
    }


def cut_mutations(src):
    return {
        "C01": src.replace(
            "r->max = (*s == '-') ? strtoul(s + 1, &s, 10) : r->min;",
            "r->max = (*s == '-') ? strtoul(s + 1, &s, 10) : r->min + 1;",
            1,
        ),

        "C02": src.replace(
            "r->max && r->max + 1 < l->min",
            "r->max && r->max + 2 < l->min",
            1,
        ),

        "C03": src.replace(
            "if (n >= s->len)",
            "if (n > s->len)",
            1,
        ),

        "C04": src.replace(
            "for (n++, i = 0; i < s->len; i++)",
            "for (n += 2, i = 0; i < s->len; i++)",
            1,
        ),

        "C05": src.replace(
            "!memcmp(s->data + i, delim, delimlen)",
            "memcmp(s->data + i, delim, delimlen) != 0",
            1,
        ),

        "C06": src.replace(
            'i += delimlen;\n\t\t\t\tcontinue;',
            'i += 1;\n\t\t\t\tcontinue;',
            1,
        ),

        "C07": src.replace(
            "if (!sflag) {",
            "if (sflag) {",
            1,
        ),

        "C08": src.replace(
            "if (!s.len)",
            "if (s.len > 0)",
            1,
        ),

        "C09": src.replace(
            "putchar('\\n');",
            "putchar(' ');",
            1,
        ),

        "C10": src.replace(
            'ret |= fshut(stdin, "<stdin>") | fshut(stdout, "<stdout>");',
            'ret = fshut(stdin, "<stdin>") | fshut(stdout, "<stdout>");',
            1,
        ),
    }


head_original = HEAD_SRC.read_text()
cut_original = CUT_SRC.read_text()

head_variants = head_mutations(head_original)
cut_variants = cut_mutations(cut_original)

records = []

for mutation_id, source in head_variants.items():
    if source == head_original:
        raise RuntimeError(f"{mutation_id}: transformation made no change")

    path = write_variant("head", mutation_id, source)

    records.append({
        "id": mutation_id,
        "program": "head",
        "source": str(path),
        "changed": True
    })

for mutation_id, source in cut_variants.items():
    if source == cut_original:
        raise RuntimeError(f"{mutation_id}: transformation made no change")

    path = write_variant("cut", mutation_id, source)

    records.append({
        "id": mutation_id,
        "program": "cut",
        "source": str(path),
        "changed": True
    })

manifest_out = ROOT / "runs/mutations/generated_variants.json"

with manifest_out.open("w") as f:
    json.dump(records, f, indent=2)

print("=" * 70)
print("MUTATION GENERATION")
print("=" * 70)
print("Head variants:", len(head_variants))
print("Cut variants :", len(cut_variants))
print("Total        :", len(records))
print()
print("Output:", manifest_out)
print("=" * 70)
