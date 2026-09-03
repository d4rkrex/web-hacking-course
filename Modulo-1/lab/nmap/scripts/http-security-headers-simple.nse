local http = require "http"
local shortport = require "shortport"

description = [[
Hace una request HTTP/HTTPS simple y revisa si existen cabeceras de seguridad basicas.
Pensado como ejemplo didactico para alumnos que recien empiezan con NSE.
]]

author = "GitHub Copilot"
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
categories = { "discovery", "safe" }

portrule = shortport.http

local headers_to_check = {
  {
    name = "X-Frame-Options",
    reason = "reduce riesgo de clickjacking"
  },
  {
    name = "X-Content-Type-Options",
    reason = "evita MIME sniffing basico"
  },
  {
    name = "Content-Security-Policy",
    reason = "limita carga y ejecucion de contenido"
  },
  {
    name = "Strict-Transport-Security",
    reason = "fuerza uso de HTTPS en navegadores"
  }
}

local fingerprint_headers = {
  {
    name = "Server",
    reason = "puede revelar servidor web o proxy"
  },
  {
    name = "X-Powered-By",
    reason = "puede revelar tecnologia o framework"
  }
}

local function normalize_headers(headers)
  local normalized = {}

  for name, value in pairs(headers or {}) do
    normalized[string.lower(name)] = value
  end

  return normalized
end

action = function(host, port)
  local response = http.get(host, port, "/")

  if not response then
    return "No se pudo obtener una respuesta HTTP/HTTPS."
  end

  local headers = normalize_headers(response.header)
  local lines = {}

  lines[#lines + 1] = string.format("Ruta consultada: %s", response.location or "/")

  if response.status then
    lines[#lines + 1] = string.format("Status: %s", response.status)
  end

  lines[#lines + 1] = ""
  lines[#lines + 1] = "Cabeceras de seguridad:"

  for _, header in ipairs(headers_to_check) do
    local value = headers[string.lower(header.name)]

    if value then
      lines[#lines + 1] = string.format("[OK] %s: %s", header.name, value)
    else
      lines[#lines + 1] = string.format("[MISSING] %s (%s)", header.name, header.reason)
    end
  end

  lines[#lines + 1] = ""
  lines[#lines + 1] = "Cabeceras utiles para fingerprinting:"

  for _, header in ipairs(fingerprint_headers) do
    local value = headers[string.lower(header.name)]

    if value then
      lines[#lines + 1] = string.format("[INFO] %s: %s", header.name, value)
    else
      lines[#lines + 1] = string.format("[NOT EXPOSED] %s (%s)", header.name, header.reason)
    end
  end

  return table.concat(lines, "\n")
end