-- seed.sql — dados de demonstração (fictícios, sem dados pessoais reais)

insert into plans (code, name, max_companies, price_cents) values
  ('starter', 'Starter', 10, 9900),
  ('profissional', 'Profissional', 50, 24900),
  ('escritorio', 'Escritório', 200, 59900),
  ('enterprise', 'Enterprise', null, null)
on conflict (code) do nothing;

-- Regras determinísticas iniciais para PE (Dia 4). O "check" em `condicao` é
-- despachado por app/rules/checks.py — ver docs/RULES.md.

insert into rules (codigo, nome, descricao, uf, tipo_processo, condicao, severidade, mensagem, acao_sugerida, fonte, versao, ativo)
values
(
  'PE-CNAE-001',
  'Empresa sem CNAE cadastrado',
  'Toda empresa precisa de ao menos um CNAE antes de qualquer processo.',
  'PE',
  null,
  '{"check": "company_has_activity"}'::jsonb,
  'erro',
  'A empresa não possui nenhum CNAE cadastrado.',
  'Cadastre pelo menos um CNAE (principal) antes de prosseguir com o processo.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
),
(
  'PE-END-001',
  'Empresa sem endereço cadastrado',
  'Toda empresa precisa de ao menos um endereço antes de qualquer processo.',
  'PE',
  null,
  '{"check": "company_has_address"}'::jsonb,
  'erro',
  'A empresa não possui nenhum endereço cadastrado.',
  'Cadastre o endereço da sede antes de prosseguir com o processo.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
),
(
  'PE-QSA-001',
  'Alteração de QSA sem sócios cadastrados',
  'Alerta quando não há nenhum sócio cadastrado para uma alteração de QSA.',
  'PE',
  'alteracao_qsa',
  '{"check": "company_has_partners"}'::jsonb,
  'atencao',
  'Nenhum sócio cadastrado para esta alteração de QSA.',
  'Cadastre os sócios atuais e os pretendidos antes de continuar.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
),
(
  'PE-QSA-002',
  'Soma de percentuais de capital divergente',
  'A soma dos percentuais de capital dos sócios deve totalizar 100%.',
  'PE',
  'alteracao_qsa',
  '{"check": "partners_percentual_sum", "tolerance": 0.01}'::jsonb,
  'erro',
  'A soma dos percentuais de capital dos sócios não totaliza 100%.',
  'Ajuste os percentuais de capital dos sócios até somarem exatamente 100%.',
  'Regra interna — não configurada como exigência oficial confirmada.',
  1,
  true
)
on conflict (codigo) do nothing;
