import random
import math

class Cerebro:
    def __init__(self, n_entradas, n_ocultas, n_salidas):
        self.n_entradas = n_entradas
        self.n_ocultas = n_ocultas
        self.n_salidas = n_salidas
        
        # Pesos: capa entrada -> oculta
        self.pesos_eo = [[random.uniform(-1, 1) for _ in range(n_ocultas)] for _ in range(n_entradas)]
        
        # Pesos: capa oculta -> salida
        self.pesos_os = [[random.uniform(-1, 1) for _ in range(n_salidas)] for _ in range(n_ocultas)]
        
        # Bias
        self.bias_o = [random.uniform(-1, 1) for _ in range(n_ocultas)]
        self.bias_s = [random.uniform(-1, 1) for _ in range(n_salidas)]

    def sigmoide(self, x):
        try:
            return 1 / (1 + math.exp(-x))
        except OverflowError:
            return 0 if x < 0 else 1

    def pensar(self, entradas):
        # Capa Oculta
        ocultas = []
        for j in range(self.n_ocultas):
            suma = self.bias_o[j]
            for i in range(self.n_entradas):
                suma += entradas[i] * self.pesos_eo[i][j]
            ocultas.append(self.sigmoide(suma))
            
        # Capa Salida
        salidas = []
        for k in range(self.n_salidas):
            suma = self.bias_s[k]
            for j in range(self.n_ocultas):
                suma += ocultas[j] * self.pesos_os[j][k]
            salidas.append(self.sigmoide(suma))
            
        return salidas # Retorna lista con probabilidades [Arriba, Abajo, Izq, Der] o similar

    def mutar(self, tasa_mutacion):
        def ajustar(valor):
            if random.random() < tasa_mutacion:
                return valor + random.gauss(0, 0.1)
                #return random.uniform(-1, 1) # Mutacion drastica
            return valor

        # Mutar pesos EO
        for i in range(self.n_entradas):
            for j in range(self.n_ocultas):
                self.pesos_eo[i][j] = ajustar(self.pesos_eo[i][j])
                
        # Mutar pesos OS
        for j in range(self.n_ocultas):
            for k in range(self.n_salidas):
                self.pesos_os[j][k] = ajustar(self.pesos_os[j][k])
                
        # Mutar Bias
        self.bias_o = [ajustar(b) for b in self.bias_o]
        self.bias_s = [ajustar(b) for b in self.bias_s]

    def cruzar(self, otro_cerebro):
        hijo = Cerebro(self.n_entradas, self.n_ocultas, self.n_salidas)
        
        # Cruzar pesos simplemente eligiendo de uno u otro aleatoriamente
        # (Se podria hacer punto de corte, pero esto es mas simple y efectivo para redes pequeñas)
        
        # Pesos EO
        for i in range(self.n_entradas):
            for j in range(self.n_ocultas):
                hijo.pesos_eo[i][j] = self.pesos_eo[i][j] if random.random() < 0.5 else otro_cerebro.pesos_eo[i][j]
        
        # Pesos OS
        for j in range(self.n_ocultas):
            for k in range(self.n_salidas):
                hijo.pesos_os[j][k] = self.pesos_os[j][k] if random.random() < 0.5 else otro_cerebro.pesos_os[j][k]
                
        return hijo
