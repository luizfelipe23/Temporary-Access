# Temporary Access

Sistema self-hosted para geração e validação de credenciais temporárias.

A aplicação permitirá autenticar usuários, gerar chaves com tempo de expiração, transformar essas chaves em QR Codes e validar credenciais, mantendo um histórico básico das validações.

## Funcionalidades

- Autenticação de usuários
- Geração de chaves temporárias
- Expiração e revogação de credenciais
- Geração de QR Codes
- Validação de chaves
- Registro de validações
- Execução totalmente via Docker

## Stack

- Python + FastAPI
- React + TypeScript
- SQLite
- Docker + Docker Compose

## Executar

```bash
docker compose up --build
