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
        result = []
        prezzi = []

        for distributore in self._distributori:
            somma = 0
            prezzi_distributore = PrezzoDAO.get_prezzi(distributore.id)    # Qui metto tutti i prezzi relativi a quel distributore
            for prezzo in prezzi_distributore:
                if prezzo.data.month == mese:
                    prezzi.append(prezzo)
                    somma += prezzo.prezzo_litro

            media_prezzi = somma / (len(prezzi))
            result.append((distributore.nome, media_prezzi))

        return result




    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)





    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if len(sequenza_parziale) == 7:
            self.__sequenza_ottima = sequenza_parziale
            self.__costo_ottimo = costo_corrente
            return
        else:
            # Devo capire quale distributore ha il prezzo minimo per il giorno 1, per partire da lui
            if costo_corrente == 0:
                id_min = None
                prezzo_min = None
                for id, prezzi in prezzi_settimana.items():
                    if prezzo_min is None:
                        prezzo_min = prezzi[0]
                        id_min = id
                    elif prezzi[0] < prezzo_min:
                        prezzo_min = prezzi[0]
                        id_min = id
                costo_corrente += prezzo_min * 100
                ultimo_distributore = id_min
                giorno += 1
                sequenza_parziale.append(ultimo_distributore)
            else:
                costo_giorno = prezzi_settimana[ultimo_distributore][giorno - 1]  # TODO controllare
                for distributore in self._distributori:
                    costo = prezzi_settimana[distributore.id][giorno - 1]
                    if costo * 100 + self.prezzo_fisso < costo_giorno * 100:   # Allora vale la pena spostarsi
                        ultimo_distributore = distributore.id
                        sequenza_parziale.append(ultimo_distributore)
                        costo_corrente += costo * 100 + self.prezzo_fisso
                        return
                    else:
                        sequenza_parziale.append(ultimo_distributore)
                        costo_corrente += costo_giorno * 100
                        return












    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        result = {}

        for distributore in self._distributori:
            prezzi = PrezzoDAO.get_prezzi(distributore.id)
            prezzi_settimana = []
            for prezzo in prezzi:
                if prezzo.data.month == mese and 1 <= prezzo.data.day <= 7:
                    prezzi_settimana.append(prezzo.prezzo_litro)
            result[distributore.id] = prezzi_settimana
        return result
