# Ejemplos de cURL para Login

## Problema Original
Los comandos curl que estabas usando tenían problemas de formato en Windows. Aquí están las versiones corregidas:

## ❌ Comando Incorrecto (el que no funcionaba)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ -H Content-Type: application/json -d {"username":"admin","password":"admin"}
```

**Problemas:**
1. Falta comillas en el header `-H "Content-Type: application/json"`
2. Usa `username` en lugar de `login`
3. Las comillas del JSON no están escapadas correctamente

## ✅ Comandos Correctos

### Opción 1: Con archivo JSON (Recomendado)
```bash
# Crear archivo login_data.json con:
# {"login": "admin", "password": "admin"}

curl -X POST http://127.0.0.1:8000/api/auth/login/ -H "Content-Type: application/json" -d @login_data.json
```

### Opción 2: Con datos inline (Windows CMD)
```cmd
curl -X POST http://127.0.0.1:8000/api/auth/login/ -H "Content-Type: application/json" -d "{\"login\":\"admin\",\"password\":\"admin\"}"
```

### Opción 3: Con PowerShell
```powershell
$body = @{
    login = "admin"
    password = "admin"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login/" -Method POST -ContentType "application/json" -Body $body
```

### Opción 4: Login con Email
```bash
# Con username
curl -X POST http://127.0.0.1:8000/api/auth/login/ -H "Content-Type: application/json" -d "{\"login\":\"admin\",\"password\":\"admin\"}"

# Con email
curl -X POST http://127.0.0.1:8000/api/auth/login/ -H "Content-Type: application/json" -d "{\"login\":\"admin@gmail.com\",\"password\":\"admin\"}"
```

## Respuesta Esperada
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Usar el Token de Acceso
```bash
# Ejemplo de uso del token en requests posteriores
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://127.0.0.1:8000/api/v1/users/
```

## Notas Importantes
1. **Campo de login**: Usa `login` (no `username`) - acepta tanto username como email
2. **Content-Type**: Siempre incluir `"Content-Type: application/json"`
3. **Escape de comillas**: En Windows CMD, usar `\"` para escapar comillas en JSON
4. **Tokens**: Guarda el `access` token para requests autenticados
5. **Refresh**: Usa el `refresh` token para obtener nuevos access tokens