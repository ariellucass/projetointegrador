import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Definir o pino 4 como saída
PIN_GPIO = 17
GPIO.setup(PIN_GPIO, GPIO.OUT)

print(f"Acionando o pino GPIO {PIN_GPIO}...")

try:
    # Ligar o pino (nível alto)
    GPIO.output(PIN_GPIO, GPIO.HIGH)
    print("Pino ligado!")
    time.sleep(2)  # Manter ligado por 2 segundos

    # Desligar o pino (nível baixo)
    GPIO.output(PIN_GPIO, GPIO.LOW)
    print("Pino desligado!")
    time.sleep(1) # Manter desligado por 1 segundo

    # Você pode fazer um pisca-pisca rápido para testar
    print("Pisca-pisca rápido (3 vezes)...")
    for _ in range(3):
        GPIO.output(PIN_GPIO, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(PIN_GPIO, GPIO.LOW)
        time.sleep(0.2)

except KeyboardInterrupt:
    # Permite sair do script com Ctrl+C de forma limpa
    print("\nPrograma interrompido pelo usuário.")

finally:
    # Sempre limpe as configurações dos pinos GPIO ao finalizar o script.
    # Isso é crucial para evitar que os pinos fiquem em um estado indefinido
    # e causem problemas em scripts futuros ou no hardware.
    GPIO.cleanup()
    print("Configurações GPIO limpas. Pinos liberados.")
