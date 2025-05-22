from unicorn import *
from unicorn.x86_const import *
from keystone import *

def ejecutar_imc_unicorn(peso, estatura_cm):
    peso = int(peso)  # Convertir a entero
    # Ensamblar el código usando Keystone
    ks = Ks(KS_ARCH_X86, KS_MODE_32)
    instrucciones = [
        f"mov eax, {peso}",           # peso
        f"mov ebx, {estatura_cm}",    # estatura
        "imul ebx, ebx",              # estatura^2
        "mov ecx, eax",
        "imul ecx, 10000",            # peso * 10000
        "mov eax, ecx",
        "idiv ebx"                    # resultado en eax
    ]
    encoding, _ = ks.asm(" ; ".join(instrucciones))
    code = bytes(encoding)

    # Crear una instancia del emulador Unicorn para arquitectura x86 de 32 bits
    mu = Uc(UC_ARCH_X86, UC_MODE_32)

    # Dirección base para emulación
    ADDRESS = 0x1000000
    STACK = 0x2000000
    STACK_SIZE = 1024 * 1024  # 1 MB

    # Asignar memoria para código y stack
    mu.mem_map(ADDRESS, 2 * 1024 * 1024)
    mu.mem_write(ADDRESS, code)

    # Asignar stack
    mu.mem_map(STACK, STACK_SIZE)
    mu.reg_write(UC_X86_REG_ESP, STACK + STACK_SIZE // 2)

    # Inicializar registros que se usarán
    mu.reg_write(UC_X86_REG_EDX, 0)  # evitar basura al dividir

    # Ejecutar el código
    mu.emu_start(ADDRESS, ADDRESS + len(code))

    # Leer el resultado del registro EAX
    resultado = mu.reg_read(UC_X86_REG_EAX)
    return resultado
