import copy

from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

        self.prezzo_fisso = 5

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """

        '''
        result = []

        for distributore in self._distributori:
            somma = 0
            prezzi = []
            prezzi_distributore = PrezzoDAO.get_prezzi(distributore.id)    # Qui metto tutti i prezzi relativi a quel distributore
            for prezzo in prezzi_distributore:
                if prezzo.data.month == mese:
                    prezzi.append(prezzo)
                    somma += prezzo.prezzo_litro

            if len(prezzi) != 0:
                media_prezzi = somma / (len(prezzi))
            else:
                media_prezzi = 0
            result.append((distributore.nome, media_prezzi))
        '''


        risultato = []

        for distributore in self._distributori:
            prezzi_mese = []
            for prezzo in distributore.get_prezzi():
                if prezzo.data.month == mese:
                    prezzi_mese.append(prezzo.prezzo_litro)

            media = sum(prezzi_mese) / len(prezzi_mese)
            risultato.append((distributore.nome, media))
        return risultato




    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese) # {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}

        self.__ricorsione([], 1, None, 0, prezzi_settimana)
        print(self.__sequenza_ottima)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        if len(sequenza_parziale) == 7:
            # La salvo solo se è la prima trovata (-1 = "nessuna soluzione ancora")
            # oppure se costa meno della migliore trovata finora
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = copy.deepcopy(sequenza_parziale)   # Salvo una copia
            return

        # Devo scegliere il distributore per il "giorno" corrente.
        else:
            for distributore in self._distributori:
                id_d = distributore.id
                costo = prezzi_settimana[id_d][giorno - 1] * 100

                # Costo fisso di 5€ solo se cambio distributore rispetto a ieri
                # Al giorno 1 ultimo_distributore è None: nessun costo di spostamento
                if ultimo_distributore is not None and id_d != ultimo_distributore:
                    costo += self.prezzo_fisso

                sequenza_parziale.append(id_d)
                self.__ricorsione(sequenza_parziale, giorno + 1, id_d, costo_corrente + costo, prezzi_settimana)
                sequenza_parziale.pop()






        # A - Condizione terminale: sequenza completa (7 giorni)
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:   # Vuol dire che ho trovato qualcosa che è migliore di quello che avevo salvato
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale) # Come fare il .copy() ma con la lista
            return

        # Parte di ricorsione
        for id_distributore, prezzi in prezzi_settimana.items():
            costo = prezzi[giorno - 1] * 100
            if ultimo_distributore is not None and ultimo_distributore != id_distributore:
                costo += self.prezzo_fisso
            nuovo_costo = costo_corrente + costo

            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                sequenza_parziale.append(id_distributore)
                self.__ricorsione(sequenza_parziale, giorno + 1, id_distributore, nuovo_costo, prezzi_settimana)
                sequenza_parziale.pop()




    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        result = {}

        for distributore in self._distributori:
            '''prezzi = PrezzoDAO.get_prezzi(distributore.id)'''
            prezzi = distributore.get_prezzi()
            prezzi_settimana = []
            for prezzo in prezzi:
                if prezzo.data.month == mese and 1 <= prezzo.data.day <= 7:
                    prezzi_settimana.append(prezzo.prezzo_litro)
            result[distributore.id] = prezzi_settimana
        return result
