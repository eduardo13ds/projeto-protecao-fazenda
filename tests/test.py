from machine import ADC, Pin
import time
import dht
import machine
import math

# Configuração para a leitura de humidade do DHT

sensor = dht.DHT11(machine.Pin(18))

pot = ADC(Pin(2))
pot.atten(ADC.ATTN_11DB)  # Faixa de 0-3.3V

# Valor do resistor de carga (ajuste conforme seu circuito)
R = pow(10,13) #Resistencia do ar umido em ohm



while True:
    print("Tudo ocorrendo perfeitamente :D")
    # Leitura do ADC (12 bits = 0-4095)
    adc_value = pot.read()
    time.sleep(0.1)  # Atraso para estabilização
    # No físico utilizar:
    sensor.measure()
    umidade = sensor.humidity()
    # Conversão para tensão
    voltage = (adc_value * 3.3) / 4095
    
    # Cálculo da corrente (Lei de Ohm)
    current = voltage / R
    
    # J = I/Area Cálculo da densidade elétrica 
    # Area é a seção tranversal do pino
    # (região onde a corrente está passando)
    j = current / (0.785*(pow(10,-4))) # Supondo que seja circular de 1 cm de diametro
    # 3.14*0.5² = 0.785
    # Pela lei de Ohm: J = σE portanto E = J/σ
    # E é o campo elétrico
    # σ condutividade elétrica do material, o material é o ar humido
    # variando entre 10^-9 e 10^-11
    E = j/pow(10,-10)

    # Exibição dos resultados
    print(f"ADC: {adc_value:4d} | Tensão: {voltage:.3f}V | Corrente: {current}A")
    print(f"Campo elétrico é de {E} V/m // {E *0.01} V/cm")
    print(f"Umidade: {umidade}")

    if (E > 10000 and umidade > 75):# A diferença de potencial varia 
        print("⚡ ALERTA: TEMPESTADE INTENSA SE APROXIMANDO!")
    

    time.sleep(5)  # Intervalo entre leiturasz