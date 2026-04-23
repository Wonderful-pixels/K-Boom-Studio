from .fwsim import import_fwsim
from .finale import import_finale
from .kseq import import_kseq

methods={"FWsim" : import_fwsim,
         "Finale Fireworks" : import_finale,
         "K-Boom KSEQ file" : import_kseq}