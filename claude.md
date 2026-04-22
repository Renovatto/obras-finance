# 📑 Registro de Memória Técnica: Claude Sonnet

Este documento preserva o histórico de desenvolvimento, as decisões arquiteturais fundamentais e a evolução do projeto **ObrasFinance**. Foi criado para garantir que futuras versões de IA compreendam o "porquê" por trás das escolhas técnicas.

---

## 🏗️ Evolução Arquitetural

O projeto nasceu da necessidade de modernizar um sistema financeiro de construção civil, migrando de uma estrutura baseada em templates Jinja2 para uma **Arquitetura Desacoplada** de alta performance.

### Marcos de Desenvolvimento:
1.  **Fundação Backend:** Escalado de scripts simples para uma estrutura robusta em FastAPI com SQLAlchemy 2.0 (Assíncrono).
2.  **Transição Frontend:** Implementação do Sveltekit com Svelte 5, utilizando **Runes** (`$state`, `$effect`, `$derived`) para reatividade granular.
3.  **Mobilidade e Desktop:** Preparação do sistema para ser portátil (Single Executable) via PyInstaller, com suporte a bancos de dados dinâmicos.
4.  **UX Premium:** Implementação de um design minimalista e moderno, focado em alta usabilidade e micro-interações (Tooltips, Modais, Transições).

---

## 🧠 Decisões de Design (Rationale)

### 1. SQLite com Camada de Sincronização
**Decisão:** Utilizar SQLite com caminhos configuráveis via UI.
**Motivo:** O sistema precisava ser portátil para rodar em máquinas de clientes sem necessidade de infraestrutura complexa (Docker/Postgres). A sincronização entre DB e `config.json` resolve o problema de inicialização do sistema.

### 2. Svelte 5 Runes
**Decisão:** Uso obrigatório de Runes no frontend.
**Motivo:** Performance e clareza de código. O estado reativo global (`ui.svelte.ts`) e local permite um controle fino sobre modais e gatilhos de atualização sem o overhead de stores legadas.

### 3. Tipos de Dados Customizados (SQLAlchemy)
**Decisão:** Criação de `UUIDType` e `DecimalType` no backend.
**Motivo:** O SQLite não suporta nativamente UUID ou Precisão Decimal. Esses decorators garantem que o Python sempre lide com `uuid.UUID` e `decimal.Decimal`, evitando erros financeiros de arredondamento.

---

## 🛠️ Desafios Superados (Legacy context)
- **Problema de Bootstrap:** O sistema não sabia onde estava o banco sem ler o banco.
    - **Solução:** Implementação de um "Bootstrap Sync" que espelha o caminho do banco da tabela `ConfiguracaoSistema` para um arquivo `config.json` local.
- **Tour de Boas-Vindas Dinâmico:** Posicionamento de tooltips em elementos de layout fixos e móveis.
    - **Solução:** Overlay SVG com cálculo de `BoundingClientRect` e reatividade de redimensionamento de janela.

---
*Este registro encerra o contexto da sessão de implementação do Onboarding e Migração de Configurações.*
