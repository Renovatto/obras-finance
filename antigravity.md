# 🛸 Antigravity: Bíblia de Referência do Sistema

Este é o documento mestre de contexto para o **ObrasFinance**. Ele deve ser lido integralmente por qualquer IA antes de realizar modificações estruturais no código.

---

## 📐 1. Stack Tecnológica
- **Backend:** FastAPI (Python 3.12+), SQLAlchemy 2.0 (Async), Pydantic v2.
- **Banco de Dados:** SQLite (via `aiosqlite`) com PRAGMA `foreign_keys=ON`.
- **Frontend:** SvelteKit (Svelte 5), TypeScript, Vite.
- **Estilo:** Tailwind CSS 3.4+, PostCSS.
- **Gráficos:** Chart.js 4.5.
- **Ícones:** Lucide-Svelte.

---

## 📂 2. Estrutura de Pastas e Responsabilidades

### Backend (`/backend/app`)
- `/models`: Definição de modelos ORM e tipos customizados (UUID, Decimal).
- `/routers`: Endpoints da API agrupados por domínio (Obras, Lançamentos, Dashboard).
- `/services`: Toda a lógica de negócio (cálculos financeiros, consultas complexas).
- `/schemas`: Modelos Pydantic para validação de entrada e saída.
- `/core`: Configurações de sistema, base de dados e segurança.

### Frontend (`/src`)
- `/routes`: Páginas e layouts do SvelteKit.
- `/lib/components`: Componentes reutilizáveis de UI (Modais, Inputs, Selects).
- `/lib/stores`: Estados globais utilizando Runes do Svelte 5.
- `/lib/api.ts`: Cliente HTTP centralizado.

---

## ⛓️ 3. Regras de Negócio e Banco de Dados

### Entidades Principais:
1.  **Obra:** Projeto central. Se deletada, apaga os lançamentos vinculados (Cascade).
2.  **LançamentoFinanceiro:** Receitas e Despesas. Vinculado a uma Categoria, Forma de Pagamento e Responsável.
3.  **Auxiliares (Categoria, FormaPagto, Responsavel):** Tabelas de apoio. Possuem restrição de deletar (`RESTRICT`) se houver lançamentos vinculados.
4.  **ConfiguracaoSistema:** Tabela Singleton (ID=1) que guarda o caminho do banco e flag de onboarding.

### Regras Financeiras:
- **Precisão:** Valores monetários são salvos como `TEXT` no SQLite (via `DecimalType`) para garantir 100% de precisão decimal.
- **Uppercase:** Todos os nomes de categorias, obras e responsáveis são convertidos para **CAIXA ALTA** via Pydantic validators.

---

## 🔌 4. Fluxo de Inicialização (Bootstrap)
O arquivo `backend/app/routers/config.py` gerencia o ponto crítico do sistema:
1. Ao salvar configurações no Frontend, o sistema envia para a API.
2. O Backend salva na tabela `configuracao_sistema`.
3. O Backend **sincroniza** imediatamente esses dados para o arquivo `~/Documents/ObrasFinance/config.json`.
4. No próximo boot, `backend/app/core/config.py` lê esse JSON para montar a URL do banco de dados.

---

## 🎨 5. Guias de Estilo UI/UX
- **Design:** Moderno, minimalista, com bordas arredondadas generosas (`rounded-2xl` e `rounded-[2rem]`).
- **Sombras:** Uso consistente de `shadow-xl shadow-gray-200/50`.
- **Animações:** Transições suaves do Svelte (`fade`, `slide`, `scale`).
- **Interatividade:** Feedback visual em hover e botões com `active:scale-[0.98]`.

---

## 🛠️ 6. Próximas Implementações (Roadmap)
- [ ] **Módulo de Relatórios:** Implementar geração de PDF e exportação para Excel.
- [ ] **Filtros Avançados:** Filtros dinâmicos por data personalizada em todos os módulos.
- [ ] **Anexos:** Upload de documentos e fotos de comprovantes para lançamentos.
- [ ] **Backup Automático:** Rotina para exportar o banco de dados em horários agendados.

---
**AVISO PARA IA:** Este sistema utiliza Svelte 5. NÃO use sintaxe legada de stores (ex: `$store`). Sempre use Runes (`$state`, `$derived`, etc).
