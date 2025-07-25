#!/bin/bash

# Navegar até a pasta do projeto
cd /usr/projeto || {
  echo "❌ Diretório /meuprojeto/ não encontrado."
  exit 1
}

# Instalar dependências
#echo "📥 Instalando express e pg..."
#npm install express pg

# Iniciar com PM2
echo "🚀 Iniciando server.js com PM2..."
#pm2 delete projeto
pm2 start server.js --name "projeto"

# Salvar o estado do PM2 para restaurar no boot
pm2 save
