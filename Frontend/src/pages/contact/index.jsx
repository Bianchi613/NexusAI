import InfoPage from '../../components/info-page/index.jsx'

const sections = [
  {
    title: 'Responsavel pelo projeto',
    paragraphs: [
      'Esta pagina representa o contato direto com voce, responsavel pelo Nexus IA, para centralizar o ponto institucional do portal dentro da propria interface.',
      'Ela pode ser ajustada depois com email real, formulario, rede social profissional ou qualquer outro canal oficial que voce queira expor publicamente.',
    ],
  },
  {
    title: 'Assuntos de contato',
    paragraphs: [
      'O espaco pode ser usado para tratar duvidas sobre o produto, feedback de interface, ajustes no fluxo editorial, integracoes com o backend e validacao das materias publicadas.',
      'Tambem faz sentido concentrar aqui pedidos relacionados a parceria, imprensa, revisao de conteudo e manutencao operacional do portal.',
    ],
  },
  {
    title: 'Proximo passo',
    paragraphs: [
      'Quando voce quiser, esta pagina pode ganhar canais reais de atendimento, como email institucional, WhatsApp comercial, formulario de mensagem ou links externos para perfil profissional.',
    ],
  },
]

export default function ContactPage({ onChangePage }) {
  return (
    <InfoPage
      kicker="Canal institucional"
      title="Contato"
      intro="Esta pagina foi criada como ponto oficial de contato do Nexus IA e pode ser refinada depois com os seus canais reais."
      sections={sections}
      onChangePage={onChangePage}
    />
  )
}
