import subprocess, tempfile, os

# Tomar una proteina de Bacillus y ver que dominios tiene
with open('proteomas_donantes/proteoma_Bacillus_subtilis.faa') as f:
    contenido = f.read()

# Extraer las primeras 5 secuencias
seqs = []
header = None
seq = []
for linea in contenido.split(chr(10)):
    if linea.startswith('>'):
        if header:
            seqs.append((header, ''.join(seq)))
        header = linea
        seq = []
    else:
        seq.append(linea.strip())
    if len(seqs) >= 5:
        break

print('Primeras 5 proteinas de Bacillus:')
for h, s in seqs:
    print(' ', h[:80], '|', len(s), 'aa')
