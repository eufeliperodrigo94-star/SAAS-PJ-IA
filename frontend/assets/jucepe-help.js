// Guia de referência "Como protocolar na JUCEPE", resumido a partir dos
// manuais oficiais "Passo a Passo" do portal da Junta Comercial de
// Pernambuco. Conteúdo estático (não depende de IA nem de dados da
// empresa) — apenas orientação de uso do portal externo da JUCEPE, o
// sistema não protocola nada automaticamente.

const JUCEPE_GENERIC_STEPS = [
  "Fazer login no Integrador Estadual.",
  "Solicitar o DBE (Documento Básico de Entrada) no site da Receita Federal, no convênio com a Junta Comercial de Pernambuco.",
  "Preencher o Requerimento Eletrônico correspondente ao ato, informando o número do DBE.",
  "Assinar digitalmente todos os documentos (certificado A1/A3 ou conta gov.br nível Prata/Ouro) e realizar o pagamento do DAE.",
];

const JUCEPE_HELP_BY_TYPE = {
  abertura: {
    titulo: "Constituição de empresa",
    passos: [
      "Solicitar Viabilidade no Integrador Estadual, escolhendo a Junta Comercial de Pernambuco.",
      "Solicitar o DBE (Documento Básico de Entrada) na Receita Federal, no convênio com a JUCEPE.",
      "Preencher o Requerimento Eletrônico (Inscrição de Matriz) com o número do DBE.",
      "Assinar digitalmente e realizar o pagamento do DAE.",
      "Após o deferimento, preencher o Módulo de Administração Tributária (MAT) na Receita Federal em até 90 dias corridos para obter o CNPJ — perder o prazo exige refazer Viabilidade e DBE.",
    ],
    fonte: "JUCEPE — Passo a Passo \"Constituição\" e \"Módulo MAT — Processo Expirado\".",
  },
  alteracao_qsa: {
    titulo: "Alteração de sócios (QSA)",
    passos: [
      "Elaborar o ato de deliberação: Ata de reunião/assembleia de sócios (sociedades com mais de um sócio) ou ato de decisão singular (sociedade limitada unipessoal).",
      ...JUCEPE_GENERIC_STEPS,
    ],
    fonte: "JUCEPE — Passo a Passo \"Registro de Deliberação\"; formalidades conforme IN DREI nº 81, Anexo IV (Manual de Registro de Sociedade Limitada).",
  },
  alteracao_administrador: {
    titulo: "Alteração de administrador",
    passos: [
      "Elaborar o ato de deliberação: Ata de reunião/assembleia de sócios ou ato de decisão singular (unipessoal), nomeando o novo administrador.",
      ...JUCEPE_GENERIC_STEPS,
    ],
    fonte: "JUCEPE — Passo a Passo \"Registro de Deliberação\"; formalidades conforme IN DREI nº 81, Anexo IV.",
  },
  alteracao_endereco: {
    titulo: "Alteração de endereço (dentro de PE)",
    passos: JUCEPE_GENERIC_STEPS,
    fonte: "DREI — Manual de Registro de Sociedade Limitada (IN DREI nº 81/2020, Anexo IV): a alteração contratual deve informar o novo endereço completo.",
  },
  alteracao_cnae: {
    titulo: "Alteração de CNAE/atividade",
    passos: [
      ...JUCEPE_GENERIC_STEPS,
      "Só é possível marcar uma atividade como principal — as demais devem ser secundárias (sem limite de quantidade).",
    ],
    fonte: "JUCEPE — Passo a Passo \"Constituição\" (mesma regra vale para alteração de CNAE).",
  },
  alteracao_capital: {
    titulo: "Alteração de capital social",
    passos: [
      "Elaborar o ato alterador informando o novo capital social e a forma de integralização.",
      ...JUCEPE_GENERIC_STEPS,
    ],
    fonte: "JUCEPE — Passo a Passo \"Registro de Deliberação\" e \"Constituição\".",
  },
  alteracao_nome_objeto: {
    titulo: "Alteração de nome empresarial/objeto social",
    passos: [
      "Verificar se a nova razão social segue as regras de composição da IN DREI nº 81.",
      ...JUCEPE_GENERIC_STEPS,
    ],
    fonte: "JUCEPE — Passo a Passo \"Constituição\": composição do nome empresarial conforme IN DREI nº 81.",
  },
  alteracao_porte: {
    titulo: "Alteração de porte (enquadramento/desenquadramento ME-EPP)",
    passos: [
      "Solicitar o DBE marcando o evento 222 — Enquadramento/Reenquadramento/Desenquadramento ME/EPP.",
      "Preencher o Requerimento Eletrônico, marcando \"Alteração de Porte Empresarial\" e a opção correspondente à situação da empresa.",
      "Se o porte já foi alterado na Receita: marcar \"Sim\" e não informar o DBE. Se não foi alterado: informar os 24 dígitos do DBE.",
      "Assinar digitalmente e realizar o pagamento do DAE.",
    ],
    fonte: "JUCEPE — Passo a Passo \"Alteração de Porte\".",
  },
  transferencia_uf: {
    titulo: "Transferência de sede de PE para outra UF",
    passos: [
      "Solicitar a Viabilidade de mudança de endereço na Junta Comercial do estado de destino (obrigatório antes de continuar).",
      "Gerar o DBE na Receita Federal informando a transferência de sede de PE para a outra UF.",
      "Arquivar o ato de alteração contratual na JUCEPE, mencionando a mudança de UF, e assinar digitalmente.",
      "Com o ato já chancelado pela JUCEPE, protocolar o arquivamento na Junta Comercial do estado de destino para concluir a transferência.",
    ],
    fonte: "JUCEPE — Passo a Passo \"Transferência de PE para Outra UF\".",
  },
};

const JUCEPE_ALWAYS_NOTES = [
  {
    titulo: "Assinatura digital",
    texto:
      "Todos os sócios/administradores (ou procuradores) devem assinar com certificado digital A1/A3 e-CPF, ou com a conta gov.br em nível Prata ou Ouro (com verificação em duas etapas habilitada). O processo só é enviado à JUCEPE após todos os itens estarem assinados.",
  },
  {
    titulo: "Complemento de taxa",
    texto:
      "Use \"Complemento de Pagamento\" no Integrador Estadual se o boleto (DAE) foi pago após o vencimento, com valor menor que o devido, ou se o processo foi assinado mas o boleto não chegou a ser emitido.",
  },
];

function renderJucepeHelp(processType) {
  const container = document.getElementById("jucepe-help-content");
  if (!container) return;

  const info = JUCEPE_HELP_BY_TYPE[processType];
  const stepsHtml = info
    ? `
      <p style="font-weight: 600; margin: 0 0 8px">${info.titulo}</p>
      <ol style="margin: 0 0 8px; padding-left: 20px">
        ${info.passos.map((p) => `<li style="margin-bottom: 4px">${p}</li>`).join("")}
      </ol>
      <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0 0 16px">Fonte: ${info.fonte}</p>`
    : "";

  const notesHtml = JUCEPE_ALWAYS_NOTES.map(
    (n) => `
    <p style="font-weight: 600; margin: 12px 0 4px">${n.titulo}</p>
    <p style="margin: 0; color: var(--text-muted)">${n.texto}</p>`
  ).join("");

  container.innerHTML = `${stepsHtml}${notesHtml}`;
}
