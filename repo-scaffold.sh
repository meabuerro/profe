#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

GREEN='\033[0;32m'
BLUE='\033[1m'
NC='\033[0m'

print_header() {
  echo -e "\n${BLUE}==> $1${NC}\n"
}

task "=== Acudiendo al repositorio de programación didáctica ==="

print_header "Configuración inicial"
say "Creando directorio de trabajo..."
mkdir -p workdir
cd workdir
pwd

say "Scheme y país:"
select_country
add_ccc self

task "Fase 1: Estructura y autoridad"
say "Evaluando marco legal y competencias..."
verify_autonomy_budget

print_header "Configuración del proyecto (fase 1)"
task "Creando directorio de proyecto..."
mkdir -p proyecto
cd proyecto
pwd

print_header "Configuración de accesos"
task "Enumerando recursos..."
list_resources
