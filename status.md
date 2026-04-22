# Estado do Projeto: ObrasFinance

## Visão Geral
O **ObrasFinance** é um sistema de gestão financeira especializado para projetos de construção civil. Ele oferece controle granular de receitas e despesas por obra, categorias inteligentes e dashboards analíticos de alta performance.

## Estado Atual do Desenvolvimento
O projeto encontra-se em um estado **Estável e Funcional**, pronto para uso básico ou demonstração.

### ✅ Totalmente Funcional
- **Core Financeiro**: CRUD completo de lançamentos (receitas/despesas) com paginação e filtros.
- **Gestão de Obras**: Cadastro e acompanhamento individual de projetos.
- **Dashboard Analítico**: KPIs em tempo real, gráfico mensal de P&L e distribuição por categorias (Doughnut).
- **Onboarding Interativo**: Sistema de tour dinâmico com tooltips para o primeiro acesso.
- **Arquitetura Portátil**: Configuração de banco de dados SQLite dinâmica com modo portátil via PyInstaller.
- **Design System**: Interface premium com Svelte 5 Runes e Tailwind CSS.

### ⚠️ Parcialmente Implementado
- **Relatórios**: O módulo existe na interface e API, mas a inteligência de geração de PDF/Excel ainda é básica (apenas visual).
- **Filtros Avançados**: Filtros de data arbitrária (range) precisam de implementação no backend.

### ❌ Não Iniciado / Futuro
- **Módulo de Anexos**: Upload de notas fiscais/fotos.
- **Autenticação Multi-usuário**: Projetado para ser single-user/local por enquanto.
- **Backup Automático**: Rotina de exportação do `.db`.

## Decisões Arquiteturais Chave
- **FastAPI + SQLAlchemy Async**: Escolhido pela alta performance e suporte total a operações assíncronas no SQLite.
- **Svelte 5 (Runes)**: Uso de `$state` e `$derived` para garantir uma interface que não perde reatividade mesmo em estados globais complexos.
- **Hibridismo JSON/DB para Config**: O uso de `config.json` para bootstrap resolve o problema de localizar o banco de dados antes da conexão inicial.
- **Precisão Decimal**: Todos os valores monetários são tratados como `TEXT` no Banco de Dados via decorador customizado para evitar erros de ponto flutuante.

## Débito Técnico Conhecido
- **Consolidação de Modelos**: Atualmente todos os modelos ORM estão em `models/__init__.py`. Se a regra de negócio crescer, devem ser movidos para módulos individuais.
- **Testes**: Ausência de cobertura de testes unitários automatizados (recomenda-se Pytest e Playwright).
- **Tratamento de Erros no Frontend**: Erros de rede são exibidos de forma genérica; precisam de mensagens mais amigáveis ao usuário final.

## Próximos Passos (Backlog Priorizado)
1.  **Geração de Relatórios**: Implementar exportação de PDF e CSV no serviço de relatórios.
2.  **Anexos de Documentos**: Adicionar suporte a `files` nos lançamentos financeiros.
3.  **Refatoração de Filtros**: Unificar a lógica de filtros de data entre Dashboard e Lançamentos.
