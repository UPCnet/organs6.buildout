#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba standalone para validar la lógica de seguridad del portrait upload.
No requiere el entorno Plone completo.
"""


def validate_image_file_content_standalone(file_data):
    """
    Versión standalone de la función de validación.
    Copia de la lógica implementada en validations.py
    """
    # Leer los primeros bytes para verificación
    if hasattr(file_data, 'read'):
        # Es un objeto file-like
        current_pos = file_data.tell()
        file_data.seek(0)
        header = file_data.read(32)
        file_data.seek(current_pos)
    else:
        # Es bytes directamente
        header = file_data[:32] if len(file_data) >= 32 else file_data
    
    # Verificar magic bytes manualmente para mayor seguridad
    if len(header) < 4:
        raise ValueError("Archivo demasiado pequeño")
    
    # JPEG: FF D8 FF
    if header[:3] == b'\xff\xd8\xff':
        return 'jpeg'
    
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if header[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
        return 'png'
    
    # WebP: RIFF ... WEBP
    if len(header) >= 12 and header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return 'webp'
    
    # Si no coincide con ningún tipo permitido
    raise ValueError("Tipo de archivo no reconocido como imagen válida")


def create_test_files():
    """Crea archivos de prueba con diferentes magic bytes"""
    
    # JPEG válido (magic bytes)
    jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00' + b'\x00' * 100
    
    # PNG válido (magic bytes)
    png_data = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0dIHDR\x00\x00\x00\x01' + b'\x00' * 100
    
    # WebP válido (magic bytes)
    webp_data = b'RIFF' + b'\x00\x00\x00\x00' + b'WEBP' + b'VP8 ' + b'\x00' * 100
    
    # PHP file (debería fallar)
    php_data = b'<?php system($_GET["cmd"]); ?>'
    
    # Shell script (debería fallar)
    shell_data = b'#!/bin/bash\nrm -rf /'
    
    # Texto plano (debería fallar)
    text_data = b'This is just text'
    
    # GIF (debería fallar - no está en whitelist)
    gif_data = b'GIF89a' + b'\x00' * 100
    
    return {
        'jpeg': jpeg_data,
        'png': png_data,
        'webp': webp_data,
        'php': php_data,
        'shell': shell_data,
        'text': text_data,
        'gif': gif_data
    }


def test_validation():
    """Ejecuta las pruebas de validación"""
    
    test_files = create_test_files()
    results = []
    
    print("=" * 70)
    print("PRUEBAS DE VALIDACIÓN DE SEGURIDAD PARA PORTRAIT UPLOAD")
    print("=" * 70)
    print()
    
    # Tipos que DEBEN pasar la validación
    valid_types = ['jpeg', 'png', 'webp']
    
    # Tipos que DEBEN fallar la validación
    invalid_types = ['php', 'shell', 'text', 'gif']
    
    # Probar tipos válidos
    print("1. PROBANDO TIPOS DE IMAGEN VÁLIDOS:")
    print("-" * 70)
    
    for file_type in valid_types:
        data = test_files[file_type]
        try:
            result = validate_image_file_content_standalone(data)
            status = "✓ PASS" if result else "✗ FAIL"
            results.append((file_type, True, status))
            print(f"  {status} - {file_type.upper()}: Detectado como '{result}'")
        except Exception as e:
            results.append((file_type, False, "✗ FAIL"))
            print(f"  ✗ FAIL - {file_type.upper()}: {str(e)} (NO DEBERÍA FALLAR)")
    
    print()
    print("2. PROBANDO TIPOS DE ARCHIVO INVÁLIDOS/MALICIOSOS:")
    print("-" * 70)
    
    # Probar tipos inválidos
    for file_type in invalid_types:
        data = test_files[file_type]
        try:
            result = validate_image_file_content_standalone(data)
            results.append((file_type, False, "✗ FAIL"))
            print(f"  ✗ FAIL - {file_type.upper()}: Aceptado como '{result}' (DEBERÍA RECHAZARSE)")
        except Exception as e:
            results.append((file_type, True, "✓ PASS"))
            print(f"  ✓ PASS - {file_type.upper()}: Rechazado correctamente - {str(e)}")
    
    print()
    print("=" * 70)
    print("RESUMEN DE RESULTADOS:")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\nTotal de pruebas: {total}")
    print(f"Pruebas exitosas: {passed}")
    print(f"Pruebas fallidas: {total - passed}")
    
    if passed == total:
        print("\n✓ TODAS LAS PRUEBAS PASARON - Sistema de validación funcionando correctamente")
        return 0
    else:
        print("\n✗ ALGUNAS PRUEBAS FALLARON - Revisar implementación")
        return 1


def test_php_upload_scenario():
    """
    Simula el escenario específico del bug reportado:
    Un usuario intenta subir shell.php
    """
    print("\n" + "=" * 70)
    print("3. SIMULANDO ESCENARIO REAL: Intento de subir shell.php")
    print("=" * 70)
    print()
    
    # Contenido típico de un webshell
    malicious_php = b'<?php\nif(isset($_GET["cmd"])) {\n    system($_GET["cmd"]);\n}\n?>'
    
    print("Archivo: shell.php")
    print(f"Contenido (primeros 50 bytes): {malicious_php[:50]}")
    print()
    
    try:
        result = validate_image_file_content_standalone(malicious_php)
        print("✗ FALLO CRÍTICO: El archivo malicioso fue ACEPTADO")
        print("  ⚠ VULNERABILIDAD DE SEGURIDAD DETECTADA")
        return 1
    except Exception as e:
        print(f"✓ ÉXITO: El archivo malicioso fue RECHAZADO")
        print(f"  Mensaje de error: {str(e)}")
        print("  ✓ Sistema de seguridad funcionando correctamente")
        return 0


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print(" SCRIPT DE PRUEBA - VALIDACIÓN DE SEGURIDAD PORTRAIT UPLOAD")
    print("=" * 70)
    print("\nEste script verifica que:")
    print("  1. Solo se aceptan imágenes JPG, PNG y WEBP")
    print("  2. La validación se hace por contenido real (magic bytes)")
    print("  3. Se rechazan archivos maliciosos (PHP, shell scripts, etc.)")
    print()
    
    try:
        result1 = test_validation()
        result2 = test_php_upload_scenario()
        
        print("\n" + "=" * 70)
        print("CONCLUSIÓN FINAL")
        print("=" * 70)
        
        if result1 == 0 and result2 == 0:
            print("\n✓ TODAS LAS VALIDACIONES PASARON")
            print("  El sistema está protegido contra subida de archivos maliciosos.")
            exit(0)
        else:
            print("\n✗ ALGUNAS VALIDACIONES FALLARON")
            print("  Revisar la implementación antes de desplegar.")
            exit(1)
    
    except Exception as e:
        print(f"\n✗ ERROR FATAL: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

