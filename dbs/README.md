# Bases Pfam

Las bases Pfam son muy grandes y no se incluyen en el repo.

Descarga Pfam completo:
  wget https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz
  gunzip Pfam-A.hmm.gz

Construye sub-bases por rasgo:
  python construir_pfam_estres.py
